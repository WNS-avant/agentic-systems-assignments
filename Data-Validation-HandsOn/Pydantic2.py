from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from pydantic import field_validator
import re


class Address(BaseModel):
    city: str = Field(..., min_length=3)
    pincode: str

    model_config = ConfigDict(validate_assignment=True)

    @classmethod
    def validate_pincode(cls, value: str):
        if not re.fullmatch(r"\d{6}", value):
            raise ValueError("Pincode must be exactly 6 digits")
        return value

    @field_validator("pincode")
    def check_pincode(cls, v):
        return cls.validate_pincode(v)


class User(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    age: int = Field(..., gt=18)
    address: Address
    is_premium: Optional[bool] = False

    # Enable assignment validation
    model_config = ConfigDict(validate_assignment=True)

# Example Usage

try:
    user = User(
        user_id=1,
        name="Nachiketha",
        email="nachi@example.com",
        age=25,
        address={
            "city": "Hyd",
            "pincode": "500001"
        }
    )

    print("User created successfully!")
    print(user)

    user.age = 17   

except Exception as e:
    print("Validation Error:")
    print(e)