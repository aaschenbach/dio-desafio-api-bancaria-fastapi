"""Modelo ORM de conta corrente."""

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Account(Base):
    """Representa uma conta corrente bancária."""

    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("agency", "account_number", name="uq_accounts_agency_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    agency: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    account_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    owner_name: Mapped[str] = mapped_column(String(120), nullable=False)
    owner_document: Mapped[str | None] = mapped_column(String(30), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    user = relationship("User", back_populates="accounts")
    transactions = relationship(
        "Transaction",
        back_populates="account",
        cascade="all, delete-orphan",
        order_by="Transaction.created_at",
    )
