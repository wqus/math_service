from sqlalchemy.exc import SQLAlchemyError

from core.ServiceResult import ServiceResult
from repositories.banned_users_repository import BannedRepository
from repositories.support_messages_repository import TicketRepository


class AdminService:
    def __init__(self, ticket_repo: TicketRepository, ban_repo: BannedRepository):
        self.ticket_repo = ticket_repo
        self.ban_repo = ban_repo

    async def create_support_message(self, user_id: int, message: str) -> ServiceResult:
        """
        Сохраняет запрос пользователя в поддержку.
        """
        try:
            ticket_id = await self.ticket_repo.create_support_message(user_id, message)
            return ServiceResult(
                success=True,
                message_key='support_message_saved',
                data={'ticket_id': ticket_id}
            )
        except SQLAlchemyError:
            return ServiceResult(
                success=False,
                message_key='support_message_failed'
            )

    async def fetch_tickets(self, current_position: int = 0) -> ServiceResult:
        """
        Загружает и отображает тикеты для поддержки.
        """
        try:
            tickets = await self.ticket_repo.fetch_open_tickets(current_position)
            has_more = len(tickets) == 4
            last_ticket_id = tickets[-1]['id'] if tickets else None
            return ServiceResult(
                success=True,
                message_key='load_more' if has_more else 'support_no_tickets_to_load',
                data={'tickets': tickets,
                      'has_more': has_more,
                      'last_ticket_id': last_ticket_id})
        except SQLAlchemyError:
            return ServiceResult(
                success=False,
                message_key='fetch_tickets_error',
                data={'tickets': [],
                      'has_more': False,
                      'last_ticket_id': None})

    async def save_support_answer(self, ticket_id: int, answer: str, admin_id: int) -> ServiceResult:
        """
        Сохраняет ответ администратора на тикет.
        """
        try:
            await self.ticket_repo.update_ticket_with_answer(ticket_id, answer, admin_id)
            return ServiceResult(
                success=True,
                message_key='support_success_answer')
        except SQLAlchemyError:
            return ServiceResult(
                success=False,
                message_key='support_failed_answer')

    async def fetch_bans(self, current_position: int = 0) -> ServiceResult:
        """
        Загружает список заблокированных пользователей.
        """
        try:
            bans = await self.ban_repo.fetch_bans(current_position)

            has_more = len(bans) == 4
            last_ban_id = bans[-1]['id'] if bans else None

            return ServiceResult(
                success=True,
                message_key='load_more' if has_more else 'no_bans_to_load',
                data={
                    'bans': bans,
                    'has_more': has_more,
                    'last_ban_id': last_ban_id
                }
            )

        except SQLAlchemyError:
            return ServiceResult(
                success=False,
                message_key='fetch_bans_error',
                data={
                    'bans': [],
                    'has_more': False,
                    'last_ban_id': None
                }
            )