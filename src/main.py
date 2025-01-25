from contextlib import asynccontextmanager

import debugpy
from fastapi import FastAPI
from sqlmodel import Session, select

from models.patient import Patient, PatientCreate, PatientPublic
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

@app.get("/patients", response_model=list[PatientPublic])
def read_patients():
    with Session(engine) as session:
        patients = session.exec(select(Patient)).all()
        return patients

@app.put("/patient", response_model=PatientPublic)
def create_patient(patient: PatientCreate):
    with Session(engine) as session:
        db_patient = Patient.model_validate(patient)
        session.add(db_patient)
        session.commit()
        session.refresh(db_patient)
        return db_patient
