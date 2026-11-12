from typing import Annotated
from pydantic import BaseModel,Field,ConfigDict,field_validator
StrictRatio=Annotated[float,Field(strict=True,allow_inf_nan=False)]
class ComparisonInput(BaseModel):
    model_config=ConfigDict(extra="forbid")
    name:str=Field(min_length=2,max_length=160)
    study_id:int
    ratios:list[StrictRatio]=Field(min_length=2,max_length=8)
    permutations:int=Field(default=199,ge=199,le=999,strict=True)
    seed:int=Field(default=2026,ge=0,le=2147483647,strict=True)
    @field_validator("ratios")
    @classmethod
    def ratios_are_distinct_probabilities(cls,values):
        if any(isinstance(value,bool) or not 0<value<1 for value in values):raise ValueError("每个零替换比例须为(0,1)有限数")
        if len(set(values))!=len(values):raise ValueError("零替换比例不能重复")
        return [float(value) for value in values]
