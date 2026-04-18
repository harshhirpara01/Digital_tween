import traceback

from fastapi import Depends
from sqlalchemy.orm import Session
from starlette import status

from app.model_train.route import model_train
from common.comman_function import train_model, get_current_user
from common.responses import errorResponse, successResponse, HEM_INTERNAL_SERVER_ERROR
from shared.db import get_db
from shared.models import BehaviorLog
from shared.serializers import behavior_log_to_dict


MIN_LOGS_FOR_TRAIN = 5


@model_train.post("/ml/train/{user_id}")
def train(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        if int(user_id) != int(current_user["id"]):
            return errorResponse(
                status.HTTP_403_FORBIDDEN,
                "You can only train a model for your own account.",
            )

        rows = (
            db.query(BehaviorLog)
            .filter(BehaviorLog.user_id == current_user["id"])
            .order_by(BehaviorLog.log_date, BehaviorLog.id)
            .all()
        )

        if len(rows) == 0:
            return errorResponse(
                status.HTTP_400_BAD_REQUEST,
                "You have no behavior logs yet. Open the Logs page, add a few entries "
                "(mood, sleep, study time, etc.), then tap Train ML again.",
            )

        if len(rows) < MIN_LOGS_FOR_TRAIN:
            return errorResponse(
                status.HTTP_400_BAD_REQUEST,
                f"You have {len(rows)} log(s). Add at least {MIN_LOGS_FOR_TRAIN} behavior logs before training "
                "so the model has enough signal. Then try again.",
            )

        dataset = [behavior_log_to_dict(r) for r in rows]
        activities = {str(d.get("activity", "")).strip() for d in dataset if d.get("activity")}
        if len(activities) < 2:
            return errorResponse(
                status.HTTP_400_BAD_REQUEST,
                "Training needs at least two different activity values in your logs "
                '(for example, "study" and "work"). Add more varied logs, then try again.',
            )

        train_model(dataset, current_user["id"])

        return successResponse(
            status.HTTP_200_OK,
            "Model trained successfully.",
            "Model trained successfully",
        )

    except ValueError as ve:
        return errorResponse(status.HTTP_400_BAD_REQUEST, str(ve))
    except Exception as e:
        print(str(e))
        traceback.print_exc()
        return errorResponse(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            HEM_INTERNAL_SERVER_ERROR,
        )
