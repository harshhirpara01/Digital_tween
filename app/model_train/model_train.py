import json
import traceback
from fastapi import Depends
from starlette import status
from common.comman_function import resultset, train_model
from common.responses import errorResponse, successResponse, HEM_INTERNAL_SERVER_ERROR
from shared.db import get_db_cursor
from app.model_train.route import model_train

@model_train.post("/ml/train/{user_id}")
def train(user_id: int, cursor=Depends(get_db_cursor)):
    try:

        # Step 1: Fetch dataset
        cursor.execute("CALL behavior_log(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s   )", (
            'log-get',
            0,
            # current_user["id"],
            user_id,
            None,
            0,
            '',
            '',
            0,  # p_otp
            0.0,
            0.0,  # msg
            0.0,
            0.0,
            0,
            False,
            0.0,
            '',
            '',
            ''
            # msgcode
        ))

        data = resultset(cursor)
        print(data)



        if not data or data[0].get('msgcode') != 'success':
            return errorResponse(status.HTTP_400_BAD_REQUEST, "Dataset error")

        dataset = json.loads(data[0]['p_data'])

        # Step 2: Train model
        train_model(dataset, user_id)

        return successResponse(
            status.HTTP_200_OK,
            "success",
            "Model trained successfully"
        )

    except Exception as e:
        print(str(e))
        traceback.print_exc()
        return errorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, HEM_INTERNAL_SERVER_ERROR)