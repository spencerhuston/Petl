import os
import re
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup
from langchain_ollama import OllamaEmbeddings
from markdown import markdown
from ollama import ChatResponse, chat
from langchain_core.vectorstores import InMemoryVectorStore

from server.logger import logger


def markdown_to_text(markdown_text: str) -> str:
    html = markdown(markdown_text)
    html = re.sub(r'<pre>(.*?)</pre>', ' ', html)
    html = re.sub(r'<code>(.*?)</code >', ' ', html)
    return ''.join(BeautifulSoup(html, "html.parser").findAll(text=True))


def walk_files(directory: Path) -> List[str]:
    content = []
    try:
        for entry in os.listdir(directory):
            full_path = Path(f"{directory}/{entry}")
            if "edge_cases" in str(entry):
                continue
            elif os.path.isdir(full_path):
                content += [*walk_files(full_path)]
            else:
                with open(full_path, 'r') as context_file:
                    logger.info(f"Reading context: {full_path}")
                    content.append(markdown_to_text(context_file.read()))
    except Exception as walk_exception:
        raise Exception(f"Error readings file(s) from {directory} directory: {walk_exception}")
    return content


def get_context() -> List[str]:
    logger.info("Fetching context")
    context = [*walk_files(Path("docs")), *walk_files(Path("tests/resources/programs"))]
    logger.info("Successfully retrieved context")
    return context


context = get_context()
OLLAMA_MODEL = 'qwen2.5:7b'

embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

logger.info("Constructing vector store")
retriever = InMemoryVectorStore.from_texts(
    context,
    embedding=embeddings
).as_retriever()
logger.info("Vector store constructed")


def get_llm_response(chat_message: str) -> str:
    prompt_context = retriever.invoke(chat_message)
    prompt = f"""
            You are PetlLangGPT, an AI assistant that helps users write and debug PETL scripts. 
            Use the following documentation to help you answer the user's question:
            
            Petl full language context:
            {context}
            
            Current prompt-specific context:
            {prompt_context}
            
            When providing code examples, ensure they are syntactically correct and relevant to the user's query. 
            If the user asks for a CSV file, respond with a PETL script that creates the CSV file using the provided data. 
            Do not create or manipulate files directly; always provide PETL code for the user to execute.
            
            User question: {chat_message}
            
            Provide a concise and clear response, focusing on helping the user with their PETL-related query.
            """
    logger.info(prompt)

    response: ChatResponse = chat(model=OLLAMA_MODEL, messages=[
        {
            "role": "user",
            "content": prompt
        },
    ])
    logger.info(response)
    return response['message']['content']
