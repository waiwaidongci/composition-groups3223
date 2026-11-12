from pydantic import BaseModel,Field,ConfigDict
class RunInput(BaseModel):
    model_config=ConfigDict(extra="forbid")
    name:str=Field(min_length=2,max_length=160)
    study_id:int
    delta:float=Field(default=.001,gt=0,lt=1,allow_inf_nan=False,strict=True)
    permutations:int=Field(default=199,ge=199,le=999,strict=True)
    seed:int=Field(default=2026,ge=0,le=2147483647,strict=True)
