import csv
import os
import re
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, status

from server.config import Config
from server.logger import logger
from server.models import csv_content_type
from server.redis_client import FILES_KEY, session_list_add_value, session_list_remove_value, get_session


def escape_ansi(result: str) -> str:
    ansi_escape_regex = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    return ansi_escape_regex.sub('', result)


def get_csv_path(directory: Path, name: str) -> Path:
    return directory / (f"{name}.csv" if not name.endswith(".csv") else name)


def validate_csv_content(name: str,
                         content: list[list[str]]):
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
                          content: csv_content_type,
                          directory: Path,
                          session_key: str):
    validate_csv_content(name, content)
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)

    path = directory / f"{name}.csv"
    if path.exists():
        logger.info(f"Removing existing CSV: {path}")
        os.remove(path)

    _, files = get_session(session_key, FILES_KEY)
    if len(files) >= Config.CSV.MAX.FILES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Too many CSV files exist. Please delete some before creating new ones.")


def create_csv(path: Path, content: csv_content_type, include_headers: bool, session_key: str):
    logger.info(f"Creating new CSV: {path}.csv")

    try:
        with open(path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(content if include_headers else content[1:])

        if not os.path.exists(path):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Failed to write CSV")

        session_list_add_value(session_key, FILES_KEY, str(path))
        logger.info(f"CSV {path}.csv created successfully.")
    except Exception as csv_write_exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error writing CSV: {csv_write_exception}")


def delete_csv(path: Path, session_key: str):
    logger.info(f"Attempting to delete CSV at path: {path}")
    if os.path.exists(path):
        try:
            os.remove(path)
            session_list_remove_value(session_key, FILES_KEY, str(path))
            logger.info(f"CSV {path} deleted successfully.")
        except Exception as delete_exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error deleting CSV: {delete_exception}")
