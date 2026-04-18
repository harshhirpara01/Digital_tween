import traceback

from fastapi import Depends
from sqlalchemy.orm import Session
from starlette import status

from app.behavior_logs.forms.delete_log import delete_log
from app.behavior_logs.route import behavior_log
from common.comman_function import get_current_user
from common.responses import errorResponse, HEM_INTERNAL_SERVER_ERROR, successResponse
from shared.db import get_db
from shared.models import BehaviorLog


@behavior_log.post("/Behavior-log-delete")
def delete_log_entry(
    formdata: delete_log,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        row = (
            db.query(BehaviorLog)
            .filter(
                BehaviorLog.id == formdata.log_id,
                BehaviorLog.user_id == current_user["id"],
            )
            .first()
        )

        if not row:
            return errorResponse(
                status.HTTP_400_BAD_REQUEST,
                "Log not found or you do not have permission to delete it.",
            )

        db.delete(row)
        db.commit()

        return successResponse(status.HTTP_200_OK, "Log deleted successfully.")

    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        db.rollback()
        return errorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, HEM_INTERNAL_SERVER_ERROR)
