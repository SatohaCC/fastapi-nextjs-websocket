"""固定ウィンドウ方式の Redis ベースのレートリミッター。"""

import redis.asyncio as aioredis


class FixedWindowRateLimiter:
    """識別子（ユーザー ID や IP アドレス等）ごとにアクション回数を制限する。

    固定ウィンドウ方式で Redis カウンターを管理し、制限を超えた場合は
    True を返す。カウンター未存在時（初回）は TTL を設定するため、INCR → EXPIRE (NX)
    を 1 パイプラインで実行し、原子性を確保する。
    """

    def __init__(
        self,
        redis_url: str,
        key_prefix: str,
        max_attempts: int,
        window_seconds: int,
    ) -> None:
        """レートリミッターを初期化します。

        Args:
            redis_url: 接続先 Redis の URL。
            key_prefix: Redis キーのプレフィックス（アクション種別ごとに固有のもの）。
            max_attempts: ウィンドウ内の最大許容回数。
            window_seconds: ウィンドウ幅（秒）。
        """
        self._redis: aioredis.Redis = aioredis.from_url(
            redis_url, socket_keepalive=True, health_check_interval=30
        )
        self._key_prefix = key_prefix
        self._max_attempts = max_attempts
        self._window_seconds = window_seconds

    async def is_limited(self, identifier: str) -> bool:
        """レートリミットに抵触するか判定し、カウンターを加算します。

        Args:
            identifier: 制限対象の識別子（ユーザー ID や IP アドレス等）。

        Returns:
            制限に抵触する場合は True、そうでなければ False。
        """
        key = f"{self._key_prefix}{identifier}"
        count = await self._increment(key)
        return count > self._max_attempts

    async def _increment(self, key: str) -> int:
        """指定キーのカウンターをインクリメントし、カウント値を返します。

        カウンターが存在しない場合（初回）は TTL を設定します。
        INCR と EXPIRE NX をパイプラインで実行することで、
        インクリメントと TTL 設定の原子性を保証します。

        Args:
            key: Redis キー。

        Returns:
            インクリメント後のカウント値。
        """
        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.incr(key)
            pipe.expire(key, self._window_seconds, nx=True)
            results = await pipe.execute()
        count: int = results[0]
        return count
