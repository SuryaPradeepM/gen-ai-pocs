"""Utilities to initialize Embedding and LLM Models
"""

import os

from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.core.node_parser import (
    MarkdownElementNodeParser,
    MarkdownNodeParser,
    SemanticSplitterNodeParser,
    SentenceSplitter,
    TokenTextSplitter,
)
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.azure_openai import AzureOpenAI
from loguru import logger

from src.utils.config_utils import DOTENV_PATH, config

# take environment variables from config/.env file
load_dotenv(dotenv_path=DOTENV_PATH, verbose=True, override=True)


TEMP = config["temperature"]
MAX_RETRIES = config["max_retries"]
SPLITTER = config["splitter"]  # TODO: deprecated
SPLITTING_STRATEGIES = {
    "Doc Intelligence + Layout Aware Splitter",
    "Simple Token Splitter",
    "Sentence Splitter",
    "Semantic Splitter",
}

CHUNK_SIZE = config["chunk_size"]
CHUNK_OVERLAP = config["chunk_overlap"]
EMBEDDING_MODEL = config["embedding_model"]
SEMANTIC_SPLITTER_BUFFER_SIZE = config["semantic_splitter_buffer_size"]
SEMANTIC_SPLITTER_BREAKPOINT_PERCENTILE_THRESH = config[
    "semantic_splitter_breakpoint_percentile_thresh"
]

# Llama Index does not support RBAC authentication, an API key is required
azure_openai_key = os.environ.get("AZURE_OPENAI_API_KEY")
if len(azure_openai_key) == 0:
    raise Exception("API key required")
azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
api_version = os.environ.get("AZURE_OPENAI_API_VERSION")
ada_embedder = os.environ.get("AZURE_OPENAI_ADA_DEPLOYMENT_NAME")
gpt_deployment_name = os.environ.get("AZURE_OPENAI_GPT_DEPLOYMENT_NAME")
gpt_model_version = os.environ.get("GPT_MODEL_VERSION")
ada_embedder_model_version = os.environ.get("ADA_EMBEDDER_MODEL_VERSION")


def get_embed_model(embedding_model_str=EMBEDDING_MODEL):
    if embedding_model_str not in {
        "text-embedding-ada-002",
        "pubmedbert-base-embeddings",
        "pubmedbert-base-embeddings-matryoshka",
    }:
        raise ValueError(f"Invalid Embedding model configured: {embedding_model_str}")
    try:
        match embedding_model_str:
            case "text-embedding-ada-002":
                embed_model = AzureOpenAIEmbedding(
                    model=ada_embedder_model_version,
                    deployment_name=ada_embedder,
                    api_key=azure_openai_key,
                    azure_endpoint=azure_endpoint,
                    api_version=api_version,
                )
            case "pubmedbert-base-embeddings":
                embed_model = HuggingFaceEmbedding(
                    model_name="neuml/pubmedbert-base-embeddings"
                )
            case "pubmedbert-base-embeddings-matryoshka":
                embed_model = HuggingFaceEmbedding(
                    model_name="neuml/pubmedbert-base-embeddings-matryoshka"
                )
    except Exception as exp:
        logger.error(
            f"Unable to initialize {embedding_model_str} with Exception: {exp}\nFalling back to text-embedding-ada-002"
        )
        embed_model = AzureOpenAIEmbedding(
            model=ada_embedder_model_version,
            deployment_name=ada_embedder,
            api_key=azure_openai_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
        )
    return embed_model


def get_llm():
    return AzureOpenAI(
        model=gpt_model_version,
        deployment_name=gpt_deployment_name,
        api_key=azure_openai_key,
        azure_endpoint=azure_endpoint,
        api_version=api_version,
        temperature=TEMP,
        max_retries=MAX_RETRIES,
    )


llm = get_llm()
embed_model = get_embed_model()
# markdown_splitter = MarkdownNodeParser(include_metadata=True)
markdown_splitter = MarkdownElementNodeParser(
    include_metadata=True,
)
sentence_splitter = SentenceSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
)


def get_splitter(splitter_str=SPLITTER, embed_model=embed_model):
    if splitter_str not in SPLITTING_STRATEGIES:
        logger.warning(
            f"Invalid splitter configured: {splitter_str}\nFalling back to Sentence Splitter."
        )
        splitter_str = "Sentence Splitter"
    try:
        match splitter_str:
            case "Sentence Splitter" | "Doc Intelligence + Layout Aware Splitter":
                splitter = sentence_splitter

            case "Semantic Splitter":
                # Splits a document into Nodes, with each node being a group of semantically related sentences. (leverage embed_model)
                splitter = SemanticSplitterNodeParser(
                    embed_model=embed_model,
                    buffer_size=SEMANTIC_SPLITTER_BUFFER_SIZE,
                    breakpoint_percentile_threshold=SEMANTIC_SPLITTER_BREAKPOINT_PERCENTILE_THRESH,
                )
            case "Simple Token Splitter":
                splitter = TokenTextSplitter(
                    chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
                )
    except Exception as exp:
        logger.error(
            f"Unable to initialize {splitter_str} with Exception: {exp}\nFalling back to Sentence Splitter."
        )
        splitter = sentence_splitter
    return splitter


Settings.llm = llm
Settings.embed_model = embed_model
Settings.chunk_size = CHUNK_SIZE
