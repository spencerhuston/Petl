from typing import Union

from pydantic import BaseModel

csv_content_type = list[list[Union[str, int, bool]]]


class InterpreterModel(BaseModel):
    input: str


class CreateCsvModel(BaseModel):
    name: str
    content: csv_content_type
    include_headers: bool


class DeleteCsvModel(BaseModel):
    name: str


class AssistantModel(BaseModel):
    message: str
