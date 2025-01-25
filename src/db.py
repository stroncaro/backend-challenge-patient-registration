import os

from sqlmodel import SQLModel, create_engine
from sqlalchemy.exc import SQLAlchemyError

from models.patient import Patient

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
DB_URL = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

engine = create_engine(DB_URL, echo=True)

def create_database_and_tables():
    try:
        SQLModel.metadata.create_all(bind=engine)
        print("Tables created successfully.")
    except SQLAlchemyError as e:
        print(f"Error creating tables: {e}")
