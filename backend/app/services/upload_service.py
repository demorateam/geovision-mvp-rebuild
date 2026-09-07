from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from ..config import settings

ALLOWED_EXTENSIONS = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/heic": ".heic", "image/heif": ".heif"}
MAX_SIZE = 15 * 1024 * 1024


async def save_image(file: UploadFile) -> str:
    """Validates and stores an uploaded image, returning its public URL."""
    ext = ALLOWED_EXTENSIONS.get((file.content_type or "").lower())
    if not ext:
        raise HTTPException(400, "فقط تصاویر JPG، PNG، WEBP، HEIC و HEIF مجاز هستند")
    data = await file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(400, "حجم فایل نباید بیشتر از ۱۵ مگابایت باشد")
    filename = f"{int(datetime.utcnow().timestamp() * 1000)}-{uuid4().hex}{ext}"
    path = Path(settings.upload_dir) / filename
    path.write_bytes(data)
    return f"/uploads/{filename}"
