import pytest
from unittest.mock import AsyncMock
from bot.services.CaсheService import CacheService


@pytest.mark.asyncio
async def test_get_access_data_success():
    mock_redis_client = AsyncMock()
    mock_redis_client.hgetall.return_value = {'role': 'premium', 'premium_until': '2027-01-01'}

    service = CacheService(
        redis_client=mock_redis_client
    )

    result = await service.get_access_data(1)

    assert result == {'role': 'premium', 'premium_until': '2027-01-01'}
    mock_redis_client.hgetall.assert_called_once_with("access:1")


@pytest.mark.asyncio
async def test_get_access_data_error():
    mock_redis_client = AsyncMock()
    mock_redis_client.hgetall.side_effect = Exception()

    service = CacheService(
        redis_client=mock_redis_client
    )

    result = await service.get_access_data(1)

    assert result == {}
    mock_redis_client.hgetall.assert_called_once_with("access:1")


@pytest.mark.asyncio
async def test_set_access_data_success():
    mock_redis = AsyncMock()
    service = CacheService(redis_client=mock_redis)

    await service.set_access_data(user_id=1, role="premium", premium_until="2025-01-01", ttl=600)

    mock_redis.hset.assert_called_once_with(
        "access:1",
        mapping={"role": "premium", "premium_until": "2025-01-01"}
    )

    mock_redis.expire.assert_called_once_with("access:1", 600)


@pytest.mark.asyncio
async def test_set_access_data_error():
    mock_redis = AsyncMock()
    mock_redis.hset.side_effect = Exception("Redis error")
    service = CacheService(redis_client=mock_redis)

    await service.set_access_data(user_id=1, role="premium", premium_until="2025-01-01")

    mock_redis.hset.assert_called_once()
    mock_redis.expire.assert_not_called()


@pytest.mark.asyncio
async def test_invalidate_access_success():
    mock_redis = AsyncMock()
    service = CacheService(redis_client=mock_redis)

    await service.invalidate_access(1)

    mock_redis.delete.assert_called_once_with("access:1")


@pytest.mark.asyncio
async def test_invalidate_access_error():
    mock_redis = AsyncMock()
    mock_redis.delete.side_effect = Exception()
    service = CacheService(redis_client=mock_redis)

    await service.invalidate_access(1)

    mock_redis.delete.assert_called_once_with("access:1")


@pytest.mark.asyncio
async def test_get_attempts_success():
    mock_redis = AsyncMock()
    mock_redis.get.return_value = "5"
    service = CacheService(redis_client=mock_redis)

    result = await service.get_attempts(1)

    assert result == "5"
    mock_redis.get.assert_called_once_with("attempts:1")


@pytest.mark.asyncio
async def test_get_attempts_error():
    mock_redis = AsyncMock()
    mock_redis.get.side_effect = Exception()
    service = CacheService(redis_client=mock_redis)

    result = await service.get_attempts(1)

    assert result is None
    mock_redis.get.assert_called_once_with("attempts:1")


@pytest.mark.asyncio
async def test_set_attempts_success():
    mock_redis = AsyncMock()
    service = CacheService(redis_client=mock_redis)

    await service.set_attempts(1, 5)

    mock_redis.set.assert_called_once_with("attempts:1", 5, ex=600)

@pytest.mark.asyncio
async def test_set_attempts_error():
    mock_redis = AsyncMock()
    mock_redis.set.side_effect = Exception()
    service = CacheService(redis_client=mock_redis)

    await service.set_attempts(1, 5)

    mock_redis.set.assert_called_once_with("attempts:1", 5, ex=600)