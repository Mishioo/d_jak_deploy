import sqlite3 as sql
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from ..models import (
    Track,
    Album,
    NewAlbumRequest,
    Customer,
    CustomerUpdateRequest,
    CustomerExpense,
    GenreSales,
)

router = APIRouter()
router.db_connection = None


@router.on_event("startup")
async def startup():
    router.db_connection = sql.connect("arewedancer/chinook.db")


@router.on_event("shutdown")
async def shutdown():
    router.db_connection.close()


async def get_db():
    factory = router.db_connection.row_factory
    router.db_connection.row_factory = sql.Row
    try:
        yield router.db_connection
    finally:
        router.db_connection.row_factory = factory


@router.get("/tracks", response_model=List[Track])
async def tracks(
    page: int = 0, per_page: int = 10, db: sql.Connection = Depends(get_db)
):
    data = db.execute(
        "SELECT trackid, name, albumid, mediatypeid, genreid, composer, milliseconds, "
        "bytes, unitprice FROM tracks ORDER BY trackid LIMIT ? OFFSET ?;",
        (per_page, page * per_page),
    ).fetchall()
    return data


@router.get(
    "/tracks/composers/", response_model=List[str],
)
async def composers_tracks(composer_name: str, db: sql.Connection = Depends(get_db)):
    db.row_factory = lambda c, x: x[0]
    data = db.execute(
        "SELECT name FROM tracks WHERE composer = ? ORDER BY name;", (composer_name,)
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
        "SELECT name FROM artists WHERE artistid = ?;", (album.artist_id,)
    ).fetchone()
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"error": f"No artist with this Id: {album.artist_id}"}},
        )
    cursor = db.execute(
        "INSERT INTO albums (title, artistid) VALUES (?, ?);",
        (album.title, album.artist_id),
    )
    db.commit()
    album = db.execute(
        "SELECT albumid, title, artistid FROM albums WHERE albumid = ?;",
        (cursor.lastrowid,),
    ).fetchone()
    return album


@router.get("/albums/{album_id}", response_model=Album)
async def gat_album_by_id(album_id: int, db: sql.Connection = Depends(get_db)):
    album = db.execute(
        "SELECT albumid, title, artistid FROM albums WHERE albumid = ?;", (album_id,),
    ).fetchone()
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"error": f"No album with this Id: {album_id}"}},
        )
    return album


@router.put("/customers/{customer_id}", response_model=Customer)
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdateRequest,
    db: sql.Connection = Depends(get_db),
):
    customer = db.execute(
        "SELECT * FROM customers WHERE customerid = ?;", (customer_id,)
    ).fetchone()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"error": f"No customer with this Id: {customer_id}"}},
        )
    customer_data = customer_data.dict(exclude_unset=True)
    command = (
        f"UPDATE customers SET "
        f"{', '.join(f'{key}=:{key}' for key in customer_data)} "
        f"WHERE customerid=:customerid;"
    )
    print(command)
    db.execute(command, dict(customerid=customer_id, **customer_data))
    db.commit()
    updated = {
        key: customer_data[key.lower()]
        for key in customer.keys()
        if key.lower() in customer_data
    }
    return dict(customer, **updated)


def customers_sales(db):
    expences = db.execute(
        "SELECT c.customerid, c.email, c.phone, ROUND(SUM(i.total), 2) as number "
        "FROM customers c "
        "INNER JOIN invoices i "
        "ON c.customerid = i.customerid "
        "GROUP BY c.customerid "
        "ORDER BY number DESC, c.customerid;"
    ).fetchall()
    return [CustomerExpense(**entry).dict(by_alias=False) for entry in expences]


def genres_sales(db):
    genres = db.execute(
        "SELECT g.name, SUM(i.quantity) AS number "
        "FROM tracks t "
        "JOIN invoice_items i ON i.trackid = t.trackid "
        "JOIN genres g ON g.genreid = t.genreid "
        "group by g.genreid "
        "ORDER BY number DESC, g.name;"
    ).fetchall()
    return [GenreSales(**entry).dict(by_alias=False) for entry in genres]


SALES_OPERATIONS = {
    "customers": customers_sales,
    "genres": genres_sales,
}


@router.get("/sales")
async def sales(category: str, db: sql.Connection = Depends(get_db)):
    try:
        return SALES_OPERATIONS[category](db)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"error": f"Unknown category: {category}"}},
        )
