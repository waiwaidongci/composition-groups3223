from fastapi import HTTPException
from ..models import CompositionStudy,CompositionSample,ComponentSpec
from ..utils.serialize import record
from .analysis_service import prepare_snapshot

def get_study(db,sid):
    row=db.get(CompositionStudy,sid)
    if not row:raise HTTPException(404,"组成研究不存在")
    return row
def create_snapshot(db,study):return {"study":record(study),"components":[record(c) for c in db.query(ComponentSpec).filter_by(study_id=study.id).order_by(ComponentSpec.position)],"samples":[record(s) for s in db.query(CompositionSample).filter_by(study_id=study.id).order_by(CompositionSample.code)]}
def list_studies(db):
    out=[]
    for s in db.query(CompositionStudy).order_by(CompositionStudy.code):
        snapshot=create_snapshot(db,s);counts={};zero_rows=0
        for row in snapshot['samples']:counts[row['group']]=counts.get(row['group'],0)+1;zero_rows+=any(v==0 for v in row['values'].values())
        supported=True;reason='成分与组规模完整，支持CLR置换研究'
        try:prepare_snapshot(snapshot,s.default_delta)
        except ValueError as e:supported=False;reason=str(e)
        out.append({**record(s),"sample_count":len(snapshot['samples']),"component_count":len(snapshot['components']),"group_counts":counts,"zero_rows":zero_rows,"supported":supported,"reason":reason})
    return out
