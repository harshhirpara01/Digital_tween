import traceback
from fastapi import Depends
from starlette import status
from common.comman_function import get_current_user, resultset
from common.responses import errorResponse, HEM_INTERNAL_SERVER_ERROR
from shared.db import get_db_cursor
from app.users.route import user
from app.users.forms.user_register_otp_sent import userregidterotp


user.post("/User_Register")
def user_register(
        # current_user=Depends(get_current_user),
        formdata : userregidterotp = Depends(),
        cursor=Depends(get_db_cursor)
):
    try:
        execstring = """
            CALL register(%s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(execstring, (
            'before-insert',
            formdata.full_name,
            formdata.email,
            formdata.password,
            formdata.age,
            formdata.proffesion,
            '',
            ''
        ))

        cursor.execute(execstring)
        data = resultset(cursor)

    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        return errorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, HEM_INTERNAL_SERVER_ERROR)








