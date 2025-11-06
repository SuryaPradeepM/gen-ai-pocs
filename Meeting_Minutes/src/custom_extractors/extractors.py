"""
Metadata extraction pipeline for nodes. (Nodes Post-Processing)
"""

from typing import List, Optional

from llama_index.core.extractors import (
    KeywordExtractor,
    QuestionsAnsweredExtractor,
    SummaryExtractor,
    TitleExtractor,
)
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.schema import TextNode, TransformComponent
from loguru import logger

from src.utils.config_utils import config
from src.utils.models import embed_model, llm
from src.utils.string_utils import list_to_string

from .node_category import NOISE, NodeCategoryExtractor

# TODO: P4 from llama_index.core.ingestion.cache import RedisCache
# from llama_index.core.ingestion import IngestionCache
# from llama_index.core.storage.docstore import SimpleDocumentStore
# from llama_index.extractors.entity import EntityExtractor
# from llama_index.extractors.marvin import MarvinMetadataExtractor


SHOW_PROGRESS = config["show_progress"]
NUM_WORKERS = config["num_workers"]
NODE_METADATA_KEYWORDS = config["node_metadata_keywords"]

DEFAULT_TITLE_NODE_TEMPLATE = """\
Context: {context_str}. Give a title that summarizes all of \
the unique entities, titles or themes found in the context. Title: """


DEFAULT_TITLE_COMBINE_TEMPLATE = """\
{context_str}. Based on the above candidate titles and content, \
what is the comprehensive title for this document? Title: """


title_extractor = TitleExtractor(
    llm=llm,
    nodes=4,
    node_template=DEFAULT_TITLE_NODE_TEMPLATE,
    combine_template=DEFAULT_TITLE_COMBINE_TEMPLATE,
    num_workers=NUM_WORKERS,
)
questions_answered = QuestionsAnsweredExtractor(
    llm=llm, questions=2, embedding_only=True, num_workers=NUM_WORKERS
)
summary_extractor = SummaryExtractor(
    llm=llm, summaries=["self"], num_workers=NUM_WORKERS
)
keyword_extractor = KeywordExtractor(
    llm=llm,
    keywords=NODE_METADATA_KEYWORDS,
    num_workers=NUM_WORKERS,
)
# entity_extractor = EntityExtractor(prediction_threshold=0.6)

# Custom category extractor
custom_extractor = NodeCategoryExtractor(llm=llm)


all_transformations = [
    # title_extractor,
    # questions_answered,
    # summary_extractor,
    # keyword_extractor,
    # entity_extractor,
    embed_model,  # generate embedding
]


def get_pipeline(
    transformations: List[TransformComponent] = all_transformations,
) -> IngestionPipeline:
    # TODO: P4 | Integrate Redis Cache
    metadata_extraction_pipeline = IngestionPipeline(
        transformations=transformations,
        # docstore=SimpleDocumentStore(),
        # cache=IngestionCache(cache=RedisCache(redis_uri="redis://127.0.0.1:6379",collection="pipeline_cache")),
    )
    return metadata_extraction_pipeline


def extract_metadata(
    nodes: List[TextNode],
    labels_descriptions_dict: Optional[dict] = None,
    pipeline: IngestionPipeline = None,
    convert_node_category_to_str: bool = True,
    sanity_check_node_category: bool = True,
) -> List[TextNode]:
    """Extracts Nodes' metadata

    Args:
        nodes (List[TextNode]): List of input nodes
        labels_descriptions_dict (Optional[dict], optional): TextNode category labels and associated descriptions. Defaults to None.
        pipeline (IngestionPipeLine): metadata extraction pipeline to run. Defaults to None.
        convert_node_category_to_str (bool): Convert "category" in node.metadata to string (for Azure AI Search compatibility). Defaults to True.
        sanity_check_node_category (bool): Apply length filter on nodes and give the label of noise . Defaults to True.

    Returns:
        List[TextNode]: List of nodes with updated metadata
    """
    # TODO: P2 | Add delays and batch processing, to handle rate limits hit with huge volume
    if pipeline is None:
        category_extractor = custom_extractor.get_extractor(
            labels_descriptions_dict=labels_descriptions_dict
        )
        all_transformations.append(category_extractor)
        pipeline = get_pipeline(all_transformations)
    try:
        pipeline.run(
            nodes=nodes,
            # cache_collection="transformations_cache",
            # num_workers=NUM_WORKERS,  # if > 1, Hits LLMs rate limits, to process high volume of nodes
            show_progress=SHOW_PROGRESS,
            in_place=True,
        )

        if sanity_check_node_category and isinstance(labels_descriptions_dict, dict):
            label_set = set(labels_descriptions_dict.keys())
            label_set.add("Noise")
            for node in nodes:
                node_categories = node.metadata.get("category", None)
                if node_categories is None:
                    continue
                if len(node.text) < 40:
                    # tiny chunks are considered as Noise
                    node.metadata["category"] = ["Noise"]
                    continue

                validated_categories = set()
                for category in node_categories:
                    if category not in label_set:
                        validated_categories.add("Noise")
                    else:
                        validated_categories.add(category)

                if validated_categories == NOISE:
                    # if all categories predicted are
                    node.metadata["category"] = ["Noise"]
                else:
                    validated_categories.discard("Noise")
                    node.metadata["category"] = list(validated_categories)

        if convert_node_category_to_str:
            for node in nodes:
                if "category" not in node.metadata:
                    continue
                node.metadata["category"] = list_to_string(node.metadata["category"])
    except Exception as exp:
        logger.error(f"Extract metadata failed with Exception: {exp}")


def reclassify_nodes(
    nodes: List[TextNode], labels_descriptions_dict: dict
) -> List[TextNode]:
    """Reclassify nodes with given updated labels

    Args:
        nodes (List[TextNode]): List of input nodes
        labels_descriptions_dict (dict): node category labels and associated descriptions

    Returns:
        List[TextNode]: List of nodes with updated category metadata
    """
    category_extractor = custom_extractor.get_extractor(
        labels_descriptions_dict=labels_descriptions_dict
    )
    category_extraction_pipeline = get_pipeline(transformations=[category_extractor])

    for node in nodes:
        # delete existing node category
        node.metadata.pop("category", None)

    return extract_metadata(
        nodes,
        pipeline=category_extraction_pipeline,
        labels_descriptions_dict=labels_descriptions_dict,
    )
