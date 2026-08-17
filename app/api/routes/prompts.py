from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api.deps import get_current_user
from app.core.database import get_db

router = APIRouter(prefix="/v1/prompts", tags=["prompts"])


@router.post("", response_model=schemas.PromptOut, status_code=201)
def create_or_version_prompt(
    payload: schemas.PromptCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    latest = (
        db.query(models.Prompt)
        .filter(models.Prompt.project_id == payload.project_id, models.Prompt.name == payload.name)
        .order_by(models.Prompt.version.desc())
        .first()
    )
    next_version = (latest.version + 1) if latest else 1

    prompt = models.Prompt(
        project_id=payload.project_id,
        name=payload.name,
        template=payload.template,
        version=next_version,
        created_by=current_user.id,
    )
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return prompt


@router.get("/{prompt_id}", response_model=schemas.PromptOut)
def get_prompt(prompt_id: str, db: Session = Depends(get_db)):
    prompt = db.get(models.Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


@router.get("", response_model=list[schemas.PromptOut])
def list_prompt_versions(project_id: str, name: str, db: Session = Depends(get_db)):
    return (
        db.query(models.Prompt)
        .filter(models.Prompt.project_id == project_id, models.Prompt.name == name)
        .order_by(models.Prompt.version.asc())
        .all()
    )
