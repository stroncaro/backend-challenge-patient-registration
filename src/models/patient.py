from typing import ClassVar
from io import BytesIO

from PIL import Image, UnidentifiedImageError
import phonenumbers
from pydantic import EmailStr, field_validator
from sqlmodel import SQLModel, Field, Column, BLOB

class PatientBase(SQLModel):
    name: str
    email: EmailStr
    phone_number: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        # Validating names is a complex endeavour, so I'm only catching empty strings here.
        # Stricter validation can be implemented if required.
        # For context, see answer and comments at https://stackoverflow.com/a/2385811
        if not value.strip():
            raise ValueError("Name cannot be empty or only whitespace")
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
    document_image: bytes = Field(sa_column=Column(BLOB(MAX_IMG_SIZE)))

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
