from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import Base, engine
from .routers import tickets
from app.routers import ai




# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Support CRM API",
    description="Customer Support Ticketing CRM System",
    version="1.0.0"
)


# Paths
BASE_DIR = Path(__file__).resolve().parent


# Static files
app.mount(
    "/static",
    StaticFiles(
        directory=BASE_DIR / "static"
    ),
    name="static"
)


# HTML templates
templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)


# Register ticket API
app.include_router(tickets.router)
app.include_router(ai.router)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        }
    )


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "Support CRM is running"
    }