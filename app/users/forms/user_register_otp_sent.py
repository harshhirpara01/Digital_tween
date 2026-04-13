from pydantic import BaseModel


class userregidterotp(BaseModel):
    full_name : str
    email : str
    password : str
    age : str
    proffesion : str
