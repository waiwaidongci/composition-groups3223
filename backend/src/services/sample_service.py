from fastapi import HTTPException
from ..models import CompositionSample
from ..utils.serialize import record
from .study_service import get_study
from .audit_service import log

def list_samples(db,sid):get_study(db,sid);return [{**record(s),"zero_count":sum(v==0 for v in s.values.values())} for s in db.query(CompositionSample).filter_by(study_id=sid).order_by(CompositionSample.code)]
def annotate(db,sid,data,user):
    row=db.get(CompositionSample,sid)
    if not row:raise HTTPException(404,"组成样本不存在")
    row.note=data.note;log(db,user.email,'sample.annotate',sid);db.commit();return record(row)
