from pydantic import BaseModel, EmailStr, Field
from pydantic import ValidationError

class UserRegister(BaseModel):
    username: str = Field(..., min_length=5)
    email: EmailStr
    age: int = Field(..., gt=18)


# Example Usage
try:
    user = UserRegister(
        username="nachi123",
        email="nachi@example.com",    # Valid Input
        age=22
    )
    print("Valid user:", user)

#     # user = UserRegister(
#     # username="abc",            // Invalid Input 
#     # email="not-an-email",  
#     # age=17                 
# )

except ValidationError as e:
    print("Validation Error:")
    print(e)