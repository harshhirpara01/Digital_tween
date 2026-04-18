import traceback

from fastapi import Depends
from sqlalchemy.orm import Session
from starlette import status

from app.behavior_logs.route import behavior_log
from common.comman_function import get_current_user
from common.responses import errorResponse, HEM_INTERNAL_SERVER_ERROR, successResponse
from fastapi.encoders import jsonable_encoder
from shared.db import get_db
from shared.models import BehaviorLog
from shared.serializers import behavior_log_to_dict


@behavior_log.get("/Behavior-log-get")
def log_get(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        rows = (
            db.query(BehaviorLog)
            .filter(BehaviorLog.user_id == current_user["id"])
            .order_by(BehaviorLog.log_date, BehaviorLog.id)
            .all()
        )
        data = [behavior_log_to_dict(r) for r in rows]

        return successResponse(
            status.HTTP_200_OK,
            "success",
            jsonable_encoder(data),
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        return errorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, HEM_INTERNAL_SERVER_ERROR)
