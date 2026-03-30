from fastapi import FastAPI
from app.database import engine
from app.seed import seed_dev_data

app = FastAPI()
seed_dev_data()

@app.get("/")
async def root():
    return {"message": "Hello World"}