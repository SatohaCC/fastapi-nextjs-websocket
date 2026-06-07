"""LoginRateLimiter のユニットテスト。"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.infrastructure.auth.login_rate_limiter import LoginRateLimiter

TEST_IP = "192.168.1.1"
TEST_USERNAME = "alice"

IP_MAX = 3
IP_WINDOW = 60
USER_MAX = 5
USER_WINDOW = 900


def _make_limiter(mock_redis: MagicMock) -> LoginRateLimiter:
    """モック Redis を注入した LoginRateLimiter を生成します。"""
    with patch("redis.asyncio.from_url", return_value=mock_redis):
        return LoginRateLimiter(
            redis_url="redis://localhost:6379",
            ip_max_attempts=IP_MAX,
            ip_window_seconds=IP_WINDOW,
            user_max_attempts=USER_MAX,
            user_window_seconds=USER_WINDOW,
        )


def _make_pipeline_mock(counts: list[int]) -> MagicMock:
    """pipeline.execute() が counts を順に返すモックを生成します。

    Args:
        counts: pipeline.execute() が返す (incr_result, expire_result) のリスト。
                各要素が 1 回の pipeline 実行に対応する。
    """
    pipeline_mock = MagicMock()
    pipeline_mock.incr = MagicMock()
    pipeline_mock.expire = MagicMock()
    pipeline_mock.execute = AsyncMock(side_effect=[[count, True] for count in counts])
    pipeline_mock.__aenter__ = AsyncMock(return_value=pipeline_mock)
    pipeline_mock.__aexit__ = AsyncMock(return_value=None)
    return pipeline_mock


@pytest.mark.asyncio
async def test_first_attempt_is_not_limited() -> None:
    """初回ログイン試行はレートリミットに抵触しないこと。"""
    mock_redis = MagicMock()
    # user: 1回目, ip: 1回目
    mock_redis.pipeline = MagicMock(
        side_effect=[
            _make_pipeline_mock([1]),  # username check
            _make_pipeline_mock([1]),  # ip check
        ]
    )
    limiter = _make_limiter(mock_redis)

    result = await limiter.is_limited(TEST_IP, TEST_USERNAME)

    assert result is False


@pytest.mark.asyncio
async def test_ip_limit_exceeded_returns_true() -> None:
    """IP アドレスの試行回数が上限を超えた場合に True を返すこと。"""
    mock_redis = MagicMock()
    mock_redis.pipeline = MagicMock(
        side_effect=[
            _make_pipeline_mock([1]),  # username: 1回目（制限内）
            _make_pipeline_mock([IP_MAX + 1]),  # ip: 上限超え
        ]
    )
    limiter = _make_limiter(mock_redis)

    result = await limiter.is_limited(TEST_IP, TEST_USERNAME)

    assert result is True


@pytest.mark.asyncio
async def test_username_limit_exceeded_returns_true() -> None:
    """ユーザー名の試行回数が上限を超えた場合に True を返すこと。"""
    mock_redis = MagicMock()
    mock_redis.pipeline = MagicMock(
        side_effect=[
            _make_pipeline_mock([USER_MAX + 1]),  # username: 上限超え
        ]
    )
    limiter = _make_limiter(mock_redis)

    result = await limiter.is_limited(TEST_IP, TEST_USERNAME)

    assert result is True


@pytest.mark.asyncio
async def test_username_limit_exceeded_skips_ip_check() -> None:
    """ユーザー名が上限超えの場合、IP チェックを実行しないこと。"""
    mock_redis = MagicMock()
    pipeline_call_count = 0

    def pipeline_factory(*args, **kwargs):
        """呼ばれるたびに次のパイプラインモックを返す。"""
        nonlocal pipeline_call_count
        pipeline_call_count += 1
        if pipeline_call_count == 1:
            return _make_pipeline_mock([USER_MAX + 1])
        return _make_pipeline_mock([1])

    mock_redis.pipeline = MagicMock(side_effect=pipeline_factory)
    limiter = _make_limiter(mock_redis)

    await limiter.is_limited(TEST_IP, TEST_USERNAME)

    assert pipeline_call_count == 1


@pytest.mark.asyncio
async def test_no_ip_skips_ip_check() -> None:
    """IP が None の場合、IP チェックを実行しないこと。"""
    mock_redis = MagicMock()
    pipeline_call_count = 0

    def pipeline_factory(*args, **kwargs):
        """呼ばれるたびに次のパイプラインモックを返す。"""
        nonlocal pipeline_call_count
        pipeline_call_count += 1
        return _make_pipeline_mock([1])

    mock_redis.pipeline = MagicMock(side_effect=pipeline_factory)
    limiter = _make_limiter(mock_redis)

    result = await limiter.is_limited(None, TEST_USERNAME)

    assert result is False
    assert pipeline_call_count == 1


@pytest.mark.asyncio
async def test_exactly_at_limit_is_not_limited() -> None:
    """試行回数がちょうど上限値の場合はレートリミットに抵触しないこと。"""
    mock_redis = MagicMock()
    mock_redis.pipeline = MagicMock(
        side_effect=[
            _make_pipeline_mock([USER_MAX]),  # username: ちょうど上限
            _make_pipeline_mock([IP_MAX]),  # ip: ちょうど上限
        ]
    )
    limiter = _make_limiter(mock_redis)

    result = await limiter.is_limited(TEST_IP, TEST_USERNAME)

    assert result is False
