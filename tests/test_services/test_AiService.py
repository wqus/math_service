import pytest
from unittest.mock import AsyncMock
from sqlalchemy.exc import SQLAlchemyError
from bot.services.AIService import AIService

@pytest.mark.asyncio
async def test_get_show_solution_success():
    mock_llm_client = AsyncMock()
    mock_llm_client.chat_completion.return_value = 'solution'

    service = AIService(
        llm_client=mock_llm_client
    )

    result = await service.get_show_solution('expression', 'RU')

    assert result.success == True
    assert result.data['response'] == 'solution'
    mock_llm_client.chat_completion.assert_called_once()

@pytest.mark.asyncio
async def test_get_show_solution_error():
    mock_llm_client = AsyncMock()
    mock_llm_client.chat_completion.side_effect = Exception()

    service = AIService(
        llm_client=mock_llm_client
    )

    result = await service.get_show_solution('expression', 'RU')

    assert result.success == False
    assert result.message_key == 'llm_error'
    mock_llm_client.chat_completion.assert_called_once()


@pytest.mark.asyncio
async def test_get_generate_similar_success():
    mock_llm_client = AsyncMock()
    mock_llm_client.chat_completion.return_value = 'solution'

    service = AIService(
        llm_client=mock_llm_client
    )

    result = await service.get_generate_similar('expression', 'RU')

    assert result.success == True
    assert result.data['response'] == 'solution'
    mock_llm_client.chat_completion.assert_called_once()

@pytest.mark.asyncio
async def test_get_generate_similar_error():
    mock_llm_client = AsyncMock()
    mock_llm_client.chat_completion.side_effect = Exception()

    service = AIService(
        llm_client=mock_llm_client
    )

    result = await service.get_generate_similar('expression', 'RU')

    assert result.success == False
    assert result.message_key == 'llm_error'
    mock_llm_client.chat_completion.assert_called_once()