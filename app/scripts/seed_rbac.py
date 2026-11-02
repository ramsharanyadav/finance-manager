
from sqlalchemy import select

from app.database.connection import SessionLocal
from app.models.role import Role
from app.models.permission import Permission

from app.core.permissions import (
    DEFAULT_PERMISSIONS,
    USER_PERMISSIONS,
    ADMIN_PERMISSIONS,
)


def seed_permissions(db):
    """
    Create default permissions if they do not exist.
    """

    existing_permissions = db.scalars(
        select(Permission)
    ).all()

    permission_map = {
        permission.code: permission
        for permission in existing_permissions
    }

    for code, description in DEFAULT_PERMISSIONS:
        if code not in permission_map:
            permission = Permission(
                code=code,
                description=description,
            )

            db.add(permission)
            permission_map[code] = permission

    db.flush()

    return permission_map


def seed_roles(db, permission_map):
    """
    Create default roles and attach permissions.
    """

    role_definitions = {
        "USER": {
            "description": "Normal application user",
            "permissions": USER_PERMISSIONS,
        },
        "ADMIN": {
            "description": "Application administrator",
            "permissions": ADMIN_PERMISSIONS,
        },
    }

    for role_name, role_data in role_definitions.items():

        role = db.scalar(
            select(Role).where(Role.name == role_name)
        )

        if role is None:
            role = Role(
                name=role_name,
                description=role_data["description"],
            )
            db.add(role)

        role.permissions = [
            permission_map[code]
            for code in role_data["permissions"]
        ]


def seed_rbac():
    """
    Main RBAC seeding function.
    """

    db = SessionLocal()

    try:
        permission_map = seed_permissions(db)

        seed_roles(db, permission_map)

        db.commit()

        print("RBAC seed completed successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_rbac()
