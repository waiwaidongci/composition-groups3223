from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from ..config.database import get_db
from ..controllers.dependencies import current_user,roles
from ..constants.roles import Role
from ..schemas.component import ComponentOutput
from ..services.component_service import list_components
router=APIRouter(tags=['components'])
@router.get('/studies/{sid}/components',response_model=list[ComponentOutput])
def index(sid:int,db:Session=Depends(get_db),user=Depends(current_user)):return list_components(db,sid)
