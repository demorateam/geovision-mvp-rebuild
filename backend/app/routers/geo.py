from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response as RawResponse

from ..auth import require_auth
from ..neshan import reverse as neshan_reverse, search as neshan_search, static_map

router = APIRouter()


@router.get("/api/geocode")
async def geocode(lat: float, lng: float, session=Depends(require_auth)):
    if not -90 <= lat <= 90 or not -180 <= lng <= 180:
        raise HTTPException(400, "مختصات نامعتبر")
    return await neshan_reverse(lat, lng)


@router.get("/api/search-location")
async def search_location(term: str, lat: float | None = None, lng: float | None = None, session=Depends(require_auth)):
    if len(term) < 2:
        raise HTTPException(400, "عبارت جستجو حداقل ۲ کاراکتر")
    return await neshan_search(term, lat, lng)


@router.get("/api/map")
async def map_image(lat: float, lng: float, zoom: int = 13, session=Depends(require_auth)):
    content, media_type = await static_map(lat, lng, zoom)
    return RawResponse(content, media_type=media_type, headers={"Cache-Control": "private, max-age=300"})
