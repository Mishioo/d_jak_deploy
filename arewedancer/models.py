from typing import Optional

from pydantic import BaseModel


class Patient(BaseModel):
    name: str
    surname: str


class Track(BaseModel):
    TrackId: int
    Name: str
    AlbumId: Optional[int]
    MediaTypeId: int
    GenreId: Optional[int]
    Composer: Optional[str]
    Milliseconds: int
    Bytes: Optional[int]
    UnitPrice: float


class NewAlbumRequest(BaseModel):
    title: str
    artist_id: int


class Album(BaseModel):
    AlbumId: int
    Title: str
    ArtistId: int
