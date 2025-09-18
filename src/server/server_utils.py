import csv
import json
import os
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, status

from server.config import Config
from server.logger import logger
from server.redis_client import redis_client, FILES_KEY


def get_csv_path(directory: Path, name: str) -> Path:
    return directory / (f"{name}.csv" if not name.endswith(".csv") else name)


def validate_csv_content(name: str,
                         content: str):
    error: Optional[str] = None
    if not name or not content:
        error = "CSV name and content must be provided."
    elif len(content[0]) * len(content) > Config.CSV.MAX.SIZE:
        error = "CSV content exceeds maximum allowed size."
    elif "," in name or "/" in name or "\\" in name:
        error = "CSV name contains invalid characters."

    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=error)


def validate_csv_writable(name: str,
                          content: str,
                          directory: Path,
                          cookie_key: str):
    validate_csv_content(name, content)
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)

    path = directory / f"{name}.csv"
    if path.exists():
        logger.info(f"Removing existing CSV: {path}")
        os.remove(path)

    if len(redis_client.get(cookie_key)[FILES_KEY]) >= Config.CSV.MAX.FILES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Too many CSV files exist. Please delete some before creating new ones.")


def create_csv(path: Path, content: str, cookie_key: str):
    logger.info(f"Creating new CSV: {path}.csv")

    try:
        with open(path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(content)

        if not os.path.exists(path):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Failed to write CSV")

        files = redis_client.hget(cookie_key, FILES_KEY)
        files.append(str(path))
        redis_client.hset(cookie_key, FILES_KEY, files)

        logger.info(f"CSV {path}.csv created successfully.")
    except Exception as csv_write_exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error writing CSV: {csv_write_exception}")


def delete_csv(directory: Path, path: Path, cookie_key: str) -> Optional[str]:
    logger.info(f"Attempting to delete CSV at path: {path}")
    if os.path.exists(path):
        try:
            os.remove(path)

            files = redis_client.hget(cookie_key, FILES_KEY)
            files.remove(str(path))
            redis_client.hset(cookie_key, FILES_KEY, files)

            redis_client.get(cookie_key)[FILES_KEY].remove(str(path))
            logger.info(f"CSV {path} deleted successfully.")
            return json.dumps(os.listdir(directory))
        except Exception as delete_exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error deleting CSV: {delete_exception}")
