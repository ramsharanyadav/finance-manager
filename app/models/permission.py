import uuid

from typing import TYPE_CHECKING

from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin


if TYPE_CHECKING:
    from app.models.role import Role

class Permission(TimestampMixin, Base):

    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    roles: Mapped[list["Role"]] = relationship(
        secondary="role_permissions",
        back_populates="permissions"
    )