from datetime import date, time

from pydantic import BaseModel


class add_log(BaseModel):
    user_id : int
    log_date : date
    log_hour : int
    activity : str
    mood : str
    energy_level : int
    study_hour : float
    work_hour : float
    mobile_usage_hour : float
    sleep_hours : float
    social_intreaction_minutes : int
    is_weekend : bool
    productivy_score : float