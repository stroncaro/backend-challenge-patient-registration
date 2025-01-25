from typing import Union

from contextlib import asynccontextmanager
import os

import debugpy
from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, create_engine, SQLModel

from models.patient import Patient


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start debugging
    debugpy.listen(("0.0.0.0", 5678))

    # Init db connection
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_PORT = os.getenv("MYSQL_PORT")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

    DB_URL = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

    engine = create_engine(DB_URL, echo=True)

    try:
        SQLModel.metadata.create_all(bind=engine)
        print("Tables created successfully.")
    except SQLAlchemyError as e:
        print(f"Error creating tables: {e}")
    
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
