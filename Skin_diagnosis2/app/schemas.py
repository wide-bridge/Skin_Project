from typing import List, Literal, Optional

from pydantic import BaseModel


Route = Literal["makeup", "medical", "hybrid"]


class PredictionItem(BaseModel):
    label: str
    confidence: float


class DiagnosisResult(BaseModel):
    label: str
    confidence: float
    top_predictions: List[PredictionItem]
    margin: float
    uncertainty: str
    notice: str


class ChatResponse(BaseModel):
    mode: str
    route: Route
    answer: str
    diagnosis: Optional[DiagnosisResult] = None
    suggestions: List[str]

