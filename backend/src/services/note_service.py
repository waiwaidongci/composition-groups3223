from fastapi import HTTPException
from ..models import CompositionRun,ResampleNote
from ..utils.serialize import record
from .audit_service import log

def list_notes(db):return [record(n) for n in db.query(ResampleNote).order_by(ResampleNote.id.desc())]
def create_note(db,data,user):
    run=db.get(CompositionRun,data.run_id)
    if not run or run.status!="completed":raise HTTPException(409,"只能对已完成组成研究提交补样建议")
    row=ResampleNote(**data.model_dump(),owner=user.name,status="submitted")
    db.add(row);db.flush();log(db,user.email,"resample.submit",row.id);db.commit();return record(row)
def review_note(db,nid,data,user):
    row=db.get(ResampleNote,nid)
    if not row:raise HTTPException(404,"补样建议不存在")
    if row.status!="submitted":raise HTTPException(409,"已审阅建议不可重复审批")
    row.status=data.status;row.reviewer=user.name;row.review_note=data.review_note
    log(db,user.email,"resample."+data.status,row.id);db.commit();return record(row)
