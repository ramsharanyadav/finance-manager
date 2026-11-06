from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.user import User
from app.models.role import Role

class UserRepository:

    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return db.scalar(statement)

    @staticmethod
    def get_by_id(db: Session, user_id) -> User | None:
        statement = (
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == user_id)
        )
        return db.scalar(statement)

    @staticmethod
    def create(
        db: Session,
        *, 
        full_name: str,
        email: str,
        password_hash: str
    ) -> User:
        
        user = User(
            full_name=full_name,
            email=email,
            password_hash=password_hash,
        )

        db.add(user)
        db.flush()

        return user

    @staticmethod
    def assign_role(
        db: Session,
        user: User,
        role: Role
    )-> None:

        if role not in user.roles:
            user.roles.append(role)

        db.flush()
