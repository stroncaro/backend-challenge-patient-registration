from typing import Union

from contextlib import asynccontextmanager

import debugpy
from fastapi import FastAPI
from sqlmodel import Session

from db import create_database_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start debugging
    debugpy.listen(("0.0.0.0", 5678))

    create_database_and_tables()
    
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
