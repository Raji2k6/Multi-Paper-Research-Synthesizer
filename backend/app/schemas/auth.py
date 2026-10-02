from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        email = value.strip().lower()
        local, separator, domain = email.partition("@")
        if (
            not separator
            or not local
            or not domain
            or "." not in domain
            or any(character.isspace() for character in email)
        ):
            raise ValueError("Enter a valid email address.")
        return email

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("Name cannot be blank.")
        return name


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserResponse(BaseModel):
    id: str
    email: str
    name: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
