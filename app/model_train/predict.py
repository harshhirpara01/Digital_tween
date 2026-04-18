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
def predict_activity(data: dict):
    try:
        current_user=Depends(get_current_user),

        user_id = current_user["id"]

        # 🔥 Load files
        model = joblib.load(f"app/ml/models/model_{user_id}.pkl")
        activity_encoder = joblib.load(f"app/ml/models/activity_encoder_{user_id}.pkl")
        mood_encoder = joblib.load(f"app/ml/models/mood_encoder_{user_id}.pkl")
        columns = joblib.load(f"app/ml/models/columns_{user_id}.pkl")

        # 🔥 Encode input
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
            "productivity_score": data["productivity_score"]
        }

        df = pd.DataFrame([input_dict])
        df = df.reindex(columns=columns, fill_value=0)

        # 🔥 Prediction
        pred = model.predict(df)[0]
        predicted_activity = activity_encoder.inverse_transform([pred])[0]

        # 🔥 Confidence
        proba = model.predict_proba(df)
        confidence = round(max(proba[0]) * 100, 2)

        # 🔥 Suggestion (simple logic)
        if data["mobile_usage_hours"] > 4:
            suggestion = "Mobile kam use kar"
        elif data["productivity_score"] < 5:
            suggestion = "Focus improve kar"
        else:
            suggestion = "Tu sahi track pe hai"

        return successResponse(
            status.HTTP_200_OK,
            "success",
            {
                "predicted_activity": predicted_activity,
                "confidence": f"{confidence}%",
                "suggestion": suggestion
            }
        )

    except Exception as e:
        print(e)
        return errorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, "Error")