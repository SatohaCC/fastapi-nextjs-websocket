"""ログイン試行に対する Redis ベースのレートリミッター。"""

import redis.asyncio as aioredis


class LoginRateLimiter:
    """IP アドレスおよびユーザー名ごとにログイン試行回数を制限する。

    固定ウィンドウ方式で Redis カウンターを管理し、制限を超えた場合は
    True を返す。カウンター未存在時に TTL を設定するため、INCR → EXPIRE (NX)
    を 1 パイプラインで実行し、原子性を確保する。
    """

    _IP_KEY_PREFIX = "rate_limit:login:ip:"
    _USER_KEY_PREFIX = "rate_limit:login:user:"

    def __init__(
        self,
        redis_url: str,
        ip_max_attempts: int,
        ip_window_seconds: int,
        user_max_attempts: int,
        user_window_seconds: int,
    ) -> None:
        """レートリミッターを初期化します。

        Args:
            redis_url: 接続先 Redis の URL。
            ip_max_attempts: IP アドレスごとの最大試行回数。
            ip_window_seconds: IP アドレスごとのウィンドウ幅（秒）。
            user_max_attempts: ユーザー名ごとの最大試行回数。
            user_window_seconds: ユーザー名ごとのウィンドウ幅（秒）。
        """
        self._redis: aioredis.Redis = aioredis.from_url(
            redis_url, socket_keepalive=True, health_check_interval=30
        )
        self._ip_max = ip_max_attempts
        self._ip_window = ip_window_seconds
        self._user_max = user_max_attempts
        self._user_window = user_window_seconds

    async def is_limited(self, ip: str | None, username: str) -> bool:
        """レートリミットに抵触するか判定し、カウンターを加算します。

        IP ベースおよびユーザー名ベースの両方を確認し、
        どちらか一方でも上限を超えていれば True を返します。

        Args:
            ip: クライアントの IP アドレス。None の場合は IP チェックをスキップ。
            username: ログイン試行のユーザー名。

        Returns:
            制限に抵触する場合は True、そうでなければ False。
        """
        user_key = f"{self._USER_KEY_PREFIX}{username}"
        user_count = await self._increment(user_key, self._user_window)
        if user_count > self._user_max:
            return True

        if ip is not None:
            ip_key = f"{self._IP_KEY_PREFIX}{ip}"
            ip_count = await self._increment(ip_key, self._ip_window)
            if ip_count > self._ip_max:
                return True

        return False

    async def _increment(self, key: str, window_seconds: int) -> int:
        """指定キーのカウンターをインクリメントし、カウント値を返します。

        カウンターが存在しない場合（初回）は TTL を設定します。
        INCR と EXPIRE NX をパイプラインで実行することで、
        インクリメントと TTL 設定の原子性を保証します。

        Args:
            key: Redis キー。
            window_seconds: TTL（秒）。

        Returns:
            インクリメント後のカウント値。
        """
        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.incr(key)
            pipe.expire(key, window_seconds, nx=True)
            results = await pipe.execute()
        count: int = results[0]
        return count
