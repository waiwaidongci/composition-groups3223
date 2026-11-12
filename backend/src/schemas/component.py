from pydantic import BaseModel
class ComponentOutput(BaseModel):
    id:int
    study_id:int
    code:str
    label:str
    unit:str
    position:int
    meaning:str
