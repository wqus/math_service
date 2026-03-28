import logging

from sqlalchemy.exc import SQLAlchemyError
from bot.repositories.users_repository import UserRepository

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def init_user(self, user_id: int) -> None:
        """
        Инициализирует пользователя (если не существует).
        Ничего не возвращает.
        """
        try:
            await self.repo.create_user_if_not_exists(user_id)
        except SQLAlchemyError:
            logger.exception(f"Ошибка при уменьшении попыток user={user_id}")

    async def update_user_language(
            self,
            user_id: int,
            language: str
    ) -> bool:
        """
        Обновляет язык пользователя.

        Возвращает:
        - True → язык успешно обновлён
        - False → ошибка
        """
        try:
            return await self.repo.update_user_language(user_id, language)
        except SQLAlchemyError:
            return False
