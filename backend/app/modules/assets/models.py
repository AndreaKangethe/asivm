from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    identifiers: Mapped[list["AssetIdentifier"]] = relationship(back_populates="asset")


class AssetIdentifier(Base):
    __tablename__ = "asset_identifiers"
    __table_args__ = (
        Index("ix_asset_identifier_lookup", "identifier_type", "value"),
        Index(
            "uq_active_asset_identifier",
            "identifier_type",
            "value",
            unique=True,
            sqlite_where=text("valid_to IS NULL"),
            postgresql_where=text("valid_to IS NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    identifier_type: Mapped[str] = mapped_column(String(64))
    value: Mapped[str] = mapped_column(String(255))
    valid_from: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    valid_to: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    asset: Mapped[Asset] = relationship(back_populates="identifiers")
