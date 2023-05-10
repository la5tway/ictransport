from fastapi import APIRouter, Depends, Response
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncConnection

from .stubs import StubAsyncConnection

router = APIRouter()


@router.get("/health-check", include_in_schema=False)
async def health_check(
    conn: AsyncConnection = Depends(StubAsyncConnection),
):
    try:
        (await conn.scalars(text("SELECT version()"))).one()
    except SQLAlchemyError:
        return Response(status_code=500)
    return Response(status_code=204)
