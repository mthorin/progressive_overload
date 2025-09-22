from fastapi import FastAPI, Body, HTTPException
from starlette.middleware.cors import CORSMiddleware

CORS_CONFIG = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}

app = FastAPI()
app.add_middleware(CORSMiddleware, **CORS_CONFIG)

