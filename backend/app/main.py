from fastapi import FastAPI
from app.database import engine
from app.seed import seed_dev_data
from app.routes import users

app = FastAPI()
seed_dev_data()

app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}