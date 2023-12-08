from fastapi import APIRouter, Request

from src.limiter import limiter

router = APIRouter(prefix="/test", tags=["test"])


@router.get("/")
@limiter.limit(limit_value="10/minute")
async def read_contacts(request: Request):
    return {"message": "Hello World"}
