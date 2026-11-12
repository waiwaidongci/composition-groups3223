import time
from pathlib import Path
from .config.database import Base,engine
from .services.queue_service import queue,RUN_QUEUE,COMPARISON_QUEUE
from .services.job_service import process_run,process_comparison
Base.metadata.create_all(engine)
HEARTBEAT=Path("/artifacts/heartbeat")
while True:
    try:HEARTBEAT.parent.mkdir(parents=True,exist_ok=True);HEARTBEAT.write_text(str(time.time()))
    except OSError:pass
    job=queue.blpop([RUN_QUEUE,COMPARISON_QUEUE],timeout=2)
    if not job:continue
    key,value=job
    if key==COMPARISON_QUEUE:process_comparison(int(value))
    else:process_run(int(value))
