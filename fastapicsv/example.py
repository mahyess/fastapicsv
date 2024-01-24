from typing import List
from pydantic import BaseModel

from fastapi import FastAPI
from fastapicsv.middlewares import CSVMiddleware

app = FastAPI()
app.add_middleware(CSVMiddleware, nested_separator="__")

items = [
    {"id": 1, "name": "First Item", "person": {"firstname": "John", "lastname": "Doe"}},
    {"id": 2, "name": "Second Item", "person": {"firstname": "Jane", "lastname": "Smith"}},
    {"id": 3, "name": "Third Item", "person": {"firstname": "Jack", "lastname": "Jones"}},
]


@app.get("/")
async def get():
    return items


class Item(BaseModel):
    id: int
    name: str


@app.post("/")
async def post(body: List[Item]):
    new_items = [*items, *body]
    return new_items
