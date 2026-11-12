from fastapi import HTTPException
from ..models import SensitivityComparison
from ..utils.serialize import record
from .study_service import get_study,create_snapshot
from .sensitivity_algorithm import validate_ratios,validate_comparison_snapshot,compare_ratios
from .queue_service import queue,COMPARISON_QUEUE
from .audit_service import log

BLOCKING_STATUSES=("queued","running","failed")

def _successor_ids(db):
    return {row.retry_of for row in db.query(SensitivityComparison).filter(SensitivityComparison.retry_of.isnot(None))}
def _summary(row,successors):
    result=row.result or {}
    data={"id":row.id,"name":row.name,"study_id":row.study_id,"study_code":row.input_snapshot.get("study",{}).get("code",""),
        "ratios":[float(x) for x in row.deltas],"permutations":row.permutations,"seed":row.seed,"status":row.status,"error":row.error,
        "retry_of":row.retry_of,"owner":row.owner,"created_at":row.created_at,"published":row.status=="completed" and bool(result),
        "blocking":row.status in BLOCKING_STATUSES and row.id not in successors}
    if data["published"]:
        data["frozen"]=result.get("frozen",{});data["summary"]=result.get("summary",{})
        data["input_hash"]=result.get("input_hash","");data["permutation"]=result.get("permutation",{})
    return data
def list_comparisons(db):
    successors=_successor_ids(db)
    return [_summary(row,successors) for row in db.query(SensitivityComparison).order_by(SensitivityComparison.id.desc())]
def get_comparison(db,cid):
    row=db.get(SensitivityComparison,cid)
    if not row:raise HTTPException(404,"敏感性比较不存在")
    return row
def detail(db,cid):
    row=get_comparison(db,cid);successors=_successor_ids(db);data=record(row)
    data["published"]=row.status=="completed" and bool(row.result)
    data["blocking"]=row.status in BLOCKING_STATUSES and row.id not in successors
    data["study_code"]=row.input_snapshot.get("study",{}).get("code","")
    data.pop("input_snapshot",None)
    return data
def _validate(snapshot,ratios,permutations):
    try:return validate_comparison_snapshot(snapshot,ratios,permutations)
    except ValueError as e:raise HTTPException(422,str(e))
def _enqueue(db,row):
    db.commit()
    try:queue.rpush(COMPARISON_QUEUE,row.id)
    except Exception:
        row.status="failed";row.error="队列不可用，请重试";db.commit();raise HTTPException(503,row.error)
def create_comparison(db,data,user):
    study=get_study(db,data.study_id);snapshot=create_snapshot(db,study)
    ratios=_validate(snapshot,data.ratios,data.permutations)
    row=SensitivityComparison(name=data.name,study_id=study.id,deltas=ratios,permutations=data.permutations,seed=data.seed,input_snapshot=snapshot,owner=user.name)
    db.add(row);db.flush();log(db,user.email,"sensitivity.enqueue",row.id);_enqueue(db,row)
    return _summary(row,_successor_ids(db))
def retry_comparison(db,cid,user):
    row=get_comparison(db,cid)
    if row.status!="failed":raise HTTPException(409,"只有失败的敏感性比较需要重试")
    retry=SensitivityComparison(name=row.name,study_id=row.study_id,deltas=row.deltas,permutations=row.permutations,seed=row.seed,owner=user.name,retry_of=row.id,
        input_snapshot=row.input_snapshot)
    db.add(retry);db.flush();log(db,user.email,"sensitivity.retry",retry.id);_enqueue(db,retry)
    return _summary(retry,_successor_ids(db))
def comparison_block_reason(db,study_id):
    successors=_successor_ids(db)
    rows=[row for row in db.query(SensitivityComparison).filter_by(study_id=study_id).all()
          if row.status in BLOCKING_STATUSES and row.id not in successors]
    if not rows:return ""
    labels=[f"#{row.id} {row.status}" for row in rows]
    return "该研究存在未完成的敏感性比较（"+"、".join(labels)+"），整组比较尚未发布，暂不开放补样审批或导出；失败比较请重试后再审阅。"
