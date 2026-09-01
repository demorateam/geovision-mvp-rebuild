import httpx
from .config import settings

BASE="https://api.neshan.org"

def mock_search(term):
    items=[
        {"title":f"{term} - میدان آزادی","location":{"x":51.3235,"y":35.7248},"neighbourhood":"آزادی","address":"تهران، میدان آزادی"},
        {"title":f"{term} - میدان ولیعصر","location":{"x":51.4082,"y":35.7117},"neighbourhood":"ولیعصر","address":"تهران، میدان ولیعصر"},
        {"title":f"{term} - میدان انقلاب","location":{"x":51.3915,"y":35.7009},"neighbourhood":"انقلاب","address":"تهران، میدان انقلاب"},
        {"title":f"{term} - میدان تجریش","location":{"x":51.4344,"y":35.8042},"neighbourhood":"تجریش","address":"تهران، میدان تجریش"},
        {"title":f"{term} - میدان امام حسین","location":{"x":51.4381,"y":35.7011},"neighbourhood":"امام حسین","address":"تهران، میدان امام حسین"}]
    return {"count":len(items),"items":items}

async def search(term, lat=None, lng=None):
    if not settings.neshan_api_key or settings.neshan_api_key.startswith("your_"): return mock_search(term)
    params={"term":term}
    if lat is not None and lng is not None: params.update(lat=lat,lng=lng)
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r=await c.get(f"{BASE}/v1/search",params=params,headers={"Api-Key":settings.neshan_api_key})
            r.raise_for_status(); return r.json()
    except Exception: return mock_search(term)

async def reverse(lat,lng):
    if not settings.neshan_api_key or settings.neshan_api_key.startswith("your_"):
        return {"formatted_address":f"نزدیک مختصات {lat:.4f}, {lng:.4f}","city":"تهران","state":"تهران","municipality_zone":None}
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r=await c.get(f"{BASE}/v5/reverse",params={"lat":lat,"lng":lng},headers={"Api-Key":settings.neshan_api_key})
            r.raise_for_status(); return r.json()
    except Exception:
        return {"formatted_address":f"نزدیک مختصات {lat:.4f}, {lng:.4f}","city":"تهران","state":"تهران","municipality_zone":None}

def map_url(lat,lng,zoom=13):
    return f"{BASE}/static/v1/maps?center={lat},{lng}&zoom={zoom}&width=600&height=400&api-key={settings.neshan_api_key}"
