import traceback

from fastapi import Depends
from sqlalchemy.orm import Session
from starlette import status

from app.users.forms.verify_register_otp import verifyotp
from app.users.route import user
from common.responses import errorResponse, HEM_INTERNAL_SERVER_ERROR, successResponse
from fastapi.encoders import jsonable_encoder
from shared.db import get_db
from shared.models import User


@user.post("/verify_register_otp")
def verify_register_otp(
    formdata: verifyotp,
    db: Session = Depends(get_db),
):
    try:
        email = formdata.email.strip().lower()
        user_row = db.query(User).filter(User.email == email).first()

        if not user_row:
            return errorResponse(
                status.HTTP_400_BAD_REQUEST,
                "No registration found for this email. Register again.",
            )

        if user_row.is_verified:
            return errorResponse(
                status.HTTP_400_BAD_REQUEST,
                "This account is already verified. You can log in.",
            )

        if not user_row.otp_code or str(user_row.otp_code).strip() != str(formdata.otp).strip():
            return errorResponse(
                status.HTTP_400_BAD_REQUEST,
                "Invalid or expired verification code.",
            )

        user_row.is_verified = True
        user_row.otp_code = None
        db.add(user_row)
        db.commit()

        return successResponse(
            status.HTTP_200_OK,
            "Email verified successfully. You can log in now.",
            jsonable_encoder({"status": "success"}),
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        db.rollback()
        return errorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, HEM_INTERNAL_SERVER_ERROR)
