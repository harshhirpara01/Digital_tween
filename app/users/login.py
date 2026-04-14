import traceback
from fastapi import Depends
from starlette import status
from common.comman_function import get_current_user, resultset, create_token
from common.responses import errorResponse, HEM_INTERNAL_SERVER_ERROR, successResponse
from shared.db import get_db_cursor
from app.users.route import user
from app.users.forms.login import loginform
from fastapi.encoders import jsonable_encoder

@user.post("/login")
def login(
        # current_user=Depends(get_current_user),
        formdata : loginform,
        cursor=Depends(get_db_cursor)
):
    try:
        cursor.execute("CALL register(%s, %s,%s,%s,%s,%s,%s,%s,%s,%s)", (
            'login',
            '',
            formdata.email,
            formdata.password,
            0,
            '',
            '',  # p_otp
            0,
            '',  # msg
            ''  # msgcode
        ))


        data = resultset(cursor)
        print(data)
        if data[0].get('msgcode') == 'success':
            token = create_token(email= formdata.email,uid=data[0].get('p_uid'))
            dataa = {
                "token":token
            }

            return successResponse(status.HTTP_200_OK,data[0].get('msg'),jsonable_encoder(dataa))

        return errorResponse(status.HTTP_400_BAD_REQUEST,data[0].get('msg'))

    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        return errorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, HEM_INTERNAL_SERVER_ERROR)








