from fastapi import APIRouter, Depends

from ..ai import analyze
from ..auth import require_role
from ..schemas import AnalysisRequest

router = APIRouter()


@router.post("/api/analyze-incident")
async def analyze_incident(body: AnalysisRequest, session=Depends(require_role("CITIZEN"))):
    result, source = await analyze(body.imageBase64, body.description)
    return {"analysis": result, "source": source}
