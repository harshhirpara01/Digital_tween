
from pydantic import BaseModel


class verifyotp(BaseModel):
    email : str
    otp : str

