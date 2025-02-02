from typing import Annotated
from contextlib import asynccontextmanager

import debugpy
from fastapi import FastAPI, HTTPException, UploadFile, Form, File
from pydantic import EmailStr, ValidationError
from sqlmodel import Session

from models.patient import Patient, PatientPublic
from db import engine, create_database_and_tables
from utils.chunks import read_file_in_chunks, FileTooLargeException

@asynccontextmanager
async def lifespan(app: FastAPI):
    debugpy.listen(("0.0.0.0", 5678))
    create_database_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.put("/patient", response_model=PatientPublic)
async def create_patient(
    name: Annotated[str, Form(
        min_length=1,
        max_length=255,
        title="Name",
        description="The full name of the patient."
    )],
    address: Annotated[str, Form(
        min_length=10,
        max_length=255,
        title="Address",
        description="The full address of the patient."
    )],
    email: Annotated[EmailStr, Form(
        max_length=255,
        title="Email",
        description="The email address of the patient."
    )],
    phone_number: Annotated[str, Form(
        max_length=255,
        title="Phone Number",
        description="The phone number of the patient. Should include the country code."
    )],
    document_image_file: Annotated[UploadFile, File(
        title="Document Image",
        description="A photo of the patient's ID card. Must be less than 2 MB in size and in an accepted image format (JPEG, PNG)."
    )],
):
    # Get image in chunks to avoid blocking the application.
    # NOTE: Currently, the images are stored in ram, which should be fine for moderate traffic?
    # For scaling, consider:
    #   1. Writing images to temp files on disk (slower, but can mitigate ram usage issues)
    #   2. Monitor memory usage and deny requests after certain treshold to avoid app crashing?
    #   3. Stream image directly to a cloud storage? (will also lessen the burden on the db)
    try:
        document_image = await read_file_in_chunks(document_image_file, max_size=Patient.MAX_IMG_SIZE)
    except FileTooLargeException as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Validate data, collecting errors
    # NOTE: Currently, the image is being validated synchronously with the rest of the data,
    # which could slow down execution. If this turns out to be a problem, validate it asynchronously.
    patient_data = Patient(
        name=name,
        address=address,
        email=email,
        phone_number=phone_number,
        document_image=document_image
    )
    validation_errors = []
    try:
        Patient.model_validate(patient_data)
    except ValidationError as e:
        validation_errors.extend([
            {"loc": err["loc"], "msg": err["msg"], "type": err["type"]}
            for err in e.errors()
        ])
    if validation_errors:
        raise HTTPException(status_code=422, detail=validation_errors)

    # NOTE: It bears saying that depending on project needs, it could be needed to validate the document_image
    # with an external id validation service to prevent forged ids or otherwise false data to enter the system.

    with Session(engine) as session:
        session.add(patient_data)
        session.commit()
        session.refresh(patient_data)
        return patient_data
