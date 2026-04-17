import os
import joblib
import traceback
from fastapi import Depends
from starlette import status
from fastapi.encoders import jsonable_encoder

from common.responses import successResponse, errorResponse, HEM_INTERNAL_SERVER_ERROR
from app.model_train.route import model_train


@model_train.post("/ml/predict/activity")
def predict_activity(data: dict):
    try:
        user_id = data.get("user_id")

        model_path = f"app/ml/models/model_{user_id}.pkl"
        activity_encoder_path = f"app/ml/models/activity_encoder_{user_id}.pkl"
        mood_encoder_path = f"app/ml/models/mood_encoder_{user_id}.pkl"

        if not os.path.exists(model_path):
            return errorResponse(status.HTTP_400_BAD_REQUEST, "Model not trained")

        model = joblib.load(model_path)
        activity_encoder = joblib.load(activity_encoder_path)
        mood_encoder = joblib.load(mood_encoder_path)

        input_data = [[
            data["log_hour"],
            mood_encoder.transform([data["mood"]])[0],
            data["energy_level"],
            data["study_hours"],
            data["work_hours"],
            data["mobile_usage_hours"],
            data["sleep_hours"],
            data["social_interaction_minutes"],
            data["is_weekend"],
            data["productivity_score"]
        ]]

        prediction = model.predict(input_data)[0]

        predicted_activity = activity_encoder.inverse_transform([prediction])[0]

        return successResponse(
            status.HTTP_200_OK,
            "success",
            jsonable_encoder({
                "predicted_activity": predicted_activity
            })
        )

    except Exception as e:
        print(str(e))
        traceback.print_exc()
        return errorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, HEM_INTERNAL_SERVER_ERROR)