import traceback
from fastapi import Depends
from starlette import status
from common.comman_function import get_current_user, resultset, create_token
from common.responses import errorResponse, HEM_INTERNAL_SERVER_ERROR, successResponse
from shared.db import get_db_cursor
from app.behavior_logs.route import behavior_log
from app.behavior_logs.forms.add_log import add_log
from fastapi.encoders import jsonable_encoder

@behavior_log.post("/Behavior-log-add")
def log_add(formdata : add_log,
        current_user=Depends(get_current_user),
        cursor=Depends(get_db_cursor)
):
    try:
        if formdata.productivy_score > 10:
            return errorResponse(status.HTTP_400_BAD_REQUEST,"please enter score in between 1 to 10")

        cursor.execute("CALL behavior_log(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s   )", (
            'log-insert',
            0,
            current_user["id"],
            # formdata.user_id,
            formdata.log_date,
            formdata.log_hour,
            formdata.activity,
            formdata.mood,
            formdata.energy_level,  # p_otp
            formdata.study_hour,
            formdata.work_hour,  # msg
            formdata.mobile_usage_hour,
            formdata.sleep_hours,
            formdata.social_intreaction_minutes,
            formdata.is_weekend,
            formdata.productivy_score,
            '',
            '',
            '' # msgcode
        ))


        data = resultset(cursor)
        # print(data)

        if data[0].get('msgcode') == 'success':


            return successResponse(status.HTTP_200_OK,data[0].get('msg'))

        return errorResponse(status.HTTP_400_BAD_REQUEST,data[0].get('msg'))

    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        return errorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, HEM_INTERNAL_SERVER_ERROR)








