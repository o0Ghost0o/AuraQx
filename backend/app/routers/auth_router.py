from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.core.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    verify_password,
)
from app.models.auth import LoginRequest, RefreshTokenRequest, TokenResponse, UserProfile

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    """Autentica al usuario auditor/hospital con usuario y contraseña definidos por secreto."""
    valid_user = req.username == settings.auth_username
    valid_pass = verify_password(req.password, settings.auth_password)

    if not (valid_user and valid_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas. Verifique usuario y contraseña.",
        )

    user_profile = UserProfile(
        username=req.username,
        role="auditor_clinico",
        full_name="Dr. Auditor Quirúrgico",
        organization="Aseguradora Nacional / Hospital de la Red",
    )

    token_data = {
        "sub": user_profile.username,
        "role": user_profile.role,
        "full_name": user_profile.full_name,
        "org": user_profile.organization,
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=user_profile,
    )


@router.post("/refresh")
async def refresh_token(req: RefreshTokenRequest):
    """Renueva un Access Token de 15 minutos utilizando un Refresh Token válido de 7 días."""
    payload = decode_token(req.refresh_token, expected_type="refresh")
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no contiene identidad válida.",
        )

    token_data = {
        "sub": username,
        "role": payload.get("role", "auditor_clinico"),
        "full_name": payload.get("full_name", "Dr. Auditor Quirúrgico"),
        "org": payload.get("org", "Aseguradora Nacional / Hospital de la Red"),
    }

    new_access_token = create_access_token(token_data)

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
    }


@router.get("/me", response_model=UserProfile)
async def get_my_profile(current_user: UserProfile = Depends(get_current_user)):
    """Retorna el perfil del usuario autenticado."""
    return current_user
