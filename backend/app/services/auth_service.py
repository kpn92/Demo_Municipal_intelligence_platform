from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.security import verify_password
from app.models.role import Role
from app.models.user import AppUser
from app.models.user_role import UserRole


ROLE_MODULES = {
    "admin": ["cleaning", "fleet", "reports", "settings"],
    "cleaning_supervisor": ["cleaning", "settings"],
    "fleet_operator": ["fleet"],
}

ROLE_ALIASES = {
    "admin": "admin",
    "cleaning_supervisor": "supervisor",
    "fleet_operator": "fleet",
}


def get_user_by_username(db: Session, username: str) -> AppUser | None:
    statement = (
        select(AppUser)
        .where(AppUser.username == username.strip().lower())
        .options(selectinload(AppUser.roles).selectinload(UserRole.role))
    )
    return db.execute(statement).scalar_one_or_none()


def authenticate_user(db: Session, username: str, password: str) -> AppUser | None:
    user = get_user_by_username(db, username)
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def build_auth_user_payload(user: AppUser) -> dict:
    roles = [entry.role for entry in user.roles if entry.role and entry.role.is_active]
    role_codes = [role.code for role in roles]
    modules = sorted({
        module
        for role_code in role_codes
        for module in ROLE_MODULES.get(role_code, [])
    })
    primary_role_code = role_codes[0] if role_codes else ("admin" if user.is_superuser else "user")
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "role": ROLE_ALIASES.get(primary_role_code, primary_role_code),
        "roles": [{"code": role.code, "name": role.name} for role in roles],
        "modules": modules,
        "sector_scope": "cleaning" if "cleaning" in modules else None,
        "is_superuser": user.is_superuser,
    }


def get_role_by_code(db: Session, code: str) -> Role | None:
    return db.execute(select(Role).where(Role.code == code)).scalar_one_or_none()
