from datetime import date, time

from pydantic import BaseModel


class delete_log(BaseModel):
    log_id : int
