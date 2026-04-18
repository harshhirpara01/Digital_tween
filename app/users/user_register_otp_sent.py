import secrets
import traceback

from fastapi import Depends
from sqlalchemy.orm import Session
from starlette import status

from app.users.forms.user_register_otp_sent import userregidterotp
from app.users.route import user
from common.comman_function import send_registration_otp_mail
from common.responses import errorResponse, HEM_INTERNAL_SERVER_ERROR, successResponse
from fastapi.encoders import jsonable_encoder
from shared.db import get_db
from shared.models import User
from shared.password_utils import hash_password


@user.post("/User_Register")
def user_register(
    formdata: userregidterotp,
    db: Session = Depends(get_db),
):
    try:
        email = formdata.email.strip().lower()
        existing = db.query(User).filter(User.email == email).first()

        if existing and existing.is_verified:
            return errorResponse(
                status.HTTP_400_BAD_REQUEST,
                "This email is already registered. Please log in.",
            )

        otp = f"{secrets.randbelow(1_000_000):06d}"
        password_hash = hash_password(formdata.password)

        if existing and not existing.is_verified:
            existing.full_name = formdata.full_name
            existing.password_hash = password_hash
            existing.age = formdata.age
            existing.profession = formdata.proffesion
            existing.otp_code = otp
            user_row = existing
        else:
            user_row = User(
                full_name=formdata.full_name,
                email=email,
                password_hash=password_hash,
                age=formdata.age,
                profession=formdata.proffesion,
                otp_code=otp,
                is_verified=False,
            )
            db.add(user_row)

        db.flush()

        if not send_registration_otp_mail(email, otp, formdata.full_name):
            db.rollback()
            return errorResponse(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Verification email could not be sent. Check MAIL_USER and EMAIL_PASS in .env (Gmail app password).",
            )

        db.commit()

        return successResponse(
            status.HTTP_200_OK,
            "Verification code sent to your email.",
            jsonable_encoder({}),
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        db.rollback()
        return errorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, HEM_INTERNAL_SERVER_ERROR)
