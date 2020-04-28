import sqlite3 as sql
from typing import List

from fastapi import APIRouter

from ..models import Track


router = APIRouter()
router.db_connection = None


@router.on_event("startup")
async def startup():
    router.db_connection = sql.connect('arewedancer/chinook.db')


@router.on_event("shutdown")
async def shutdown():
    router.db_connection.close()


@router.get("/tracks", response_model=List[Track])
async def tracks(page: int = 0, per_page: int = 10):
    router.db_connection.row_factory = sql.Row
    cursor = router.db_connection.cursor()
    data = cursor.execute(
        "SELECT trackid, name, albumid, mediatypeid, genreid, composer, milliseconds, "
        "bytes, unitprice FROM tracks ORDER BY trackid LIMIT ? OFFSET ?;",
        (per_page, page * per_page)
    ).fetchall()
    return data
