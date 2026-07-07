from fastapi import FastAPI , Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from routers import user , current_user , notification
from contextlib import asynccontextmanager
from scheduler import schedule

@asynccontextmanager
async def lifespan(app: FastAPI):
    schedule.start_scheduler()
    yield
    schedule.scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

app.include_router(user.router)
app.include_router(current_user.router)
app.include_router(notification.router)