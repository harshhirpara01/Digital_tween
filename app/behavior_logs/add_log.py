import traceback

from fastapi import Depends
from sqlalchemy.orm import Session
from starlette import status

from app.behavior_logs.forms.add_log import add_log
from app.behavior_logs.route import behavior_log
from common.comman_function import get_current_user
from common.responses import errorResponse, HEM_INTERNAL_SERVER_ERROR, successResponse
from shared.db import get_db
from shared.models import BehaviorLog


@behavior_log.post("/Behavior-log-add")
def log_add(
    formdata: add_log,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        if formdata.productivy_score > 10:
            return errorResponse(
                status.HTTP_400_BAD_REQUEST,
                "Please enter a productivity score between 1 and 10.",
            )

        row = BehaviorLog(
            user_id=current_user["id"],
            log_date=formdata.log_date,
            log_hour=formdata.log_hour,
            activity=formdata.activity,
            mood=formdata.mood,
            energy_level=formdata.energy_level,
            study_hour=formdata.study_hour,
            work_hour=formdata.work_hour,
            mobile_usage_hour=formdata.mobile_usage_hour,
            sleep_hours=formdata.sleep_hours,
            social_intreaction_minutes=formdata.social_intreaction_minutes,
            is_weekend=formdata.is_weekend,
            productivy_score=formdata.productivy_score,
        )
        db.add(row)
        db.commit()

        return successResponse(status.HTTP_200_OK, "Log saved successfully.")

    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        db.rollback()
        return errorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, HEM_INTERNAL_SERVER_ERROR)
