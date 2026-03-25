from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.init_db import init_db
from app.api import excel
from app.api import audio
from app.api import insights
from app.api import household
import logging

app = FastAPI()

origins = [
    "http://localhost:5173", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],   # allow all HTTP methods
    allow_headers=["*"],   # allow all headers
)

logging.basicConfig(level=logging.DEBUG)

app.include_router(excel.router)
app.include_router(audio.router)
app.include_router(insights.router)
app.include_router(household.router)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def root():
    return {"message": "Backend running"}