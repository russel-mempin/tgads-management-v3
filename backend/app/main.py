from fastapi import FastAPI
from sqlmodel import Session, SQLModel
from app.database import engine
from app import models

app = FastAPI()

with Session(engine) as session:
    SQLModel.metadata.create_all(engine)

@app.get("/")
async def root():
    return {"message": "Hello World"}