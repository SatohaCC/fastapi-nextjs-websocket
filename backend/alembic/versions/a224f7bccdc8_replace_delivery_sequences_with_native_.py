"""replace delivery_sequences table with native PostgreSQL SEQUENCE objects.

Revision ID: a224f7bccdc8
Revises: 12d95178888c
Create Date: 2026-06-20 19:36:21.956194

delivery_sequences テーブルによる行ロック式の採番は、同一 sequence_name への
書き込みが多いとボトルネックになる（GitHub Issue #8）。これを PostgreSQL
ネイティブの SEQUENCE オブジェクト（nextval()）による非トランザクショナルな
採番に置き換える。

既存の delivery_sequences の各行（固定3件 global_chat/direct_request/
system_global ＋ 稼働中ユーザー分の direct_request:{userid} 行）について、
対応する SEQUENCE を作成し、既存の last_id を setval() で引き継いだ上で
テーブルを削除する。

ハッシュ関数はアプリ側ロジック（app.infrastructure.persistence.sa_outbox_repository
._sequence_ident）と同一のアルゴリズムだが、将来的なアプリ側の変更から
マイグレーションを独立させるため、ここにローカルに再定義する。
"""

import hashlib
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a224f7bccdc8"
down_revision: str | None = "12d95178888c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _sequence_ident(name: str) -> str:
    """SequenceName の値から固定長ハッシュ識別子を導出する。

    アプリ側ロジック（sa_outbox_repository._sequence_ident）の凍結コピー。
    将来のアプリ側変更からマイグレーションを独立させるため、ここに再定義する。
    """
    digest = hashlib.sha256(name.encode()).hexdigest()[:32]
    return f"seq_{digest}"


def upgrade() -> None:
    """delivery_sequences の各行をネイティブ SEQUENCE に移行し、テーブルを削除。"""
    bind = op.get_bind()
    rows = bind.execute(
        sa.text("SELECT name, last_id FROM delivery_sequences")
    ).fetchall()

    for name, last_id in rows:
        ident = _sequence_ident(name)
        bind.execute(sa.text(f"CREATE SEQUENCE IF NOT EXISTS {ident}"))
        if last_id and last_id > 0:
            # is_called=true で setval。次回の nextval() は last_id+1 を返す。
            bind.execute(
                sa.text(f"SELECT setval('{ident}', :last_id, true)").bindparams(
                    last_id=last_id
                )
            )

    op.drop_table("delivery_sequences")


def downgrade() -> None:
    """delivery_sequences テーブルをベストエフォートで復元します。

    SEQUENCE の ident はユーザーIDから一方向ハッシュで導出されているため、
    動的に生成された per-user inbox（direct_request:{userid}）の SEQUENCE から
    元の sequence_name 文字列を逆算することはできない。
    そのため downgrade では固定3件（global_chat, direct_request, system_global）の
    last_id のみを、対応する SEQUENCE の現在値から復元する。稼働中ユーザー分の
    per-user inbox の連番状態は失われる。
    SEQUENCE オブジェクト自体は削除しない（再度 upgrade すれば元に戻せる）。
    """
    op.create_table(
        "delivery_sequences",
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("last_id", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("name"),
    )

    bind = op.get_bind()
    for name in ("global_chat", "direct_request", "system_global"):
        ident = _sequence_ident(name)
        exists = bind.execute(
            sa.text("SELECT to_regclass(:ident) IS NOT NULL").bindparams(ident=ident)
        ).scalar()
        if not exists:
            continue
        last_value, is_called = bind.execute(
            sa.text(f"SELECT last_value, is_called FROM {ident}")
        ).one()
        last_id = int(last_value) if is_called else 0
        bind.execute(
            sa.text(
                "INSERT INTO delivery_sequences (name, last_id) "
                "VALUES (:name, :last_id)"
            ).bindparams(name=name, last_id=last_id)
        )
