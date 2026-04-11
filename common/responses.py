from fastapi.responses import JSONResponse

# HTTP Success Messages
HEM_INTERNAL_SERVER_ERROR = "Something went wrong. Please try again."
# HEM_UNAUTHORIZED = "Unauthorized error"
HEM_UNAUTHORIZED = "Your Session has been expired!"
HSM_SUCCESS = "success"

# HTTP Error Messages
HEM_ERROR = "error"
HEM_INVALID_EMAIL_FORMAT = "Invalid email format"
HEM_INVALID_MOBILE_FORMAT = "Invalid mobile number format"
HEM_INVALID_VERIFY_CODE_FORMAT = "Verify code must contain only numbers."


def successResponse(status_code, msg, data={}):
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success",
            "message": msg,
            "data": data,
        }
    )

def errorResponse(status_code, msg, data={}):
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "message": msg,
            "data": data,
        }
    )
