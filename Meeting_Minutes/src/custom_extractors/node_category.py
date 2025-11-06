"""
Custom Category Metadata extractor for nodes.

LLM-driven metadata extraction through Open AI Pydantic Program.
Currently, only `TextNode` is supported.

Supported metadata:
TextNode-level:
    - `NodeCategoryExtractor`: Category of each node (label categories defined in labels_descriptions)

The prompts used to generate the metadata are specifically aimed to help
disambiguate the chunk or node from other similar chunks or nodes.
(similar with contrastive learning)
"""

from typing import Any, List, Optional

from llama_index.core.extractors import PydanticProgramExtractor
from llama_index.core.llms.llm import LLM
from llama_index.core.service_context_elements.llm_predictor import LLMPredictorType
from llama_index.program.openai import OpenAIPydanticProgram
from pydantic import BaseModel, Field

from src.utils.config_utils import config
from src.utils.models import llm

# Compendium default labels
DEFAULT_LABELS_DESCRIPTIONS_DICT = {
    "disease_burden": """If the text contains information alluding to “Disease burden” of a patient.
Disease burden refers to the impact of a health problem as measured by 
Impact on Daily Living, Emotional Burden, and Psychological Impact, 
Impact on Employment, Financial costs, Impact on Caregivers, mortality, morbidity, or other indicators.""",
    "disease_area_overview": """If the text contains information alluding to general "Disease Area Overview”.
If there is information on the Clinical Presentation of a disease, Epidemiology, Etiology, and Risk Factors of a disease. 
It provides information at an overview level of the disease, aiding in understanding and managing the condition.""",
    "current_and_future_treatments": """If the text contains information alluding to "Current and Expected Future treatments”.
Current treatments refer to widely used, scientifically supported methods for managing diseases, including medications, lifestyle changes, and surgeries. 
Expected future treatments are those still under research, showing promising results but not yet approved, such as new drugs, gene therapy, or AI-guided procedures. 
Their availability is unpredictable, as it relies on factors such as clinical trial results, regulatory approval, and production capabilities.""",
    "healthcare_system_hurdles": """If the text contains information alluding to the general "Healthcare systems hurdles and needs". 
If there is information on "Financial burden", "Patient-HCP dialogue", "Patient support needs relating to patient-HCP dialogue", and "Policy issues", 
where "Financial Burden" pertains to the patient's monetary strain due to healthcare needs, both direct and indirect. 
"Patient-HCP Dialogue" involves the communication between the patient and their healthcare provider influencing treatment decisions and patient understanding. 
"Patient Support Needs Related to Patient-HCP Dialogue" focuses on improving patient-provider communication. 
"Policy Issues" refers to local, regional, or national policies that can impact patient care, including insurance schemes, treatment approvals, or data management policies.""",
}

# Concept Sheet default labels
DEFAULT_LABELS_DESCRIPTIONS_DICT = {
    "Trial Summary": """If the text contains information with heading “Trial Summary”.""",
    "Trial Objectives": """If the text contains information with heading “Trial Objectives”.
Objectives are also divided into primary and secondary endpoints represent the outcomes of the trial is designed to measure.""",
    "Treatment Plan": """If the text contains information with heading “Treatment Plan”.""",
    "Patient Population": """If the text contains information with heading “Patient Population”.""",
}

EXTRACT_TEMPLATE_PREFIX = """Here is the content of the section:
----------------
{context_str}
----------------
**Description of categories to classify:**
"""

EXTRACT_TEMPLATE_SUFFIX = """\n
Given the contextual information, utilize the descriptions provided above to accurately classify the category of the text.\
The categories could be multi-label and can be in a list of strings (categories). \
Finally, extract out a {class_name} object:"""

NOISE = {"Noise"}  # Noise label set for validation


class NodeCategoryExtractor:
    """
    TextNode Category extractor. TextNode-level extractor.

    Wrapper over pydantic program extractor
    Extracts `category` metadata field.

    Args:
        llm (Optional[LLM]): LLM
        labels_descriptions_dict (dict): node category labels and associated descriptions
    """

    llm: LLMPredictorType = Field(description="The LLM to use for generation.")
    labels_descriptions_dict: dict = Field(
        default=DEFAULT_LABELS_DESCRIPTIONS_DICT,
        description="Dict of labels as keys and associated descriptions",
    )

    def __init__(
        self,
        llm: Optional[LLM] = None,
        labels_descriptions_dict: dict = DEFAULT_LABELS_DESCRIPTIONS_DICT,
        num_workers: int = config["num_workers"],
    ) -> None:
        """Init params."""

        self.llm = llm
        self.labels_descriptions_dict = labels_descriptions_dict
        self.num_workers = num_workers

    @classmethod
    def class_name(cls) -> str:
        return "NodeCategoryExtractor"

    def _get_labels_descriptions_str(self, labels_descriptions_dict: dict) -> str:
        labels_descriptions = ""
        for label, description in sorted(labels_descriptions_dict.items()):
            labels_descriptions += f'\n"{label}": {description}\n'
        return labels_descriptions

    def get_extractor(
        self,
        labels_descriptions_dict: Optional[dict] = None,
    ) -> PydanticProgramExtractor:
        """Dynamic Extractor (constructed based on the passed labels & descriptions)

        Args:
            labels_descriptions_dict (Optional[dict], optional): TextNode category labels and associated descriptions. Defaults to None.

        Returns:
            PydanticProgramExtractor: Extracts TextNode Category
        """
        if labels_descriptions_dict is None:
            labels_descriptions_dict = DEFAULT_LABELS_DESCRIPTIONS_DICT

        class NodeMetadata(BaseModel):
            """TextNode metadata Model"""

            category: List[str] = Field(
                ...,
                description=(
                    f"Categories of chunk among: {sorted(list(labels_descriptions_dict.keys()))}"
                ),
            )

        extract_template_str = (
            EXTRACT_TEMPLATE_PREFIX
            + self._get_labels_descriptions_str(labels_descriptions_dict)
            + EXTRACT_TEMPLATE_SUFFIX
        )

        openai_program = OpenAIPydanticProgram.from_defaults(
            llm=llm,
            output_cls=NodeMetadata,
            prompt_template_str="{input}",
        )

        category_extractor = PydanticProgramExtractor(
            program=openai_program,
            input_key="input",
            show_progress=config["show_progress"],
            num_workers=self.num_workers,
            extract_template_str=extract_template_str,
        )
        return category_extractor
