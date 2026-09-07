from fastapi import APIRouter, Depends, File, UploadFile

from ..auth import require_role
from ..services.upload_service import save_image

router = APIRouter()


@router.post("/api/upload")
async def upload(file: UploadFile = File(...), session=Depends(require_role("CITIZEN"))):
    return {"url": await save_image(file)}
