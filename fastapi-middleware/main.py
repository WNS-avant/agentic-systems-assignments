from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print("---- Incoming Request ----")
    print(f"Method: {request.method}")
    print(f"Path: {request.url.path}")
    print("Processing request...")

    response = await call_next(request)

    print("Response returned")
    print("--------------------------")

    return response

@app.get("/")
async def home():
    return {"message": "FastAPI server is running"}

@app.get("/hello")
async def hello():
    return {"message": "Hello, Welcome to FastAPI!"}

@app.exception_handler(StarletteHTTPException)
async def custom_404_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={"message": "The requested resource was not found"},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )