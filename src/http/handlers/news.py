from fastapi import APIRouter, Depends
from pydantic import PositiveInt
from src.domain.news import NewsEntry
from src.constants import TAGS

from .stubs import NewsRepo, StubNewsRepo

router = APIRouter()


@router.get("/{tag}/news", response_model=list[NewsEntry])
async def get_news_by_tag(
    tag: TAGS,
    day: PositiveInt,
    news_repo: NewsRepo = Depends(StubNewsRepo),
):
    return await news_repo.get_by_tag(tag, day)
