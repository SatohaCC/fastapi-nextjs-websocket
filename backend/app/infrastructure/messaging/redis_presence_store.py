"""Redis を用いたクラスタ全体の在席（presence）ストアの実装。

各接続を有効期限（TTL）付きのエントリとして管理し、複数バックエンド
インスタンス間でも在席ロスターと JOIN/LEAVE 判定を一貫させる。

- ``presence:conns:{username}`` : ソート済み集合。member=conn_id、score=期限
  （epoch 秒）。あるユーザーのアクティブ接続集合を表す。キー自体にも TTL を
  張り、全接続が消えたら自動失効する。
- ``presence:online``           : ソート済み集合。member=username、score=期限。
  在席ロスター。読み取り時に期限切れを掃除（reap）する。

生存中の接続は ``refresh_connection`` で定期的に score を延長する。
グレースフルな停止では各接続の終了処理が ``remove_connection`` を呼んで即時に
減算するが、非グレースフルなクラッシュ（SIGKILL 等）で ``remove_connection`` が
呼ばれなくても、TTL 経過後に期限切れエントリが reap されて在席から外れるため
カウントはリークしない。
"""

import time
from collections.abc import Awaitable
from typing import cast

import redis.asyncio as aioredis

from ...application.interfaces.presence import PresenceStore

_CONNS_KEY_PREFIX = "presence:conns:"
_ONLINE_KEY = "presence:online"
_DEFAULT_TTL_SECONDS = 30


class RedisPresenceStore(PresenceStore):
    """Redis を用いた在席ストアの実装。"""

    def __init__(self, redis_url: str, ttl_seconds: int = _DEFAULT_TTL_SECONDS) -> None:
        """在席ストアを初期化します。

        Args:
            redis_url: 接続先 Redis の URL。
            ttl_seconds: 1 接続あたりの有効期限（秒）。生存中はこの間隔より十分
                短い周期で ``refresh_connection`` を呼ぶ前提。
        """
        self._redis: aioredis.Redis = aioredis.from_url(
            redis_url, socket_keepalive=True, health_check_interval=30
        )
        self._ttl = ttl_seconds

    def _conns_key(self, username: str) -> str:
        return f"{_CONNS_KEY_PREFIX}{username}"

    async def add_connection(self, username: str, conn_id: str) -> bool:
        """接続を 1 つ追加し、初オンライン（0→1）なら True を返します。"""
        key = self._conns_key(username)
        now = time.time()
        deadline = now + self._ttl
        # 先に期限切れの接続を掃除してから、現存接続数を数える。
        await cast("Awaitable[int]", self._redis.zremrangebyscore(key, "-inf", now))
        before = await cast("Awaitable[int]", self._redis.zcard(key))
        await cast("Awaitable[int]", self._redis.zadd(key, {conn_id: deadline}))
        # 全接続が消えた後にキーが残り続けないよう、キー自体にも TTL を張る。
        await cast("Awaitable[bool]", self._redis.expire(key, self._ttl * 2))
        await cast(
            "Awaitable[int]", self._redis.zadd(_ONLINE_KEY, {username: deadline})
        )
        return before == 0

    async def remove_connection(self, username: str, conn_id: str) -> bool:
        """接続を 1 つ削除し、最後の接続が切れたら True を返します。"""
        key = self._conns_key(username)
        now = time.time()
        await cast("Awaitable[int]", self._redis.zrem(key, conn_id))
        await cast("Awaitable[int]", self._redis.zremrangebyscore(key, "-inf", now))
        remaining = await cast("Awaitable[int]", self._redis.zcard(key))
        if remaining == 0:
            await cast("Awaitable[int]", self._redis.delete(key))
            await cast("Awaitable[int]", self._redis.zrem(_ONLINE_KEY, username))
            return True
        return False

    async def refresh_connection(self, username: str, conn_id: str) -> None:
        """接続と在席ロスターの有効期限を延長します。"""
        key = self._conns_key(username)
        deadline = time.time() + self._ttl
        await cast("Awaitable[int]", self._redis.zadd(key, {conn_id: deadline}))
        await cast("Awaitable[bool]", self._redis.expire(key, self._ttl * 2))
        await cast(
            "Awaitable[int]", self._redis.zadd(_ONLINE_KEY, {username: deadline})
        )

    async def online_usernames(self) -> list[str]:
        """現在オンラインのユーザー名一覧（ソート済み）を返します。"""
        now = time.time()
        # 期限切れ（クラッシュで取り残された）ユーザーを掃除してから取得する。
        await cast(
            "Awaitable[int]", self._redis.zremrangebyscore(_ONLINE_KEY, "-inf", now)
        )
        members = await cast(
            "Awaitable[list[bytes]]", self._redis.zrange(_ONLINE_KEY, 0, -1)
        )
        return sorted(
            m.decode("utf-8") if isinstance(m, (bytes, bytearray)) else str(m)
            for m in members
        )
