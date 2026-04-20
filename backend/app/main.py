from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.seed import seed_dev_data
from app.routes import users, job_orders, customers, services

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

seed_dev_data()

app.include_router(users.router)
app.include_router(job_orders.router)
app.include_router(customers.router)
app.include_router(services.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}