import traceback

from fastapi import Depends
from sqlalchemy.orm import Session
from starlette import status

from app.users.forms.login import loginform
from app.users.route import user
from common.comman_function import create_token
from common.responses import errorResponse, HEM_INTERNAL_SERVER_ERROR, successResponse
from fastapi.encoders import jsonable_encoder
from shared.db import get_db
from shared.models import User
from shared.password_utils import verify_password


@user.post("/login")
def login(
    formdata: loginform,
    db: Session = Depends(get_db),
):
    try:
        email = formdata.email.strip().lower()
        user_row = db.query(User).filter(User.email == email).first()

        if not user_row or not verify_password(formdata.password, user_row.password_hash):
            return errorResponse(
                status.HTTP_400_BAD_REQUEST,
                "Invalid email or password.",
            )

        if not user_row.is_verified:
            return errorResponse(
                status.HTTP_400_BAD_REQUEST,
                "Please verify your email with the OTP we sent before logging in.",
            )

        token = create_token(email=user_row.email, uid=user_row.id)
        if isinstance(token, dict) and token.get("status") == "error":
            return errorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, str(token.get("message")))

        return successResponse(
            status.HTTP_200_OK,
            "Login successful.",
            jsonable_encoder({"token": token}),
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        return errorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, HEM_INTERNAL_SERVER_ERROR)
