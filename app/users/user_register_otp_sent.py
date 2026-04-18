import traceback
from fastapi import Depends
from starlette import status
from common.comman_function import get_current_user, resultset
from common.responses import errorResponse, HEM_INTERNAL_SERVER_ERROR, successResponse
from shared.db import get_db_cursor
from app.users.route import user
from app.users.forms.user_register_otp_sent import userregidterotp
from fastapi.encoders import jsonable_encoder

@user.post("/User_Register")
def user_register(
        formdata : userregidterotp,
        current_user=Depends(get_current_user),

        cursor=Depends(get_db_cursor)
):
    try:
        cursor.execute("CALL register(%s, %s,%s,%s,%s,%s,%s,%s,%s,%s)", (
            'before-insert',
            formdata.full_name,
            formdata.email,
            formdata.password,
            formdata.age,
            formdata.proffesion,
            '',  # p_otp
            0,
            '',  # msg
            ''  # msgcode
        ))


        data = resultset(cursor)
        print(data)

        dataa = {
            "otp"  : data[0].get('p_otp')
        }
        return successResponse(status.HTTP_200_OK,data[0].get('msg'),jsonable_encoder(dataa))

    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        return errorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, HEM_INTERNAL_SERVER_ERROR)








