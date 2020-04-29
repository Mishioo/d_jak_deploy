import sqlite3 as sql
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from ..models import Track, Album, NewAlbumRequest

router = APIRouter()
router.db_connection = None


@router.on_event("startup")
async def startup():
    router.db_connection = sql.connect('arewedancer/chinook.db')


@router.on_event("shutdown")
async def shutdown():
    router.db_connection.close()


async def get_db():
    factory = router.db_connection.row_factory
    router.db_connection.row_factory = sql.Row
    try:
        yield router.db_connection
    finally:
        router.db_connection. row_factory = factory


@router.get("/tracks", response_model=List[Track])
async def tracks(
        page: int = 0, per_page: int = 10, db: sql.Connection = Depends(get_db)
):
    data = db.execute(
        "SELECT trackid, name, albumid, mediatypeid, genreid, composer, milliseconds, "
        "bytes, unitprice FROM tracks ORDER BY trackid LIMIT ? OFFSET ?;",
        (per_page, page * per_page)
    ).fetchall()
    return data


@router.get(
    "/tracks/composers/",
    response_model=List[str],
)
async def composers_tracks(composer_name: str, db: sql.Connection = Depends(get_db)):
    db.row_factory = lambda c, x: x[0]
    data = db.execute(
        "SELECT name FROM tracks WHERE composer = ? ORDER BY name;",
        (composer_name, )
    ).fetchall()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": f"No such composer: {composer_name}"},
        )
    else:
        return data


@router.post("/albums", status_code=status.HTTP_201_CREATED, response_model=Album)
async def new_album(album: NewAlbumRequest, db: sql.Connection = Depends(get_db)):
    artist = db.execute(
        "SELECT name FROM artists WHERE artistid = ?", (album.artist_id, )
    ).fetchone()
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"error": f"No artist with this Id: {album.artist_id}"}},
        )
    cursor = db.execute(
        "INSERT INTO albums (title, artistid) VALUES (?, ?)",
        (album.title, album.artist_id),
    )
    db.commit()
    album = db.execute(
        "SELECT albumid, title, artistid FROM albums WHERE albumid = ?",
        (cursor.lastrowid, )
    ).fetchone()
    return album


@router.get("/albums/{album_id}", response_model=Album)
async def gat_album_by_id(album_id: int, db: sql.Connection = Depends(get_db)):
    album = db.execute(
        "SELECT albumid, title, artistid FROM albums WHERE albumid = ?",
        (album_id, ),
    ).fetchone()
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"error": f"No album with this Id: {album_id}"}},
        )
    return album
