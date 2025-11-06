"""Prompt Construction for various tasks
"""

from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.core.prompts import SelectorPromptTemplate
from llama_index.core.prompts.base import ChatPromptTemplate, PromptTemplate
from llama_index.core.prompts.prompt_type import PromptType
from llama_index.core.prompts.utils import is_chat_model

from src.utils.config_utils import ROOT_DIR
from src.utils.file_utils import load_hjson, load_json

PROMPTS_PATH = ROOT_DIR / "config/prompts.hjson"
PROMPT_TMPL_PATH = ROOT_DIR / "config/prompt_templates.json"
prompts = load_hjson(PROMPTS_PATH)
prompt_templates = load_json(PROMPT_TMPL_PATH)


### Translation Prompts ###
TRANSLATE_QUERY = prompts.get(
    "generic_translate_query",
    "Translate the content into Japanese",
)

TRANSLATE_USER_PROMPT_TMPL = (
    "Content to be translated is below:\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Query: {query_str}\n"
    "Translation: \n"
)

SIMPLE_CONTEXT_PROMPT = "\n\n{context_str}\n\n"

DEFAULT_TRANSLATE_PROMPT = PromptTemplate(
    TRANSLATE_USER_PROMPT_TMPL, prompt_type=PromptType.CUSTOM
)


def get_translation_template(system_prompt: str = prompts["translate_system_msg"]):
    if not isinstance(system_prompt, str):
        system_prompt = prompts["translate_system_msg"]
    if not system_prompt:
        system_prompt = prompts["translate_system_msg"]

    translate_system_prompt = ChatMessage(
        content=system_prompt,
        role=MessageRole.SYSTEM,
    )

    TRANSLATE_TMPL_MSGS = [
        translate_system_prompt,
        ChatMessage(
            content=SIMPLE_CONTEXT_PROMPT,
            role=MessageRole.USER,
        ),
    ]

    CHAT_TRANSLATE_PROMPT = ChatPromptTemplate(message_templates=TRANSLATE_TMPL_MSGS)
    DEFAULT_TRANSLATE_PROMPT_SEL = SelectorPromptTemplate(
        default_template=DEFAULT_TRANSLATE_PROMPT,
        conditionals=[(is_chat_model, CHAT_TRANSLATE_PROMPT)],
    )
    return DEFAULT_TRANSLATE_PROMPT_SEL


### Generic Summarize Prompts ###
GENERIC_SUMMARY_QUERY = """Summarize the given document."""


def get_generic_summarize_template(
    system_prompt: str = prompts["generic_summarize_system_msg"],
):
    """getter utility to get a formatted prompt template to utilize for TreeSummarize

    Args:
        system_prompt (str, optional): Optional System msg instructions to do summarizations.
        Defaults to prompts["generic_summarize_system_msg"].
    """
    if not isinstance(system_prompt, str):
        system_prompt = prompts["generic_summarize_system_msg"]
    if not system_prompt:
        system_prompt = prompts["generic_summarize_system_msg"]

    tree_summarize_suffix = (
        "\n\nContext information from multiple chunks from single document is below.\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Given the information from the given context above and not prior knowledge.\n"
        "{query_str}\n"
        "Summary: \n"
    )
    system_prompt_tmpl = system_prompt + tree_summarize_suffix
    return PromptTemplate(system_prompt_tmpl, prompt_type=PromptType.SUMMARY)


### Summarize Meetings' Transcriptions Prompts ###
TRANSCRIPT_SUMMARY_QUERY = """Generate Meeting Minutes.
**The output ought to strictly incorporate only the following key sections: Agenda, Main Points of Discussion (Organized in topics), Decisions Made (if any), and Action Items (Overall and Individual, if present)**"""


def get_meeting_summarize_template(
    system_prompt: str = prompts["meeting_summarize_system_msg"],
):
    """getter utility to get a formatted prompt template to utilize for TreeSummarize

    Args:
        system_prompt (str, optional): Optional System msg instructions to do summarizations.
        Defaults to prompts["meeting_summarize_system_msg"].
    """
    if not isinstance(system_prompt, str):
        system_prompt = prompts["meeting_summarize_system_msg"]
    if not system_prompt:
        system_prompt = prompts["meeting_summarize_system_msg"]

    tree_summarize_suffix = (
        "\n* **Don't include the Date, Time and Location of meeting in the minutes output**\n"
        "\n\nContext information from multiple chunks from single transcription is below.\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Given the information from the given transcript above and not prior knowledge.\n"
        "{query_str}\n"
        "Minutes: \n"
    )
    system_prompt_tmpl = system_prompt + tree_summarize_suffix
    return PromptTemplate(system_prompt_tmpl, prompt_type=PromptType.SUMMARY)


# Attendance Report Parsing (Optional)
attendance_template = (
    "Given, the Meeting Attendance Report Information below:\n"
    "---------------------\n"
    "{context_str}"
    "\n---------------------\n"
    "Understand and Breakdown the information present in the first two sections, 1. Summary & 2. Participants.\n"
    "Depending only on above information, not prior knowledge,\n"
    "Create a very concise summary including the Meeting title, timings and details participants who attended the meeting, their emails:\n"
)
ATTENDANCE_PROMPT = PromptTemplate(attendance_template)


### Patient Compendium Report Generation Prompts ###
GENERIC_SUMMARIZE = prompts.get(
    "generic_summarize",
    "Describe what the provided text is about and generate a concise summary",
)


### Workspaces RAG ###

qa_prompt_tmpl_str = """\
Context information is below.
---------------------
{context}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {query}
Answer: \
"""

template_var_mappings = {"context_str": "context", "query_str": "query"}

rag_qa_prompt_tmpl = PromptTemplate(
    qa_prompt_tmpl_str, template_var_mappings=template_var_mappings
)
