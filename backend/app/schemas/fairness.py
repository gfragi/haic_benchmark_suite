from pydantic import BaseModel
from typing import List, Dict
from pydantic import BaseModel, field_validator, model_validator


class FairnessInput(BaseModel):
    predictions: List[int]
    labels: List[int]
    sensitive_features: Dict[str, List[str]]

    @model_validator(mode="after")
    def check_lengths(self):
        preds = self.predictions
        labels = self.labels
        features = self.sensitive_features
        if not (len(preds) == len(labels) == len(next(iter(features.values())))):
            raise ValueError("All input arrays must have the same length.")
        return self