from contextlib import asynccontextmanager

import debugpy
from fastapi import FastAPI
from sqlmodel import Session, select

from models.patient import Patient
from db import engine, create_database_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    debugpy.listen(("0.0.0.0", 5678))
    create_database_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World!"}

@app.get("/patients")
def read_patients():
    with Session(engine) as session:
        patients = session.exec(select(Patient)).all()
        return patients

@app.put("/patient")
def add_patient(patient: Patient):
    with Session(engine) as session:
        session.add(patient)
        session.commit()
        session.refresh(patient)
        return patient
