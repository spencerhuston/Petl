import json
import os
import shutil
from datetime import datetime

import redis

from backend.utils.config import Config
from backend.utils.logger import logger

logger.info("Starting Redis client")
redis_client = redis.Redis(host=Config.REDIS.HOST, port=Config.REDIS.PORT, db=Config.REDIS.DB, decode_responses=True)
try:
    redis_client.ping()
except ConnectionError as redis_client_connection_error:
    raise Exception(f"Redis connection error: {redis_client_connection_error}\n\nTry server restart")
logger.info("Redis client successfully connected")


HISTORY_KEY = "history"
FILES_KEY = "files"
LAST_UPDATE_TIME_KEY = "last_update_time"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def cleanup():
    current_session_ids = list(map(lambda session_id: session_id.decode('utf-8'), redis_client.scan_iter()))
    all_session_ids = os.listdir(Config.CSV.DIRECTORY)
    expired_session_ids = list(set(current_session_ids) - set(all_session_ids))

    for session_id in expired_session_ids:
        session_csv_directory = Config.CSV.DIRECTORY / session_id.decode('utf-8')
        try:
            if os.path.exists(session_csv_directory):
                shutil.rmtree(session_csv_directory)
        except Exception as cleanup_exception:
            logger.error(f"Error cleaning up session directory {session_csv_directory}: {cleanup_exception}")
        logger.info(f"Cleaned up session: {session_id}")


def get_session(session_key: str, key: str) -> (dict, list):
    session_mapping: dict = json.loads(redis_client.get(session_key))
    session_list = session_mapping.get(key, [])
    return session_mapping, session_list


def update_session_mapping(session_key: str, session_mapping: dict):
    session_mapping[LAST_UPDATE_TIME_KEY] = datetime.now().strftime(DATE_FORMAT)
    redis_client.set(session_key, json.dumps(session_mapping), ex=Config.REDIS.EXPIRE_SECONDS)


def session_list_add_value(session_key: str, key: str, value: str):
    session_mapping, session_list = get_session(session_key, key)
    session_list.append(value)
    session_mapping[key] = session_list
    update_session_mapping(session_key, session_mapping)


def session_list_remove_value(session_key: str, key: str, value: str):
    session_mapping, session_list = get_session(session_key, key)
    session_list.remove(value)
    session_mapping[key] = session_list
    update_session_mapping(session_key, session_mapping)
