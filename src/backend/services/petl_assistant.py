import os
import re
from pathlib import Path
from typing import List, Optional

from bs4 import BeautifulSoup
from fastapi import HTTPException, status
from langchain_core.vectorstores import InMemoryVectorStore, VectorStoreRetriever
from langchain_ollama import OllamaEmbeddings
from markdown import markdown
from ollama import ChatResponse, Client

from backend.utils.config import Config
from backend.utils.logger import logger


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
    context_list = [*walk_files(Path("docs")), *walk_files(Path("resources/examples/programs"))]
    logger.info("Successfully retrieved context")
    return context_list


def construct_vector_store():
    retriever: Optional[VectorStoreRetriever] = None
    if Config.MODELS.ENABLED:
        embeddings = OllamaEmbeddings(
            model=Config.MODELS.EMBED,
            base_url=Config.MODELS.URL
        )

        logger.info("Constructing vector store")
        retriever = InMemoryVectorStore.from_texts(
            context,
            embedding=embeddings
        ).as_retriever()
        logger.info("Vector store constructed")
    return retriever


context = get_context()
vectorStoreRetriever: Optional[VectorStoreRetriever] = construct_vector_store()
ollama_client: Optional[Client] = Client(host=Config.MODELS.URL) if Config.MODELS.ENABLED else None


class Prompt:
    Header = f"""
        You are PetlLangGPT, an AI assistant that helps users write and debug PETL scripts. 
        Use the following documentation to help you answer the user's question:
                
        Petl full language context:
    """
    Instructions = f"""
        When providing code examples, ensure they are syntactically correct and relevant to the user's query. 
        If the user asks for a CSV file, respond with a PETL script that creates the CSV file using the provided data. 
        Do not create or manipulate files directly; always provide PETL code for the user to execute.
    """
    Footer = f"""
        Provide a concise and clear response, focusing on helping the user with their PETL-related query.
    """


async def get_llm_response(message: str) -> str:
    try:
        prompt_context = list(map(lambda document: document.page_content, vectorStoreRetriever.invoke(message)))

        prompt = f"{Prompt.Header}\n\n" \
                 f"{context}\n\n" \
                 f"Current prompt-specific context:\n" \
                 f"{prompt_context}\n\n" \
                 f"{Prompt.Instructions}\n\n" \
                 f"User question: {message}\n\n" \
                 f"{Prompt.Footer}\n\n"
        logger.info(prompt)

        response: ChatResponse = ollama_client.chat(
            model=Config.MODELS.CORE,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        logger.info(response)
        return response['message']['content']
    except Exception as llm_exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error during LLM interaction: {llm_exception}")
