from typing import Annotated
from contextlib import asynccontextmanager

import debugpy
from fastapi import FastAPI, HTTPException, UploadFile, Form, File
from pydantic import EmailStr, ValidationError
from sqlmodel import Session, select

from models.patient import Patient, PatientPublic
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
async def create_patient(
    name: Annotated[str, Form()],
    email: Annotated[EmailStr, Form()],
    phone_number: Annotated[str, Form()],
    document_image_file: Annotated[UploadFile, File()]
):
    document_image = await document_image_file.read()
    patient_data = Patient(name=name, email=email, phone_number=phone_number, document_image=document_image)

    validation_errors = []
    try:
        Patient.model_validate(patient_data)
    except ValidationError as e:
        # FastAPI's Pydantic validation errors
        validation_errors.extend([
            {"loc": err["loc"], "msg": err["msg"], "type": err["type"]}
            for err in e.errors()
        ])
    if validation_errors:
        raise HTTPException(status_code=422, detail=validation_errors)

    with Session(engine) as session:
        session.add(patient_data)
        session.commit()
        session.refresh(patient_data)
        return patient_data
