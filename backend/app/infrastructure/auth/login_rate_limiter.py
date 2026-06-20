"""ログイン試行に対する Redis ベースのレートリミッター。"""

from ..rate_limiter import FixedWindowRateLimiter


class LoginRateLimiter:
    """IP アドレスおよびユーザー名ごとにログイン試行回数を制限する。

    IP 用・ユーザー名用の 2 つの FixedWindowRateLimiter に委譲し、
    どちらか一方でも上限を超えていれば制限と判定する。
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
        self._user_limiter = FixedWindowRateLimiter(
            redis_url=redis_url,
            key_prefix=self._USER_KEY_PREFIX,
            max_attempts=user_max_attempts,
            window_seconds=user_window_seconds,
        )
        self._ip_limiter = FixedWindowRateLimiter(
            redis_url=redis_url,
            key_prefix=self._IP_KEY_PREFIX,
            max_attempts=ip_max_attempts,
            window_seconds=ip_window_seconds,
        )

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
        if await self._user_limiter.is_limited(username):
            return True

        if ip is not None and await self._ip_limiter.is_limited(ip):
            return True

        return False
