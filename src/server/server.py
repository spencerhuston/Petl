import io
import json
import os
import uuid
from contextlib import redirect_stdout
from pathlib import Path
from typing import Optional

from flask import Flask, request, session

from petllang.execution.execute import execute_petl_script_direct
from server.cleanup import update_user_activity, add_new_user
from server.csv_utils import FILE_COUNT_KEY, validate_csv_writable, create_csv_helper, CSV_DIRECTORY, delete_csv_helper
from server.logger import logger
from server.petlassistant import get_llm_response

app = Flask(__name__)

app.secret_key = os.urandom(32)
app.config["SESSION_PERMANENT"] = False

USER_ID_KEY = "userId"
INTERPRETER_HISTORY_KEY = "history"


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

    return delete_csv_helper(csv_path, user_csv_directory)


@app.route('/chat', methods=['POST'])
def process_chat():
    if not valid_user():
        return "Unauthorized", 401

    chat_message = request.get_json()["message"]
    logger.info(f"Received chat message:\n{chat_message}")

    response = get_llm_response(chat_message)

    logger.debug(response)
    return response
