import io
import json
import os
import shutil
import uuid
from contextlib import redirect_stdout, asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional, Annotated

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, status, Depends, Cookie, Response, HTTPException

from petllang.execution.execute import execute_petl_script_direct
from server.config import Config
from server.redis_client import redis_client, HISTORY_KEY, FILES_KEY, LAST_UPDATE_TIME_KEY, DATE_FORMAT, cleanup
from server.server_utils import validate_csv_writable, create_csv, delete_csv, \
    get_csv_path
from server.logger import logger
from server.petl_assistant import get_llm_response, construct_vector_store


def on_exit():
    base_csv_directory = Path(f"{os.getcwd()}/csvs")
    try:
        if os.path.exists(base_csv_directory):
            shutil.rmtree(base_csv_directory)
    except Exception as full_clean_exception:
        logger.error(f"Error performing full cleanup of {base_csv_directory}: {full_clean_exception}")
    logger.info(f"Performed full cleanup of CSV directory")


@asynccontextmanager
async def lifespan(app: FastAPI):
    construct_vector_store()

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=cleanup, trigger="interval", seconds=Config.CLEANUP.INTERVAL_SECONDS)
    scheduler.start()

    yield

    redis_client.close()
    scheduler.shutdown()
    on_exit()


app = FastAPI(lifespan=lifespan)
app.secret_key = os.urandom(32)


async def verify_user(cookie_key: Annotated[str | None, Cookie()] = None):
    if not cookie_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized: No session cookie found.")


@app.get('/', status_code=status.HTTP_201_CREATED)
def start_user_session(response: Response, cookie_key: Annotated[str | None, Cookie()] = None):
    if not cookie_key:
        session_id = str(uuid.uuid4())
        logger.info("New session ID: " + session_id)
        redis_client.hsetex(name=session_id,
                            mapping={
                                HISTORY_KEY: [],
                                FILES_KEY: [],
                                LAST_UPDATE_TIME_KEY: datetime.now().strftime(DATE_FORMAT)
                            },
                            ex=Config.REDIS.EXPIRE_SECONDS)
        response.set_cookie(key=cookie_key, value=session_id)
    response.status_code = status.HTTP_200_OK


@app.post('/interpret', status_code=status.HTTP_200_OK, dependencies=[Depends(verify_user)])
async def interpret(input_code: str, cookie_key: str):
    logger.info(f"Interpreter request: {input_code}")

    history = redis_client.hget(cookie_key, HISTORY_KEY)
    history.append(input_code)
    redis_client.hset(cookie_key, HISTORY_KEY, history)

    try:
        stdout_buffer = io.StringIO()
        with redirect_stdout(stdout_buffer):
            result: Optional[str] = execute_petl_script_direct(input_code)

        return_string = stdout_buffer.getvalue() if result else "Invalid program"
        logger.debug(f"Interpreter Output:\n{return_string}\n")
        return return_string
    except Exception as interpret_exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Interpretation error: {interpret_exception}")


@app.get('/history', status_code=status.HTTP_200_OK, dependencies=[Depends(verify_user)])
def history(cookie_key: str):
    session_history = redis_client.hget(cookie_key, HISTORY_KEY) or []
    logger.info(f"Fetching interpreter history: {session_history}")
    return json.dumps(session_history)


@app.post('/csv', status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_user)])
def create(name: str, content: str, cookie_key: str):
    directory = Path(f"{Config.CSV.DIRECTORY}/{cookie_key}")

    validate_csv_writable(name, content, directory, cookie_key)
    create_csv(get_csv_path(directory, name), content, cookie_key)

    return json.dumps(os.listdir(directory))


@app.delete('/csv', status_code=status.HTTP_200_OK, dependencies=[Depends(verify_user)])
def delete(name: str, cookie_key: str):
    directory = Path(f"{Config.CSV.DIRECTORY}/{cookie_key}")
    return delete_csv(directory, get_csv_path(directory, name), cookie_key)


@app.post('/assistant', status_code=status.HTTP_200_OK, dependencies=[Depends(verify_user)])
async def assistant(message: str):
    logger.info(f"Received chat message:\n{message}")
    return get_llm_response(message)
