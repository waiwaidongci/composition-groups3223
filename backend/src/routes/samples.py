from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from ..config.database import get_db
from ..controllers.dependencies import current_user,roles
from ..constants.roles import Role
from ..schemas.sample import SampleOutput,SampleAnnotation
from ..services.sample_service import list_samples,annotate
router=APIRouter(tags=['samples'])
@router.get('/studies/{sid}/samples',response_model=list[SampleOutput])
def index(sid:int,db:Session=Depends(get_db),user=Depends(current_user)):return list_samples(db,sid)
@router.patch('/samples/{sid}')
def update(sid:int,data:SampleAnnotation,db:Session=Depends(get_db),user=Depends(roles(Role.ADMIN,Role.ANALYST))):return annotate(db,sid,data,user)
