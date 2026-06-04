import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fontTools.misc.cython import returns

from bot.startup import init_bot, init_redis, load_texts
import json


@pytest.mark.asyncio
async def test_init_redis_success():
    mock_client = AsyncMock()

    with patch("bot.startup.redis.Redis", new_callable=AsyncMock) as mock_redis:
        mock_redis.return_value = mock_client

        result = await init_redis()

        assert result is mock_client
        mock_client.ping.assert_awaited_once()


@pytest.mark.asyncio
async def test_init_redis_fail():
    with patch('bot.startup.redis.Redis') as mock_redis:
        mock_redis.side_effect = Exception("Connection failed")

        with pytest.raises(Exception):
            await init_redis()


@pytest.mark.asyncio
async def test_init_bot_success():
    with patch('bot.startup.Bot') as mock_bot, patch('bot.startup.init_redis') as mock_init_redis, patch(
            'bot.startup.RedisStorage'), patch('bot.startup.Dispatcher') as mock_dispatcher:
        mock_bot_instance = AsyncMock()
        mock_bot.return_value = mock_bot_instance

        mock_redis_client = AsyncMock()
        mock_init_redis.return_value = mock_redis_client

        mock_dp_instance = MagicMock()
        mock_dispatcher.return_value = mock_dp_instance

        bot, dp, redis_client = await init_bot()

        assert bot == mock_bot_instance
        assert dp == mock_dp_instance
        assert redis_client == mock_redis_client
        mock_dp_instance.include_routers.assert_called_once()


@pytest.mark.asyncio
async def test_load_texts_success():
    mock_file = AsyncMock()
    mock_file.__aenter__ = AsyncMock(return_value=mock_file)
    mock_file.read = AsyncMock()

    mock_file.read.side_effect = [
        json.dumps({"hello": "Привет"}),
        json.dumps({"hello": "Hello"})
    ]

    with patch('bot.startup.aiofiles.open', return_value=mock_file):
        result = await load_texts()

        assert 'language:RU' in result
        assert 'language:EN' in result
        assert result['language:RU']['hello'] == 'Привет'
        assert result['language:EN']['hello'] == 'Hello'
