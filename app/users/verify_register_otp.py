import traceback
from fastapi import Depends
from starlette import status
from common.comman_function import get_current_user, resultset
from common.responses import errorResponse, HEM_INTERNAL_SERVER_ERROR, successResponse
from shared.db import get_db_cursor
from app.users.route import user
from app.users.forms.verify_register_otp import verifyotp
from fastapi.encoders import jsonable_encoder

@user.post("/verify_register_otp")
def user_register(
        formdata : verifyotp,
        current_user=Depends(get_current_user),
        
        cursor=Depends(get_db_cursor)
):
    try:
        cursor.execute("CALL register(%s, %s,%s,%s,%s,%s,%s,%s,%s,%s)", (
            'verify_register_otp',
            '',
            formdata.email,
            '',
            0,
            '',
            formdata.otp,
            0,# p_otp
            '',  # msg
            ''  # msgcode
        ))


        data = resultset(cursor)
        print(data)

        dataa = {
            "otp"  : data[0].get('msg')
        }
        return successResponse(status.HTTP_200_OK,data[0].get('msgcode'),jsonable_encoder(dataa))

    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        return errorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, HEM_INTERNAL_SERVER_ERROR)








