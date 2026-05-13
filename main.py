from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from login import router as login_router
from signup import router as signup_router # 1. Import it
from tasks import router as task_router
from auth_utils import *
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
app = FastAPI()
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"Validation Error: {exc.errors()}") # This prints to your console
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(login_router)
app.include_router(signup_router) # 2. Include it
app.include_router(task_router)
@app.get("/")
async def load_startup(request: Request):
    user=request.cookies.get("access_token")
    if user is not None:
        return templates.TemplateResponse(
            request,
            "hello.html",
            {"request": request}
        )
    return templates.TemplateResponse(
    request,
    "startup.html",
    {"request": request}
)