
from pydantic import BaseModel


class loginform(BaseModel):
    email : str
    password : str

