import csv
import json
import os
from pathlib import Path
from typing import Optional

from flask import session

from server.logger import logger

CSV_DIRECTORY = Path(f"{os.getcwd()}/csvs")
MAX_CSV_SIZE = 20000  # Maximum number of cells in CSV (rows * columns)

FILE_COUNT_KEY = "file_count"
MAX_FILE_COUNT = 5


def validate_csv_content(csv_name: str,
                         csv_content: str) -> Optional[str]:
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
    return None


def validate_csv_writable(csv_name: str,
                          csv_content: str,
                          user_csv_directory: Path,
                          csv_path: Path) -> Optional[str]:
    error_message = validate_csv_content(csv_name, csv_content)
    if error_message:
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


def delete_csv_helper(csv_path: Path, directory: Path) -> Optional[str]:

    logger.info(f"Attempting to delete CSV at path: {csv_path}")

    if os.path.exists(csv_path):
        try:
            os.remove(csv_path)
            if FILE_COUNT_KEY in session and session[FILE_COUNT_KEY] > 0:
                session[FILE_COUNT_KEY] -= 1

            logger.info(f"CSV {csv_path} deleted successfully.")
            return json.dumps(os.listdir(directory))
        except Exception as delete_exception:
            error_message = f"Error deleting CSV: {delete_exception}"
            logger.error(error_message)
            return error_message
