from cerebrium.models.base import BaseModel
from typing import Dict, List, Union


class HFPipeline(BaseModel):
    def predict(self, input: Union[Dict, List]) -> list:
        if isinstance(input, dict):
            print("input: ", input)
            data = input["data"]
            params = input.get("parameters", {})
        else:
            data = input
            params = {}
        res = self.model(data, **params)
        return res
