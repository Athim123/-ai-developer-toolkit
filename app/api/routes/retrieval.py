from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import schemas
from app.api.deps import get_current_user
from app.core.database import get_db
from app.retrieval.rag_service import index_document, query_documents

router = APIRouter(prefix="/v1/retrieval", tags=["retrieval"])


class DocumentIndexRequest(BaseModel):
    project_id: str
    title: str
    content: str
    source: str = "manual"


@router.post("/documents", status_code=201)
def add_document(
    payload: DocumentIndexRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    doc = index_document(db, payload.project_id, payload.title, payload.content, payload.source)
    return {"id": doc.id, "title": doc.title}


@router.post("/query", response_model=schemas.RetrievalResponse)
def query(
    payload: schemas.RetrievalQuery,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    scored = query_documents(db, payload.project_id, payload.query, payload.top_k)
    results = [
        schemas.RetrievalResult(
            document_id=doc.id,
            title=doc.title,
            snippet=doc.content[:240],
            score=round(score, 4),
        )
        for doc, score in scored
    ]
    return schemas.RetrievalResponse(query=payload.query, results=results)
