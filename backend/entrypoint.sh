#!/bin/sh
set -e

# RUN_MIGRATIONS=false の場合はマイグレーションをスキップする。
# ECS 等で複数タスクを同時起動する構成では、各タスクが同時に
# `alembic upgrade head` を実行するとDDL競合のレースが発生し得るため、
# サービス本体のタスクではマイグレーションを無効化し、デプロイ時に
# 1回限りの専用タスク（MIGRATE_ONLY=true）で実行する運用を想定している。
# 環境変数未設定時は従来通り実行する（ローカル開発・docker-compose との後方互換）。
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
    # alembic_version テーブルが存在しない場合、既存テーブルの有無を確認する。
    # テーブルが存在する → create_all で作られた既存 DB なので stamp のみ実行。
    # テーブルが存在しない → 新規 DB なので通常の upgrade を実行。
    NEEDS_STAMP=$(python -c "
import os
from sqlalchemy import create_engine, text

url = os.environ['DATABASE_URL'].replace('+asyncpg', '+psycopg2')
engine = create_engine(url)
with engine.connect() as conn:
    has_alembic = conn.execute(text(
        \"SELECT 1 FROM information_schema.tables WHERE table_name='alembic_version'\"
    )).scalar()
    if not has_alembic:
        has_tables = conn.execute(text(
            \"SELECT 1 FROM information_schema.tables WHERE table_schema='public' LIMIT 1\"
        )).scalar()
        if has_tables:
            print('yes')
")

    if [ "$NEEDS_STAMP" = "yes" ]; then
        echo "Existing DB detected without alembic_version. Stamping as head..."
        alembic stamp head
    fi

    alembic upgrade head
fi

# MIGRATE_ONLY=true の場合はマイグレーションのみ実行して終了する
# （ECS の1回限りタスクとして実行する用途）。
if [ "${MIGRATE_ONLY:-false}" = "true" ]; then
    exit 0
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
