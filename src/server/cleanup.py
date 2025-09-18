import atexit
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict

from apscheduler.schedulers.background import BackgroundScheduler

from server.logger import logger

users: Dict[str, datetime] = {}
USER_SESSION_TIMEOUT_DURATION = 60 * 30 # 30 minutes
CLEANUP_INTERVAL = 60 * 15 # 15 minutes


def add_new_user(user_id: str):
    users[user_id] = datetime.now()


def update_user_activity(user_id: str):
    if user_id in users:
        users[user_id] = datetime.now()


def cleanup():
    users_keys = users.keys()
    for user in users_keys:
        if (datetime.now() - users[user]).total_seconds() > USER_SESSION_TIMEOUT_DURATION:
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


scheduler = BackgroundScheduler()
scheduler.add_job(func=cleanup, trigger="interval", seconds=CLEANUP_INTERVAL)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: full_clean())
atexit.register(lambda: scheduler.shutdown())
