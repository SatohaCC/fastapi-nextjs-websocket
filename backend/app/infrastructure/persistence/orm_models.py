"""SQLAlchemy の ORM モデル定義（DB テーブルのマッピング）。"""

from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy のベースクラス"""

    pass


class MessageORM(Base):
    """チャットメッセージのテーブル定義"""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class RequestORM(Base):
    """ダイレクト・リクエストのテーブル定義"""

    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sender: Mapped[str] = mapped_column(String(50), nullable=False)
    recipient: Mapped[str] = mapped_column(String(50), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="requested")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class DeliverySequenceORM(Base):
    """Outbox 用の厳密連番（シーケンス）管理テーブル"""

    __tablename__ = "delivery_sequences"

    name: Mapped[str] = mapped_column(String(50), primary_key=True)
    last_id: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)


class DeliveryFeedORM(Base):
    """Outbox 兼 配信ログのテーブル"""

    __tablename__ = "delivery_feeds"

    sequence_name: Mapped[str] = mapped_column(String(50), primary_key=True)
    sequence_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index("ix_delivery_feeds_status_seq", "status", "sequence_name", "sequence_id"),  # ポーリング最適化
    )
