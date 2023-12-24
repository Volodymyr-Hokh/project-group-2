"""
This module contains the main FastAPI application.

It sets up the FastAPI app, configures middleware, includes routers, and handles exceptions.

Example:
    To run the application, execute the following command:
        uvicorn main:app --reload

Attributes:
    app (FastAPI): The FastAPI application instance.

"""

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.limiter import limiter
from src.routes import auth, users, images, transformations, comments
from src.views import test

load_dotenv()

app = FastAPI(
    docs_url="/swagger",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.mount(
    "/_static", StaticFiles(directory="./docs/_build/html/_static/"), name="_static"
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/docs", include_in_schema=False)
async def get_documentation():
    """
    Retrieves the documentation.

    Returns:
        FileResponse: The Swagger documentation.

    """
    return FileResponse(Path("./docs/_build/html/index.html"), media_type="text/html")


@app.get("/view-source", include_in_schema=False)
async def view_source():
    source_file_path = Path("./docs/_build/html/_sources/index.rst.txt")
    return FileResponse(source_file_path)


app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(images.router, prefix="/api")
app.include_router(transformations.router, prefix="/api")
app.include_router(comments.router, prefix="/api")

app.include_router(test.router)
