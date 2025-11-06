from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class LogoStyle(str, Enum):
    MINIMAL = "minimal"
    MODERN = "modern"
    VINTAGE = "vintage"
    PLAYFUL = "playful"
    PROFESSIONAL = "professional"
    ABSTRACT = "abstract"
    GEOMETRIC = "geometric"
    HAND_DRAWN = "hand_drawn"
    MASCOT = "mascot"
    LETTERMARK = "lettermark"

class ColorScheme(str, Enum):
    MONOCHROME = "monochrome"
    COLORFUL = "colorful"
    PASTEL = "pastel"
    BOLD = "bold"
    EARTH_TONES = "earth_tones"
    METALLIC = "metallic"
    GRADIENT = "gradient"

class TargetAudience(str, Enum):
    CHILDREN = "children"
    YOUNG_ADULTS = "young_adults"
    PROFESSIONALS = "professionals"
    LUXURY = "luxury"
    GENERAL = "general"
    TECHNICAL = "technical"
    SENIORS = "seniors"

class UsageContext(str, Enum):
    ALL_PURPOSE = "all_purpose"
    DIGITAL_PRIMARY = "digital_primary"
    PRINT_PRIMARY = "print_primary"
    SOCIAL_MEDIA = "social_media"
    MERCHANDISE = "merchandise"

class LogoRequest(BaseModel):
    brand_name: str = Field(..., min_length=1, max_length=50)
    slogan: Optional[str] = Field(None, max_length=100)
    style: LogoStyle
    color_scheme: ColorScheme
    industry: Optional[str] = Field(None, max_length=50)
    target_audience: TargetAudience = Field(..., description="Primary target audience for the brand")
    usage_context: UsageContext = Field(..., description="Primary usage context for the logo")
    preferred_symbols: Optional[List[str]] = Field(None, max_length=5, description="List of symbols or imagery to incorporate")
    avoid_elements: Optional[List[str]] = Field(None, max_length=5, description="Elements or symbols to explicitly avoid")
    brand_values: Optional[List[str]] = Field(None, max_length=5, description="Core brand values to convey")
    competitor_differentiation: Optional[str] = Field(None, max_length=200, description="How to differentiate from competitors")
    additional_notes: Optional[str] = Field(None, max_length=500)
    font_style: Optional[str] = Field(None, max_length=50, description="Preferred font style (e.g., serif, sans-serif, script)")
    maintain_simplicity: bool = Field(default=True, description="Prioritize simplicity for better scalability")

class LogoResponse(BaseModel):
    logo_url: str
    preview_url: str
    generation_id: str 