from pydantic import BaseModel,EmailStr
from typing import List


class AnalysisInput(BaseModel):
    email: EmailStr
    seed_keyword: str
    brand: str
    market: str

class PromptResult(BaseModel):
    prompt: str
    brand_found: bool


class VisibilityResult(BaseModel):
    total_prompts: int
    appeared: int
    visibility_percentage: float
    details: List[PromptResult]
