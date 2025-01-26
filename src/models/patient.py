from sqlmodel import SQLModel, Field
from pydantic import EmailStr, field_validator
import phonenumbers

class PatientBase(SQLModel):
    name: str
    email: EmailStr
    phone_number: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        # Validating names is a complex endeavour, so I'm only catching empty strings here.
        # Stricter validation can be implemented if required.
        # For context, see answer and comments at https://stackoverflow.com/a/2385811
        if not value.strip():
            raise ValueError("Name cannot be empty or only whitespace")
        return value

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value):
        try:
            parsed_phone = phonenumbers.parse(value)
            if not phonenumbers.is_valid_number(parsed_phone):
                raise ValueError("Invalid phone number")
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValueError("Invalid phone number format")
        return value

class Patient(PatientBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class PatientCreate(PatientBase):
    pass

class PatientPublic(PatientBase):
    id: int
