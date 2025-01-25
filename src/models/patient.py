from sqlmodel import SQLModel, Field
from pydantic import EmailStr
import phonenumbers

class PatientBase(SQLModel):
    name: str
    email: EmailStr
    phone_number: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate_phone_number()

    def validate_phone_number(self):
        try:
            parsed_phone = phonenumbers.parse(self.phone_number)
            if not phonenumbers.is_valid_number(parsed_phone):
                raise ValueError("Invalid phone number")
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValueError("Invalid phone number format")

class Patient(PatientBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class PatientCreate(PatientBase):
    pass

class PatientPublic(PatientBase):
    id: int
