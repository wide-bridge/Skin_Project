from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class DiagnosisRequest(BaseModel):
    image_path: str | None = Field(default=None, description="Local image path for phase 04 placeholder inference")
    upload_filename: str | None = Field(default=None, description="Reserved field for future upload-based inference")

    @model_validator(mode="after")
    def validate_source(self) -> "DiagnosisRequest":
        if not self.image_path and not self.upload_filename:
            raise ValueError("Either image_path or upload_filename must be provided")
        return self


class DiagnosisResponse(BaseModel):
    predicted_disease: str = Field(default="unknown")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    differentials: list[str] = Field(default_factory=list)
    needs_human_review: bool = True
    summary: str = Field(default="Placeholder diagnosis response")
