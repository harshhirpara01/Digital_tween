from pydantic import BaseModel


class get_log(BaseModel):
    user_id : int
