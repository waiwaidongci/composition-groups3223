from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from ..config.database import get_db
from ..controllers.dependencies import current_user,roles
from ..constants.roles import Role
from ..schemas.comparison import ComparisonInput
from ..services.comparison_service import list_comparisons,detail,create_comparison,retry_comparison
router=APIRouter(prefix="/comparisons",tags=["comparisons"])
@router.get("")
def index(db:Session=Depends(get_db),user=Depends(current_user)):return list_comparisons(db)
@router.get("/{cid}")
def show(cid:int,db:Session=Depends(get_db),user=Depends(current_user)):return detail(db,cid)
@router.post("",status_code=202)
def create(data:ComparisonInput,db:Session=Depends(get_db),user=Depends(roles(Role.ADMIN,Role.ANALYST))):return create_comparison(db,data,user)
@router.post("/{cid}/retry",status_code=202)
def retry(cid:int,db:Session=Depends(get_db),user=Depends(roles(Role.ADMIN,Role.ANALYST))):return retry_comparison(db,cid,user)
