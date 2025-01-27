from typing import ClassVar
from io import BytesIO

from PIL import Image, UnidentifiedImageError
import phonenumbers
from pydantic import EmailStr, field_validator
from sqlmodel import SQLModel, Field, Column, BLOB
from sqlalchemy import event

from background_tasks.send_email import send_email

class PatientBase(SQLModel):
    name: str = Field(
        min_length=1,
        max_length=255,
        title="Name",
        description="The full name of the patient.",
    )
    address: str = Field(
        min_length=10,
        max_length=255,
        title="Address",
        description="The full address of the patient."
    )
    email: EmailStr = Field(
        max_length=255,
        title="Email",
        description="The email of the patient."
    )
    phone_number: str = Field(
        max_length=255,
        title="Phone Number",
        description="The phone number of the patient."
    )

    # NOTE: Validating names is a complex endeavour, so I'm only catching empty strings here.
    # Stricter validation can be implemented if required.
    # For context, see answer and comments at https://stackoverflow.com/a/2385811

    @field_validator("name", "address")
    @classmethod
    def validate_not_whitespace(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Value cannot be only whitespace")
        return value

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        try:
            parsed_phone = phonenumbers.parse(value)
            if not phonenumbers.is_valid_number(parsed_phone):
                raise ValueError("Invalid phone number")
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValueError("Invalid phone number format")
        return value

class Patient(PatientBase, table=True):
    # Limit img size to 2mb
    MAX_IMG_SIZE: ClassVar[int] = 2 * (1024 ** 2)

    id: int | None = Field(default=None, primary_key=True)
    document_image: bytes = Field(
        sa_column=Column(BLOB(MAX_IMG_SIZE)),
        title="Document Image",
        description="A photo of the patient's ID card. Must be less than 2 MB in size and in an accepted image format (JPEG, PNG)."
    )

    @field_validator("document_image")
    @classmethod
    def validate_document_image(cls, value: bytes) -> bytes:
        try:
            with Image.open(BytesIO(value)) as img:
                if img.format not in {"PNG", "JPEG"}:
                    raise ValueError(f"Invalid image format, must be PNG or JPEG")
                img.verify()
        except UnidentifiedImageError:
            raise ValueError("Invalid image")
        except OSError as e:
            print (f"Validating image raised OSError: {str(e)}")
            raise ValueError("Invalid image")
        except ValueError as e:
            raise ValueError(str(e))
        return value

class PatientPublic(PatientBase):
    id: int

# NOTE: Event listeners bellow. Should probably be refactored out if they start to add up
def patient_after_insert_listener(mapper, connection, target: Patient):
    subject = "Registration succesful!"
    recipients = [target.email]
    body = f"""Hello {target.name},

Your registration is complete. Thank you for trusting us with your data.

Warm regards,
The Patient Registration Team
"""

    send_email(subject, recipients, body)

event.listen(Patient, "after_insert", patient_after_insert_listener)
