from pydantic import BaseModel,Field
class SampleOutput(BaseModel):
    id:int
    study_id:int
    code:str
    group:str
    values:dict
    note:str
    zero_count:int
class SampleAnnotation(BaseModel):
    note:str=Field(min_length=8,max_length=1500)
