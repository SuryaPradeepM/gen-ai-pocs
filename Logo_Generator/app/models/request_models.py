from typing import Optional

from pydantic import BaseModel


class LogoRequest(BaseModel):
    company_name: str
    industry: str
    style: str
    colors: str
    additional_details: Optional[str] = None
