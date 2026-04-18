import traceback

from fastapi import Depends
from sqlalchemy.orm import Session
from starlette import status

from app.users.forms.change_password import ChangePasswordForm
from app.users.forms.update_profile import UpdateProfileForm
from app.users.route import user
from common.comman_function import get_current_user
from common.responses import errorResponse, HEM_INTERNAL_SERVER_ERROR, successResponse
from fastapi.encoders import jsonable_encoder
from shared.db import get_db
from shared.models import User
from shared.password_utils import hash_password, verify_password


@user.get("/account/me")
def account_me(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        row = db.query(User).filter(User.id == current_user["id"]).first()
        if not row:
            return errorResponse(status.HTTP_404_NOT_FOUND, "User not found.")

        return successResponse(
            status.HTTP_200_OK,
            "success",
            jsonable_encoder(
                {
                    "email": row.email,
                    "full_name": row.full_name,
                    "profession": row.profession,
                }
            ),
        )
    except Exception as e:
        print(e)
        traceback.print_exc()
        return errorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, HEM_INTERNAL_SERVER_ERROR)


@user.patch("/account/profile")
def account_update_profile(
    formdata: UpdateProfileForm,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        row = db.query(User).filter(User.id == current_user["id"]).first()
        if not row:
            return errorResponse(status.HTTP_404_NOT_FOUND, "User not found.")

        row.full_name = formdata.full_name.strip()
        row.profession = formdata.profession.strip()
        db.add(row)
        db.commit()

        return successResponse(
            status.HTTP_200_OK,
            "Profile updated successfully.",
            jsonable_encoder({}),
        )
    except Exception as e:
        print(e)
        traceback.print_exc()
        db.rollback()
        return errorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, HEM_INTERNAL_SERVER_ERROR)


@user.post("/account/change-password")
def account_change_password(
    formdata: ChangePasswordForm,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        if formdata.new_password != formdata.confirm_password:
            return errorResponse(
                status.HTTP_400_BAD_REQUEST,
                "New password and confirmation do not match.",
            )

        row = db.query(User).filter(User.id == current_user["id"]).first()
        if not row:
            return errorResponse(status.HTTP_404_NOT_FOUND, "User not found.")

        if not verify_password(formdata.current_password, row.password_hash):
            return errorResponse(
                status.HTTP_400_BAD_REQUEST,
                "Current password is incorrect.",
            )

        row.password_hash = hash_password(formdata.new_password)
        db.add(row)
        db.commit()

        return successResponse(
            status.HTTP_200_OK,
            "Password changed successfully. Use your new password next time you log in.",
            jsonable_encoder({}),
        )
    except Exception as e:
        print(e)
        traceback.print_exc()
        db.rollback()
        return errorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, HEM_INTERNAL_SERVER_ERROR)
