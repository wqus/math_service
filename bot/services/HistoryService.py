from sqlalchemy.exc import SQLAlchemyError

from core.ServiceResult import ServiceResult
from repositories.history_repository import HistoryRepository


class HistoryService:
    def __init__(self, repo: HistoryRepository):
        self.repo = repo

    async def get_user_history(
            self,
            user_id: int,
            cursor: tuple | None = None,
            direction: str = "next"
    ) -> ServiceResult:
        """
        Возвращает историю сообщений пользователя с пагинацией.
        """
        try:
            rows = await self.repo.fetch_user_history(user_id, cursor, direction=direction)

            prev_cursor, next_cursor = None, None

            if rows:
                if direction == "prev":
                    rows.reverse()

                first = rows[0]
                last = rows[-1]

                if await self.repo.has_newer_records(user_id, first["created_at"], first["id"]):
                    prev_cursor = (first["id"], first["created_at"])

                if await self.repo.has_older_records(user_id, last["created_at"], last["id"]):
                    next_cursor = (last["id"], last["created_at"])

            return ServiceResult(
                success=True,
                message_key="history_answer",
                data={
                    "rows": rows,
                    "prev_cursor": prev_cursor,
                    "next_cursor": next_cursor
                }
            )

        except SQLAlchemyError:
            return ServiceResult(
                success=False,
                message_key="history_error",
                data={"rows": [], "prev_cursor": None, "next_cursor": None}
            )

    async def save_message(
            self,
            user_id: int,
            input_text: str,
            output_text: str
    ) -> None:
        """
        Сохраняет сообщение пользователя (фоновая операция).
        """
        await self.repo.create_message_record(user_id, input_text, output_text)
