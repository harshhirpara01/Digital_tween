import os
import joblib
import traceback
from fastapi import Depends
from starlette import status
from fastapi.encoders import jsonable_encoder

from common.comman_function import get_current_user
from common.responses import successResponse, errorResponse, HEM_INTERNAL_SERVER_ERROR
from app.model_train.route import model_train
import pandas as pd


@model_train.post("/ml/predict/activity")
def predict_activity(
    data: dict,
    current_user=Depends(get_current_user),
):
    try:
        user_id = current_user["id"]
        base = f"app/ml/models/model_{user_id}.pkl"

        if not os.path.isfile(base):
            return errorResponse(
                status.HTTP_400_BAD_REQUEST,
                "Train a model on your logs first (Train ML on the home page).",
            )

        model = joblib.load(f"app/ml/models/model_{user_id}.pkl")
        activity_encoder = joblib.load(f"app/ml/models/activity_encoder_{user_id}.pkl")
        mood_encoder = joblib.load(f"app/ml/models/mood_encoder_{user_id}.pkl")
        columns = joblib.load(f"app/ml/models/columns_{user_id}.pkl")

        input_dict = {
            "log_hour": data["log_hour"],
            "mood": mood_encoder.transform([data["mood"]])[0],
            "energy_level": data["energy_level"],
            "study_hours": data["study_hours"],
            "work_hours": data["work_hours"],
            "mobile_usage_hours": data["mobile_usage_hours"],
            "sleep_hours": data["sleep_hours"],
            "social_interaction_minutes": data["social_interaction_minutes"],
            "is_weekend": data["is_weekend"],
            "productivity_score": data["productivity_score"],
        }

        df = pd.DataFrame([input_dict])
        df = df.reindex(columns=columns, fill_value=0)

        pred = model.predict(df)[0]
        predicted_activity = activity_encoder.inverse_transform([pred])[0]

        proba = model.predict_proba(df)
        confidence = round(max(proba[0]) * 100, 2)

        if data["mobile_usage_hours"] > 4:
            suggestion = "Screen time looks high — try a shorter phone block this evening."
        elif data["productivity_score"] < 5:
            suggestion = "Focus is a bit low — try one 25-minute deep-work sprint."
        else:
            suggestion = "You are on a solid track — keep this rhythm going."

        return successResponse(
            status.HTTP_200_OK,
            "success",
            jsonable_encoder(
                {
                    "predicted_activity": str(predicted_activity),
                    "confidence": f"{confidence}%",
                    "suggestion": suggestion,
                }
            ),
        )

    except KeyError as ke:
        return errorResponse(
            status.HTTP_400_BAD_REQUEST,
            f"Missing field: {ke}",
        )
    except Exception as e:
        print(e)
        traceback.print_exc()
        return errorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, HEM_INTERNAL_SERVER_ERROR)
