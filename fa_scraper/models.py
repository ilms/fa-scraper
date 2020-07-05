from pydantic import BaseModel
from typing import List


class Favorite(BaseModel):
    id: int
    post_id: int
    user: str


class Post(BaseModel):
    id: int
    source: str
    preview_url: str
    content_url: str
    content_type: str
    view_count: int
    fav_count: int
    rating: str
    title: str
    creator: str
    tags: List[str]
