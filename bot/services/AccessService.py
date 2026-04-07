from datetime import datetime, timezone
import logging

from sqlalchemy.exc import SQLAlchemyError

from core.ServiceResult import ServiceResult
from repositories.admins_repository import AdminRepository
from repositories.banned_users_repository import BannedRepository
from repositories.users_repository import UserRepository
from services.CaсheService import CacheService

logger = logging.getLogger(__name__)


class AccessService:
    def __init__(self, users_repo: UserRepository, ban_repo: BannedRepository, admins_repo: AdminRepository, cache: CacheService):
        self.users_repo = users_repo
        self.ban_repo = ban_repo
        self.admins_repo = admins_repo
        self.cache = cache

    async def get_user_role(self, user_id: int) -> str:
        """
        Проверяет роль пользователя (с кешем).
        """
        try:
            cached = await self.cache.get_access_data(user_id)

            if cached:
                premium_until = cached.get("premium_until")

                if premium_until and premium_until != "None":
                    if datetime.fromisoformat(premium_until) > datetime.now(timezone.utc):
                        return cached.get("role")

            # идём в БД
            premium_until, role = await self.users_repo.fetch_user_access(user_id)
            premium_until = str(premium_until)
            await self.cache.set_access_data(user_id, role, premium_until)

            return role

        except Exception:
            logger.exception(f"Ошибка при проверке роли user={user_id}")
            return "normal"

    async def invalidate_access_cache(self, user_id: int):
        """
        Инвалидирует кеш пользователя.
        """
        await self.cache.invalidate_access(user_id)

    async def has_attempts_left(self, user_id: int) -> bool:
        """
        Проверяет наличие бесплатных попыток.
        """
        try:
            attempts = await self.cache.get_attempts(user_id)

            if attempts is not None:
                return int(attempts) > 0

            return await self.users_repo.check_and_reset_attempts(user_id)

        except Exception:
            logger.exception(f"Ошибка при проверке попыток user={user_id}")
            return True

    async def decrease_attempts(self, user_id: int) -> int:
        """
        Уменьшает количество попыток.
        """
        try:
            attempts = await self.users_repo.decrease_attempts(user_id)

            await self.cache.set_attempts(user_id, attempts)

            return attempts

        except Exception:
            logger.exception(f"Ошибка при уменьшении попыток user={user_id}")
            return 1

    async def ban_user(self, user_id: int, admin_id: int, reason: str) -> ServiceResult:
        """
        Блокирует пользователя.
        """
        try:
            await self.ban_repo.ban_user(user_id, admin_id, reason)
            await self.invalidate_access_cache(user_id)

            return ServiceResult(success=True, message_key="user_was_banned_successful")

        except SQLAlchemyError:
            return ServiceResult(success=False, message_key="user_was_banned_unsuccessful")

    async def unban_user(self, user_id: int) -> ServiceResult:
        """
        Разблокирует пользователя.
        """
        try:
            await self.ban_repo.unban_user(user_id)
            await self.invalidate_access_cache(user_id)

            return ServiceResult(success=True, message_key="successful_unban")

        except SQLAlchemyError:
            return ServiceResult(success=False, message_key="unsuccessful_unban")

    async def assign_admin(self, user_id: int) -> ServiceResult:
        """
        Назначает пользователя администратором.
        """
        try:
            await self.admins_repo.add_admin(user_id)
            await self.invalidate_access_cache(user_id)

            return ServiceResult(success=True, message_key="add_admin_successful")

        except SQLAlchemyError:
            return ServiceResult(success=False, message_key="add_admin_unsuccessful")

    async def remove_admin(self, user_id: int) -> ServiceResult:
        """
        Удаляет роль администратора.
        """
        try:
            await self.admins_repo.remove_admin(user_id)
            await self.invalidate_access_cache(user_id)

            return ServiceResult(success=True, message_key="remove_admin_successful")

        except SQLAlchemyError:
            return ServiceResult(success=False, message_key="remove_admin_unsuccessful")
