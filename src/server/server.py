import atexit
import csv
import io
import json
import logging
import os
import shutil
import uuid

from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, session

from petllang.execution.execute import execute_petl_script_direct

logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

app = Flask(__name__)

app.secret_key = os.urandom(32)
app.config["SESSION_PERMANENT"] = False

USER_ID_KEY = "userId"
INTERPRETER_HISTORY_KEY = "history"

CSV_DIRECTORY = Path(f"{os.getcwd()}/csvs")
MAX_CSV_SIZE = 20000  # Maximum number of cells in CSV (rows * columns)

FILE_COUNT_KEY = "file_count"
MAX_FILE_COUNT = 5


users: Dict[str, datetime] = {}


def add_new_user(user_id: str):
    users[user_id] = datetime.now()


def update_user_activity(user_id: str):
    if user_id in users:
        users[user_id] = datetime.now()


def valid_user() -> bool:
    user_id = session.get(USER_ID_KEY)
    if not user_id:
        logger.warning("No user ID found in session")
        return False
    logger.info(f"User ID: {user_id}")
    update_user_activity(user_id)
    return True


@app.route('/')
def start_session():
    if USER_ID_KEY not in session:
        user_id = uuid.uuid4()
        session[USER_ID_KEY] = user_id
        session[FILE_COUNT_KEY] = 0
        session[INTERPRETER_HISTORY_KEY] = []

        add_new_user(str(user_id))
        logger.info(f"New session started with ID: {user_id}")
        return "Session started"
    else:
        print(session)
        return "Session already exists"


@app.route('/interpret', methods=['POST'])
def interpret():
    if not valid_user():
        return "Unauthorized", 401

    petl_input: str = request.get_json()["input"]

    logger.info("New interpreter request")
    logger.debug(f"\nInterpreter Input\n{petl_input}\n")

    temp = session[INTERPRETER_HISTORY_KEY]
    temp.append(petl_input)
    session[INTERPRETER_HISTORY_KEY] = temp

    try:
        stdout_buffer = io.StringIO()
        with redirect_stdout(stdout_buffer):
            result: Optional[str] = execute_petl_script_direct(petl_input)

        return_string = stdout_buffer.getvalue() if result else "Invalid program"
        logger.debug(f"Interpreter Output:\n{return_string}\n")
        return return_string
    except Exception as interpret_exception:
        error_message = f"Error during interpretation: {interpret_exception}"
        logger.error(error_message)
        return error_message


@app.route('/history', methods=['GET'])
def history():
    if not valid_user():
        return "Unauthorized", 401

    session_history = session.get(INTERPRETER_HISTORY_KEY, [])
    logger.info(f"Fetching interpreter history: {session_history}")
    return json.dumps(session_history)


def validate_csv_writable(csv_name: str,
                          csv_content: str,
                          user_csv_directory: Path,
                          csv_path: Path) -> Optional[str]:
    if not csv_name or not csv_content:
        logger.warning("CSV name or content not provided")
        return "CSV name and content must be provided."
    elif len(csv_content[0]) * len(csv_content) > MAX_CSV_SIZE:
        logger.warning("CSV exceeded maximum size")
        return "CSV content exceeds maximum allowed size."
    elif "," in csv_name or "/" in csv_name or "\\" in csv_name:
        error_message = "CSV name contains invalid characters."
        logger.warning(error_message)
        return error_message

    if not user_csv_directory.exists():
        user_csv_directory.mkdir(parents=True, exist_ok=True)

    if csv_path.exists():
        logger.warning("Removing existing CSV")
        os.remove(csv_path)

    if session.get(FILE_COUNT_KEY, 0) >= MAX_FILE_COUNT:
        return "Too many CSV files exist. Please delete some before creating new ones."

    return None


def create_csv_helper(csv_name: str, csv_path: Path, csv_content: str) -> Optional[str]:
    logger.info(f"Creating new CSV: {csv_name}.csv")

    try:
        with open(csv_path, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(csv_content)

        if FILE_COUNT_KEY in session:
            session[FILE_COUNT_KEY] += 1
        else:
            session[FILE_COUNT_KEY] = 1

        logger.info(f"CSV {csv_name}.csv created successfully.")
        return None
    except Exception as csv_write_exception:
        error_message = f"Error writing CSV: {csv_write_exception}"
        logger.error(error_message)
        return error_message


@app.route('/create_csv', methods=['POST'])
def create_csv():
    if not valid_user():
        return "Unauthorized", 401

    request_json = request.get_json()
    csv_name: str = request_json["name"]
    csv_content: str = request_json["content"]

    user_csv_directory = Path(f"{CSV_DIRECTORY}/{session.get(USER_ID_KEY)}")
    csv_path = Path(f"{user_csv_directory}/{csv_name}.csv")

    error_message = validate_csv_writable(csv_name, csv_content, user_csv_directory, csv_path)
    if error_message:
        logger.warning(error_message)
        return error_message

    error_message = create_csv_helper(csv_name, csv_path, csv_content)
    if error_message:
        return error_message
    else:
        return json.dumps(os.listdir(user_csv_directory))


@app.route('/delete_csv', methods=['POST'])
def delete_csv():
    if not valid_user():
        return "Unauthorized", 401

    csv_name = request.get_json()["name"]
    user_csv_directory = Path(f"{CSV_DIRECTORY}/{session.get(USER_ID_KEY)}")
    csv_path = Path(f"{user_csv_directory}/{csv_name}.csv")

    logger.info(f"Attempting to delete CSV at path: {csv_path}")

    if os.path.exists(csv_path):
        try:
            os.remove(csv_path)
            if FILE_COUNT_KEY in session and session[FILE_COUNT_KEY] > 0:
                session[FILE_COUNT_KEY] -= 1

            logger.info(f"CSV {csv_name}.csv deleted successfully.")
            return json.dumps(os.listdir(user_csv_directory))
        except Exception as delete_exception:
            error_message = f"Error deleting CSV: {delete_exception}"
            logger.error(error_message)
            return error_message


def cleanup():
    for user in users.keys():
        if (datetime.now() - users[user]).total_seconds() > 5:
            del users[user]
            user_csv_directory = Path(f"{os.getcwd()}/csvs/{user}")
            try:
                if os.path.exists(user_csv_directory):
                    shutil.rmtree(user_csv_directory)
            except Exception as cleanup_exception:
                logger.error(f"Error cleaning up user directory {user_csv_directory}: {cleanup_exception}")
            logger.info(f"Cleaned up user: {user}")


def full_clean():
    base_csv_directory = Path(f"{os.getcwd()}/csvs")
    try:
        if os.path.exists(base_csv_directory):
            shutil.rmtree(base_csv_directory)
    except Exception as full_clean_exception:
        logger.error(f"Error performing full cleanup of {base_csv_directory}: {full_clean_exception}")
    logger.info(f"Performed full cleanup of CSV directory")
    session.clear()


scheduler = BackgroundScheduler()
scheduler.add_job(func=cleanup, trigger="interval", seconds=60)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())
atexit.register(lambda: full_clean())
