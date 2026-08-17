from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api.deps import get_current_user
from app.core.database import get_db
from app.evaluation.evaluator import evaluate_run

router = APIRouter(prefix="/v1/evaluate", tags=["evaluation"])


@router.post("", response_model=schemas.EvaluateResponse)
def evaluate(
    payload: schemas.EvaluateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    run = db.get(models.Run, payload.run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    if run.status != "completed":
        raise HTTPException(status_code=409, detail=f"Run is not completed (status={run.status})")

    result = evaluate_run(run, payload.criteria)
    return schemas.EvaluateResponse(run_id=run.id, scores=result["scores"], rationale=result["rationale"])
