import json,os,traceback
from pathlib import Path
from ..config.database import SessionLocal
from ..models import CompositionRun,SensitivityComparison
from ..constants.status import RunStatus
from .analysis_service import analyze_composition
from .sensitivity_algorithm import compare_ratios
from .audit_service import log
ARTIFACTS=Path(os.environ.get("ARTIFACTS_DIR","/artifacts"))

def _write(name,payload):
    try:
        ARTIFACTS.mkdir(parents=True,exist_ok=True);(ARTIFACTS/name).write_text(json.dumps(payload,ensure_ascii=False))
    except OSError:traceback.print_exc()

def process_run(job_id):
    with SessionLocal() as db:
        run=db.get(CompositionRun,job_id)
        if not run or run.status!=RunStatus.QUEUED:return
        run.status=RunStatus.RUNNING;db.commit()
        try:
            run.result=analyze_composition(run.input_snapshot,run.delta,run.permutations,run.seed);run.status=RunStatus.COMPLETED
            _write(f"run-{run.id}.json",run.result);log(db,"worker","composition.completed",run.id)
        except Exception as e:run.status=RunStatus.FAILED;run.error=str(e);traceback.print_exc()
        db.commit()

def process_comparison(job_id):
    with SessionLocal() as db:
        row=db.get(SensitivityComparison,job_id)
        if not row or row.status!=RunStatus.QUEUED:return
        row.status=RunStatus.RUNNING;db.commit()
        try:
            row.result=compare_ratios(row.input_snapshot,row.deltas,row.permutations,row.seed);row.status=RunStatus.COMPLETED
            _write(f"comparison-{row.id}.json",row.result);log(db,"worker","sensitivity.completed",row.id)
        except Exception as e:row.status=RunStatus.FAILED;row.error=str(e);row.result={};traceback.print_exc()
        db.commit()
