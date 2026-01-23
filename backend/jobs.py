import uuid
import time
from threading import Lock

JOBS = {}
LOCK = Lock()


def create_job(total_steps: int) -> str:
    job_id = str(uuid.uuid4())

    with LOCK:
        JOBS[job_id] = {
            "status": "running",
            "progress": 0,
            "total": total_steps,
            "result": None,
            "error": None,
            "created_at": time.time()
        }

    return job_id


def update_job(job_id: str, step_inc: int = 1):
    with LOCK:
        if job_id in JOBS and JOBS[job_id]["status"] == "running":
            JOBS[job_id]["progress"] += step_inc


def finish_job(job_id: str, result: dict):
    with LOCK:
        if job_id in JOBS:
            JOBS[job_id]["status"] = "completed"
            JOBS[job_id]["result"] = result
            JOBS[job_id]["progress"] = JOBS[job_id]["total"]


def fail_job(job_id: str, error: str):
    with LOCK:
        if job_id in JOBS:
            JOBS[job_id]["status"] = "failed"
            JOBS[job_id]["error"] = error


def get_job(job_id: str):
    with LOCK:
        return JOBS.get(job_id)
