import os
import shutil

import redis

from server.config import Config
from server.logger import logger

redis_client = redis.Redis(host=Config.REDIS.URL, port=Config.REDIS.PORT, db=Config.REDIS.DB, decode_responses=True)


HISTORY_KEY = "history"
FILES_KEY = "files"
LAST_UPDATE_TIME_KEY = "last_update_time"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def cleanup():
    current_session_ids = redis_client.scan_iter()
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
