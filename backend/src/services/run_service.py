import csv,io
from redis import Redis
from fastapi import HTTPException
from ..models import CompositionRun,ResampleNote
from ..config.settings import REDIS_URL
from ..utils.serialize import record
from .study_service import get_study,create_snapshot
from .analysis_service import prepare_snapshot
from .audit_service import log
queue=Redis.from_url(REDIS_URL,decode_responses=True)
def list_runs(db):return [record(r) for r in db.query(CompositionRun).order_by(CompositionRun.id.desc())]
def get_run(db,rid):
    row=db.get(CompositionRun,rid)
    if not row:raise HTTPException(404,"组成运行不存在")
    return row
def create_run(db,data,user):
    study=get_study(db,data.study_id);snapshot=create_snapshot(db,study)
    try:
        prepare_snapshot(snapshot,data.delta)
        if len(snapshot['samples'])*data.permutations>150000:raise ValueError("样本数×置换数超额")
    except ValueError as e:raise HTTPException(422,str(e))
    row=CompositionRun(**data.model_dump(),input_snapshot=snapshot,owner=user.name);db.add(row);db.flush();log(db,user.email,'composition.enqueue',row.id);db.commit()
    try:queue.rpush('composition:jobs',row.id)
    except Exception:row.status='failed';row.error='队列不可用，请重提';db.commit();raise HTTPException(503,row.error)
    return record(row)
def export_run(db,rid):
    row=get_run(db,rid)
    if row.status!='completed' or not db.query(ResampleNote).filter_by(run_id=rid,status='approved').first():raise HTTPException(403,'仅获批完成研究可导出')
    o=io.StringIO();w=csv.writer(o);stats=row.result['statistics'];w.writerow(['sample','group','component','raw','closed','replaced','CLR','zero_count','delta','R2','pseudo_F','F_status','global_p','B','seed','input_hash'])
    for s in row.result['transformed']:
        for i,c in enumerate(row.result['components']):w.writerow([s['sample']['code'],s['sample']['group'],c['code'],s['raw'][i],s['closed'][i],s['replaced'][i],s['clr'][i],s['zero_count'],row.delta,stats['R2'],stats['F'],stats['F_status'],stats['p'],row.permutations,row.seed,row.result['input_hash']])
    return o.getvalue()
