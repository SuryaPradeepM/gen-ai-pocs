"""
RAG Pipeline for Workspace Rag
"""

from llama_index.core import VectorStoreIndex
from llama_index.core.chat_engine.types import ChatMode
from loguru import logger

from src.utils.config_utils import config
from src.utils.models import llm
from src.utils.prompts import rag_qa_prompt_tmpl


def chat(
    index: VectorStoreIndex, user_query: str, chat: bool = False, streaming: bool = True
) -> str:
    """Chat API

    Args:
        index (VectorStoreIndex): Index to get the query engine
        user_query (str): User Query
        chat (bool, optional): to use index as_chat_engine. Defaults to True.
        streaming (bool, optional): to enable streaming output. Defaults to True.

    Returns:
        str: response from model
    """
    if chat:
        # TODO: P3 | Test Memory | Global engine?
        chat_engine = index.as_chat_engine(  # Retrieval with memory
            chat_mode=ChatMode.CONTEXT,
            llm=llm,
            text_qa_template=rag_qa_prompt_tmpl,
            similarity_top_k=config["similarity_top_k"],
        )
        if streaming:
            response = chat_engine.stream_chat(user_query)
        else:
            response = chat_engine.chat(user_query)
    else:
        query_engine = index.as_query_engine(  # Simple RAG
            llm=llm,
            text_qa_template=rag_qa_prompt_tmpl,
            streaming=streaming,
            similarity_top_k=config["similarity_top_k"],
        )
        response = query_engine.query(user_query)

    if streaming:
        try:
            result = ""
            for token in response.response_gen:
                result += token
            return result
            # return Response(response.response_gen) to consume from UI
        except Exception as exp:
            logger.warning("Couldn't get response_gen response with Exception: ", exp)

    return str(response.response)
