from pydantic import BaseModel, EmailStr


class CareProviderResponse(BaseModel):
    given_name: str
    email: EmailStr
