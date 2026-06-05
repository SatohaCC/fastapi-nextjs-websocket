#!/bin/sh
set -e

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

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
