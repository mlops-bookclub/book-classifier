from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/books", tags=["books"])


class Book(BaseModel):
    title: str
    author: str


class BooksResponse(BaseModel):
    books: list[Book]


@router.get("", response_model=BooksResponse)
def list_books() -> BooksResponse:
    """Return available books. Will be populated once data pipeline is connected."""
    return BooksResponse(books=[])
