import logging
import traceback

from fastapi import status, Request
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer

from app.demo.forms.demo import DemoSchemas
from app.demo.route import demo
from common.responses import *

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="")

logger = logging.getLogger(__name__)


@demo.post("/demo")
async def demo(
        request: Request,
        form_data: DemoSchemas
):
    try:
        if not form_data.name.strip():
            return errorResponse(status.HTTP_400_BAD_REQUEST, "Invalid Input")

        response = {
            "name": form_data.name
        }

        return successResponse(status.HTTP_200_OK, HSM_SUCCESS, jsonable_encoder(response))

    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        return errorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, HEM_INTERNAL_SERVER_ERROR)
