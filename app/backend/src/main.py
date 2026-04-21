from fastapi import FastAPI

from src.routers import books, health, recommend

app = FastAPI(
    title="Book Recommender API",
    description="Inference API for the Book Recommender service",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(books.router)
app.include_router(recommend.router)
