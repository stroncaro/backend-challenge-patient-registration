from sqlmodel import SQLModel, Field
from pydantic import EmailStr, field_validator
import phonenumbers

class PatientBase(SQLModel):
    name: str
    email: EmailStr
    phone_number: str

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
