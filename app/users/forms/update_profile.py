from pydantic import BaseModel, Field


class UpdateProfileForm(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=200)
    profession: str = Field(..., min_length=1, max_length=200)
