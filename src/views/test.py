from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse


router = APIRouter(tags=["test"], include_in_schema=False)

templates = Jinja2Templates(directory="src/services/templates/Client")


@router.get("/", response_class=HTMLResponse)
async def test(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "name": "John"}
    )
