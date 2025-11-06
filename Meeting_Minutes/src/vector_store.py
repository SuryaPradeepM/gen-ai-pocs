"""Vector Store Manager for Integration and Interfacing of Llama Index with Azure Cognitive Search
"""

import sys

sys.path.append("core")

import json
import os
from typing import List

from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import TextNode
from llama_index.core.vector_stores.utils import (
    legacy_metadata_dict_to_node,
    metadata_dict_to_node,
    node_to_metadata_dict,
)
from loguru import logger

# from llama_index.vector_stores.azureaisearch import (
#     AzureAISearchVectorStore,
#     IndexManagement,
#     MetadataIndexFieldType,
# )
from src.custom_vector_stores.azure_ai_search import (
    AzureAISearchVectorStore,
    IndexManagement,
    MetadataIndexFieldType,
)
from src.utils.config_utils import DOTENV_PATH, config
from src.utils.models import embed_model
from src.utils.string_utils import list_to_string

# take environment variables from config/.env file
load_dotenv(dotenv_path=DOTENV_PATH, verbose=True, override=True)

# Make sure your .env file has values for the following environment variables
search_service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
# search_service_api_version = "2023-11-01"
credential = (
    AzureKeyCredential(os.environ["AZURE_SEARCH_ADMIN_KEY"])
    if len(os.environ["AZURE_SEARCH_ADMIN_KEY"]) > 0
    else DefaultAzureCredential()
)
embedding_dimensions = int(os.getenv("AZURE_OPENAI_EMBEDDING_DIMENSIONS", 1536))


# Default Index name to use
DEFAULT_INDEX = "compendium-index"


class AzureVectorStoreManager:
    """Manager for vector store to interface with compendium index"""

    def __init__(self):
        self.index_client = SearchIndexClient(
            endpoint=search_service_endpoint,
            credential=credential,
        )

        self.index = None
        self.vector_store = None

    def create_index(self, index_name: str = DEFAULT_INDEX) -> None:
        """Creates index by index_name if it doesn't exist already"""
        _ = AzureAISearchVectorStore(
            search_or_index_client=self.index_client,  # Use index client to create an index
            filterable_metadata_field_keys=None,
            index_name=index_name,
            index_management=IndexManagement.CREATE_IF_NOT_EXISTS,
            id_field_key="id",
            chunk_field_key="chunk",
            embedding_field_key="embedding",
            embedding_dimensionality=embedding_dimensions,
            metadata_string_field_key="metadata",
            doc_id_field_key="doc_id",
            language_analyzer="en.lucene",
            vector_algorithm_type="exhaustiveKnn",
        )

    def delete_index(self, index_name: str = DEFAULT_INDEX) -> None:
        """Deletes index and all the nodes in it by index_name if it exists"""
        self.index_client.delete_index(index_name)

    def _load_vector_store(self, index_name: str) -> None:
        # Use search client for using existing index
        self.search_client = SearchClient(
            endpoint=search_service_endpoint,
            index_name=index_name,
            credential=credential,
        )
        self.vector_store = AzureAISearchVectorStore(
            search_or_index_client=self.search_client,
            filterable_metadata_field_keys=None,
            index_management=IndexManagement.VALIDATE_INDEX,
            id_field_key="id",
            chunk_field_key="chunk",
            embedding_field_key="embedding",
            embedding_dimensionality=embedding_dimensions,
            metadata_string_field_key="metadata",
            doc_id_field_key="doc_id",
            language_analyzer="en.lucene",
            vector_algorithm_type="exhaustiveKnn",
        )

    def upsert_nodes(self, index_name: str, nodes: List[TextNode]) -> None:
        self._load_vector_store(index_name)
        # Load existing index
        if nodes:
            logger.debug(f"Upserting {len(nodes)}. First Node: {nodes[0]}")
            self.vector_store.add(nodes)

    def _index_doc_to_node(self, results) -> List[TextNode]:
        """Convert retrieved results to nodes.

        Args:
            results (_type_): Azure AI Search Results

        Returns:
            List[TextNode]: Converted to Llama-Index Nodes
        """
        nodes = list()
        for result in results:
            metadata = json.loads(result[self.vector_store._field_mapping["metadata"]])
            chunk = result[self.vector_store._field_mapping["chunk"]]

            try:
                node = metadata_dict_to_node(metadata, text=chunk)
            except Exception as exp:
                logger.warning(exp)

                # NOTE: deprecated legacy logic for backward compatibility
                metadata, node_info, relationships = legacy_metadata_dict_to_node(
                    metadata
                )
                node_id = result[self.vector_store._field_mapping["id"]]
                node = TextNode(
                    text=chunk,
                    id_=node_id,
                    metadata=metadata,
                    start_char_idx=node_info.get("start", None),
                    end_char_idx=node_info.get("end", None),
                    relationships=relationships,
                )
            node.embedding = result.get("embedding", None)
            if node.embedding is None:
                logger.error(
                    f"Embedding is missing for Chunk | ID: {result[self.vector_store._field_mapping['id']]} | Text: {chunk[:20]}"
                )
            # logger.debug(f"Retrieved node: {node}")

            nodes.append(node)

        logger.debug(f"Returned {len(nodes)} node{'s' if len(nodes) > 1 else ''}.")

        return nodes

    def get_node_by_ids(
        self, index_name: str, node_ids: List[str], get_node: bool = True
    ) -> List[TextNode]:
        """Get node with ids: List[node_id] in AI Search Index

        Args:
            index_name (str): Index name to search in
            node_ids (List[str]): List of Id's of node / chunk / AI Search Document to pull
            get_node (bool, optional): Convert AI Search results to nodes?. Defaults to True.
        """
        self._load_vector_store(index_name)
        id_field = self.vector_store._field_mapping["id"]
        if len(node_ids) == 1:
            filter = f"{id_field} eq '{node_ids[0]}'"
        else:
            # Caveat: One of the limits on a filter expression is the maximum size limit of the request.
            # The entire request, inclusive of the filter, can be a maximum of 16 MB for POST, or 8 KB for GET.
            # There's also a limit on the number of clauses in your filter expression.

            # => search.in is better than multiple or disjunctions
            # filter = " or ".join(f"{id_field} eq '{id}'" for id in node_ids)

            # https://learn.microsoft.com/en-us/azure/search/search-query-odata-search-in-function
            filter = f"search.in({id_field}, '{list_to_string(node_ids, ',')}', ',')"

        results = self.vector_store._search_client.search(
            search_text="*", filter=filter
        )
        if not results:
            logger.warning(
                f"Document with ids: {node_ids} not found in the index: {index_name}"
            )
            return []
        if get_node:
            return self._index_doc_to_node(results)
        return results

    def get_all_nodes(self, index_name: str) -> List[TextNode]:
        # TODO: Test with large number of Search Index Docs
        self._load_vector_store(index_name)

        # wild-card "*"" search to get all nodes in index
        results = self.vector_store._search_client.search(search_text="*")
        if not results:
            logger.warning(f"No documents not found in the index: {index_name}")
            return []
        return self._index_doc_to_node(results)

    def _delete_nodes_in_vector_store(
        self,
        nodes_to_delete: List[TextNode],
        index_name: str,
    ) -> None:
        """
        Delete Nodes from the AI Search Index
        """
        self._load_vector_store(index_name)

        docs_to_delete = []
        for node in nodes_to_delete:
            doc = {"id": node.id_}
            docs_to_delete.append(doc)

        if len(docs_to_delete) > 0:
            logger.debug(f"Deleting {len(docs_to_delete)} documents")
            self.search_client.delete_documents(docs_to_delete)

    def delete_file_nodes(self, index_name: str, file_name: str) -> None:
        """deletes nodes given a file_name

        Args:
            index_name (str): index to delete nodes from
            file_name (str): file_name whose associated nodes to be deleted
        """
        nodes_to_delete = []
        nodes = self.get_all_nodes(index_name)  # TODO: not efficient!
        for node in nodes:
            if node.metadata.get("file_name", "Unknown") == file_name:
                nodes_to_delete.append(node)
        try:
            logger.info(
                f"Deleting {len(nodes_to_delete)} chunks from file: {file_name}"
            )
            self._delete_nodes_in_vector_store(nodes_to_delete, index_name)
        except Exception as exp:
            logger.error(
                f"Deleting docs from AI Search Index: {index_name} failed with exception: {exp}"
            )

    def delete_nodes_by_ids(self, index_name: str, node_ids: List[str]) -> None:
        """deletes nodes by ids

        Args:
            index_name (str): index to delete nodes from
            node_ids (List[str]): List of node_ids to delete
        """
        self._load_vector_store(index_name)

        docs_to_delete = []
        for node_id in node_ids:
            doc = {"id": node_id}
            docs_to_delete.append(doc)

        # Delete operations are idempotent. That is, even if a document with "id" does
        # not exist in the index, attempting a delete operation with that key will
        # result in a 200 status code.
        if len(docs_to_delete) > 0:
            logger.debug(f"Deleting {len(docs_to_delete)} documents")
            self.search_client.delete_documents(docs_to_delete)

    def load_index(self, index_name: str) -> VectorStoreIndex:
        self._load_vector_store(index_name)
        self.index = VectorStoreIndex.from_vector_store(
            self.vector_store,
            embed_model=embed_model,
            use_async=config["use_async"],
            show_progress=config["show_progress"],
        )
        return self.index
