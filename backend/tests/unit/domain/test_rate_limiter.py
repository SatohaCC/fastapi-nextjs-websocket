"""FixedWindowRateLimiter のユニットテスト。"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.infrastructure.rate_limiter import FixedWindowRateLimiter

KEY_PREFIX = "rate_limit:test:"
MAX_ATTEMPTS = 5
WINDOW_SECONDS = 60

TEST_IDENTIFIER = "user-123"


def _make_limiter(mock_redis: MagicMock) -> FixedWindowRateLimiter:
    """モック Redis を注入した FixedWindowRateLimiter を生成します。"""
    with patch("redis.asyncio.from_url", return_value=mock_redis):
        return FixedWindowRateLimiter(
            redis_url="redis://localhost:6379",
            key_prefix=KEY_PREFIX,
            max_attempts=MAX_ATTEMPTS,
            window_seconds=WINDOW_SECONDS,
        )


def _make_pipeline_mock(count: int) -> MagicMock:
    """pipeline.execute() が [count, True] を返すモックを生成します。

    Args:
        count: INCR の結果として返すカウント値。
    """
    pipeline_mock = MagicMock()
    pipeline_mock.incr = MagicMock()
    pipeline_mock.expire = MagicMock()
    pipeline_mock.execute = AsyncMock(return_value=[count, True])
    pipeline_mock.__aenter__ = AsyncMock(return_value=pipeline_mock)
    pipeline_mock.__aexit__ = AsyncMock(return_value=None)
    return pipeline_mock


@pytest.mark.asyncio
async def test_first_attempt_is_not_limited() -> None:
    """初回アクションはレートリミットに抵触しないこと。"""
    mock_redis = MagicMock()
    mock_redis.pipeline = MagicMock(return_value=_make_pipeline_mock(1))
    limiter = _make_limiter(mock_redis)

    result = await limiter.is_limited(TEST_IDENTIFIER)

    assert result is False


@pytest.mark.asyncio
async def test_exceeding_limit_returns_true() -> None:
    """カウントが上限を超えた場合に True を返すこと。"""
    mock_redis = MagicMock()
    mock_redis.pipeline = MagicMock(return_value=_make_pipeline_mock(MAX_ATTEMPTS + 1))
    limiter = _make_limiter(mock_redis)

    result = await limiter.is_limited(TEST_IDENTIFIER)

    assert result is True


@pytest.mark.asyncio
async def test_exactly_at_limit_is_not_limited() -> None:
    """カウントがちょうど上限値の場合はレートリミットに抵触しないこと。"""
    mock_redis = MagicMock()
    mock_redis.pipeline = MagicMock(return_value=_make_pipeline_mock(MAX_ATTEMPTS))
    limiter = _make_limiter(mock_redis)

    result = await limiter.is_limited(TEST_IDENTIFIER)

    assert result is False


@pytest.mark.asyncio
async def test_key_is_prefixed_with_key_prefix() -> None:
    """Redis キーが key_prefix + identifier の形式になること。"""
    mock_redis = MagicMock()
    pipeline_mock = _make_pipeline_mock(1)
    mock_redis.pipeline = MagicMock(return_value=pipeline_mock)
    limiter = _make_limiter(mock_redis)

    await limiter.is_limited(TEST_IDENTIFIER)

    pipeline_mock.incr.assert_called_once_with(f"{KEY_PREFIX}{TEST_IDENTIFIER}")


@pytest.mark.asyncio
async def test_expire_is_set_with_window_and_nx() -> None:
    """TTL がウィンドウ幅で、既存 TTL を上書きしない（NX）こと。"""
    mock_redis = MagicMock()
    pipeline_mock = _make_pipeline_mock(1)
    mock_redis.pipeline = MagicMock(return_value=pipeline_mock)
    limiter = _make_limiter(mock_redis)

    await limiter.is_limited(TEST_IDENTIFIER)

    pipeline_mock.expire.assert_called_once_with(
        f"{KEY_PREFIX}{TEST_IDENTIFIER}", WINDOW_SECONDS, nx=True
    )
