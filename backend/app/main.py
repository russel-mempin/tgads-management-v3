from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.routes import users, job_orders, customers, services, expenses, sales
import os

app = FastAPI()

# Read allowed origins from env, fallback to localhost for dev
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.getenv("APP_ENV") == "test" or os.getenv("APP_ENV") == "dev":
    from app.seed import seed_dev_data
    seed_dev_data()

elif os.getenv("APP_ENV") == "prod":
    from app.seed import seed_prod_data
    seed_prod_data()

app.include_router(users.router)
app.include_router(job_orders.router)
app.include_router(customers.router)
app.include_router(services.router)
app.include_router(expenses.router)
app.include_router(sales.router)