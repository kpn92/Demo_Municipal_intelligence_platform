from __future__ import annotations

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.role import Role
from app.models.user import AppUser
from app.models.user_role import UserRole


ROLES = [
    ("admin", "Διαχειριστής"),
    ("cleaning_supervisor", "Επόπτης Καθαριότητας"),
    ("fleet_operator", "Χειριστής Στόλου"),
]

USERS = [
    {
        "username": "admin",
        "full_name": "Admin Δήμου",
        "role_code": "admin",
        "is_superuser": True,
    },
    {
        "username": "supervisor",
        "full_name": "G. Papadopoulos",
        "role_code": "cleaning_supervisor",
        "is_superuser": False,
    },
    {
        "username": "fleet",
        "full_name": "Στόλος Καθαριότητας",
        "role_code": "fleet_operator",
        "is_superuser": False,
    },
]


def main() -> None:
    with SessionLocal() as db:
        roles_by_code = {}
        for code, name in ROLES:
            role = db.execute(select(Role).where(Role.code == code)).scalar_one_or_none()
            if not role:
                role = Role(code=code, name=name, description=None, is_active=True)
                db.add(role)
                db.flush()
            else:
                role.name = name
                role.is_active = True
            roles_by_code[code] = role

        for user_data in USERS:
            username = user_data["username"]
            user = db.execute(select(AppUser).where(AppUser.username == username)).scalar_one_or_none()
            if not user:
                user = AppUser(
                    username=username,
                    email=None,
                    full_name=user_data["full_name"],
                    password_hash=hash_password("demo"),
                    is_active=True,
                    is_superuser=user_data["is_superuser"],
                )
                db.add(user)
                db.flush()
            else:
                user.full_name = user_data["full_name"]
                user.is_active = True
                user.is_superuser = user_data["is_superuser"]

            role = roles_by_code[user_data["role_code"]]
            existing_link = db.execute(
                select(UserRole).where(UserRole.user_id == user.id, UserRole.role_id == role.id)
            ).scalar_one_or_none()
            if not existing_link:
                db.add(UserRole(user_id=user.id, role_id=role.id))

        anna = db.execute(select(AppUser).where(AppUser.username.in_(["anna", "anna karapiperi"]))).scalars().all()
        for user in anna:
            user.is_active = False

        db.commit()


if __name__ == "__main__":
    main()
