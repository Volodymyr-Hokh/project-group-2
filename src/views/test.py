from pathlib import Path

from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from src.services.auth import auth_service


router = APIRouter(tags=["test"], include_in_schema=False)

templates = Jinja2Templates(directory="src/services/templates/Client")


@router.get("/", response_class=HTMLResponse)
async def test(
    request: Request,
    user=Depends(auth_service.get_current_user),
):
    # user = None
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "name": user.username if user else "Not a user"},
    )


@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
