import json
import os
import shutil
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Union

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, status, Depends, Cookie, Response, HTTPException

from petllang.builtins import table_petl_builtins
from petllang.execution.execute import execute_petl_script_direct
from server.utils.config import Config
from server.utils.logger import logger
from server.utils.models import InterpreterModel, CreateCsvModel, DeleteCsvModel, AssistantModel, csv_content_type
from server.services.petl_assistant import get_llm_response
from server.services.redis_client import redis_client, HISTORY_KEY, FILES_KEY, LAST_UPDATE_TIME_KEY, DATE_FORMAT, cleanup, \
    get_session, session_list_add_value
from server.utils.server_utils import validate_csv_writable, create_csv, delete_csv, get_csv_path


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
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=cleanup, trigger="interval", seconds=Config.CLEANUP.INTERVAL_SECONDS)
    scheduler.start()

    yield

    redis_client.close()
    scheduler.shutdown()
    on_exit()


app = FastAPI(lifespan=lifespan)
app.secret_key = os.urandom(32)


def verify_user(petl_cookie: Union[str, None] = Cookie(None)):
    if not petl_cookie:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized: No session cookie found.")


@app.get('/', status_code=status.HTTP_201_CREATED)
def start_user_session(response: Response, petl_cookie: Union[str, None] = Cookie(None)):
    if not petl_cookie:
        #session_id = str(uuid.uuid4())
        session_id = "TEST_COOKIE"
        logger.info("New session ID: " + session_id)
        redis_client.setex(name=session_id,
                           time=Config.REDIS.EXPIRE_SECONDS,
                           value=json.dumps({
                               HISTORY_KEY: [],
                               FILES_KEY: [],
                               LAST_UPDATE_TIME_KEY: datetime.now().strftime(DATE_FORMAT)
                           }))
        response.set_cookie(key="petl_cookie", value=session_id)
    else:
        logger.info("Session already exists: " + str(petl_cookie))
        response.status_code = status.HTTP_200_OK


@app.post('/interpret', status_code=status.HTTP_200_OK, dependencies=[Depends(verify_user)])
async def interpret(interpreter_model: InterpreterModel, petl_cookie: Union[str, None] = Cookie(None)):
    input = interpreter_model.input
    logger.info(f"Interpreter request: {input}")

    session_list_add_value(petl_cookie, HISTORY_KEY, input)
    table_petl_builtins.session_directory = Path(f"{Config.CSV.DIRECTORY}/{petl_cookie}")

    try:
        return await execute_petl_script_direct(input)
    except Exception as interpret_exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Interpretation error: {interpret_exception}")


@app.get('/history', status_code=status.HTTP_200_OK, dependencies=[Depends(verify_user)])
def history(petl_cookie: Union[str, None] = Cookie(None)):
    _, session_history = get_session(petl_cookie, HISTORY_KEY)
    logger.info(f"Fetching interpreter history: {session_history}")
    return session_history


@app.post('/csv', status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_user)])
def create(create_csv_model: CreateCsvModel, petl_cookie: Union[str, None] = Cookie(None)):
    directory = Path(f"{Config.CSV.DIRECTORY}/{petl_cookie}")

    name: str = create_csv_model.name
    content: csv_content_type = create_csv_model.content
    include_headers: bool = create_csv_model.include_headers

    validate_csv_writable(name, content, directory, petl_cookie)
    create_csv(get_csv_path(directory, name), content, include_headers, petl_cookie)

    return os.listdir(directory)


@app.delete('/csv', status_code=status.HTTP_200_OK, dependencies=[Depends(verify_user)])
def delete(delete_csv_model: DeleteCsvModel, petl_cookie: Union[str, None] = Cookie(None)):
    name = delete_csv_model.name
    directory = Path(f"{Config.CSV.DIRECTORY}/{petl_cookie}")
    delete_csv(get_csv_path(directory, name), petl_cookie)
    return os.listdir(directory)


@app.post('/assistant', status_code=status.HTTP_200_OK, dependencies=[Depends(verify_user)])
async def assistant(assistant_model: AssistantModel):
    message = assistant_model.message
    logger.info(f"Received chat message:\n{message}")
    return await get_llm_response(message)
