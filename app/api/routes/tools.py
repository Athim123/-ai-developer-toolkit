from fastapi import APIRouter, Depends, HTTPException

from app import schemas
from app.api.deps import get_current_user
from app.tools.registry import execute_tool, list_tool_schemas

router = APIRouter(prefix="/v1/tools", tags=["tools"])


@router.get("")
def list_tools():
    return list_tool_schemas()


@router.post("/execute", response_model=schemas.ToolExecuteResponse)
def execute(payload: schemas.ToolExecuteRequest, current_user=Depends(get_current_user)):
    try:
        result = execute_tool(payload.tool_name, payload.arguments)
        return schemas.ToolExecuteResponse(tool_name=payload.tool_name, result=result, success=True)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        return schemas.ToolExecuteResponse(tool_name=payload.tool_name, result={"error": str(exc)}, success=False)
