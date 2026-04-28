import re

from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator

router = APIRouter(prefix="/recommend", tags=["recommend"])

_MAX_TITLE_LENGTH = 200
# Allow Unicode letters/digits/whitespace and common book-title punctuation.
# Blocks characters used for HTML/template/shell injection: < > { } \ ` | ; null bytes.
_ALLOWED_TITLE_RE = re.compile(r"^[\w\s'\-\.,!?:&()\[\]#/"'"'"]+$", re.UNICODE)


class RecommendRequest(BaseModel):
    book_title: str = Field(
        ...,
        min_length=1,
        max_length=_MAX_TITLE_LENGTH,
        examples=["The Hunger Games"],
    )
    n_recommendations: int = Field(default=5, ge=1, le=20)

    @field_validator("book_title", mode="before")
    @classmethod
    def sanitize_book_title(cls, v: object) -> str:
        if not isinstance(v, str):
            raise ValueError("book_title must be a string")
        v = v.strip()
        if not v:
            raise ValueError("book_title must not be blank")
        if len(v) > _MAX_TITLE_LENGTH:
            raise ValueError(
                f"book_title must be at most {_MAX_TITLE_LENGTH} characters"
            )
        if not _ALLOWED_TITLE_RE.match(v):
            raise ValueError("book_title contains invalid characters")
        return v


class RecommendedBook(BaseModel):
    title: str
    author: str
    score: float = Field(..., ge=0.0, le=1.0)


class RecommendResponse(BaseModel):
    recommendations: list[RecommendedBook]


# Stub response — real model inference will be wired in issue #9
_STUB_RECOMMENDATIONS: list[RecommendedBook] = [
    RecommendedBook(title="Catching Fire", author="Suzanne Collins", score=0.97),
    RecommendedBook(title="Mockingjay", author="Suzanne Collins", score=0.95),
    RecommendedBook(title="Divergent", author="Veronica Roth", score=0.88),
    RecommendedBook(title="The Maze Runner", author="James Dashner", score=0.85),
    RecommendedBook(title="Ender's Game", author="Orson Scott Card", score=0.82),
]


@router.post("", response_model=RecommendResponse)
def recommend_books(request: RecommendRequest) -> RecommendResponse:
    """
    Return book recommendations for a given title.
    Currently returns stub data; model integration tracked in issue #9.
    """
    return RecommendResponse(
        recommendations=_STUB_RECOMMENDATIONS[: request.n_recommendations]
    )
