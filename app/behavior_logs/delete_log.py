import json
import traceback
from fastapi import Depends
from starlette import status
from common.comman_function import get_current_user, resultset, create_token
from common.responses import errorResponse, HEM_INTERNAL_SERVER_ERROR, successResponse
from shared.db import get_db_cursor
from app.behavior_logs.route import behavior_log
from app.behavior_logs.forms.delete_log import delete_log
from fastapi.encoders import jsonable_encoder

@behavior_log.post("/Behavior-log-delete")
def delete_add(formdata : delete_log,
        # current_user=Depends(get_current_user),
        cursor=Depends(get_db_cursor)
):
    try:


        cursor.execute("CALL behavior_log(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s   )", (
            'log-delet',
            formdata.log_id,
            # current_user["id"],
            0,
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

        if data[0].get('msgcode') == 'success':


            return successResponse(status.HTTP_200_OK,data[0].get('msg'))

        return errorResponse(status.HTTP_400_BAD_REQUEST,data[0].get('msg'))

    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        return errorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, HEM_INTERNAL_SERVER_ERROR)








