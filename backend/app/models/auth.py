from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., description="Nombre de usuario del auditor o personal hospitalario")
    password: str = Field(..., description="Contraseña")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Token de actualización JWT (7 días)")


class UserProfile(BaseModel):
    username: str
    role: str = "auditor_clinico"
    full_name: str = "Dr. Auditor Quirúrgico"
    organization: str = "Aseguradora Nacional / Hospital de la Red"


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(900, description="Tiempo de expiración en segundos (15 minutos = 900s)")
    user: UserProfile
