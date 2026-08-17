from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api.deps import get_current_user
from app.core.database import get_db
from app.workflows.engine import run_workflow

router = APIRouter(prefix="/v1/runs", tags=["runs"])


@router.post("", response_model=schemas.RunOut, status_code=201)
def create_run(
    payload: schemas.RunCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    prompt_template = None
    if payload.prompt_id:
        prompt = db.get(models.Prompt, payload.prompt_id)
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        prompt_template = prompt.template

    run = models.Run(
        project_id=payload.project_id,
        workflow_name=payload.workflow,
        status="running",
        input_payload=payload.input,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        result = run_workflow(
            db=db,
            run=run,
            prompt_template=prompt_template,
            model=payload.model,
            tool_names=payload.tools,
        )
        run.status = "completed"
        run.output_payload = result["output_payload"]
        run.latency_ms = result["latency_ms"]
        run.end_time = datetime.utcnow()
    except Exception as exc:  # noqa: BLE001
        run.status = "failed"
        run.output_payload = {"error": str(exc)}
        run.end_time = datetime.utcnow()

    db.add(run)
    db.commit()

    return schemas.RunOut(run_id=run.id, status=run.status, trace_url=f"/v1/runs/{run.id}/trace")


@router.get("/{run_id}", response_model=schemas.RunDetail)
def get_run(run_id: str, db: Session = Depends(get_db)):
    run = db.get(models.Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/{run_id}/trace")
def get_run_trace(run_id: str, db: Session = Depends(get_db)):
    run = db.get(models.Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return [
        {"step": e.step, "detail": e.detail, "created_at": e.created_at}
        for e in sorted(run.trace_events, key=lambda e: e.created_at)
    ]
