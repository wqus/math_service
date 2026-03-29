from keyboards.inline_kbs import answer_to_ticket_kb, unban_user_kb


async def format_tickets_list(tickets, texts, language) -> list:
    """
    Форматирует список тикетов для отображения.
    """
    tickets_formatted = []
    for ticket in tickets:
        ticket_message = (
            f'Ticket_id: {ticket['id']}\n\nUser_id: {ticket['user_id']}'
            f'\n{ticket['send_time'].strftime("%Y-%m-%d %H:%M")}\n\n"{ticket['message']}"')
        tickets_formatted.append((ticket_message, await answer_to_ticket_kb(ticket['id'], ticket['user_id'],
                                                                            texts[language]['support_answer_bt'])))
    return tickets_formatted


async def format_ban_list(bans: list, texts: dict, language) -> list:
    """
    Форматирует список банов для отображения.
    """
    formatted_ban_list = []
    for ban in bans:
        ban_message = (
            f'<b>Ban ID: {ban['id']}</b>\n\n<b>User ID</b>: {ban['user_id']}'
            f'\n<b>Admin ID:</b>{ban['banned_by']}\n<i>{ban['banned_at'].strftime("%Y-%m-%d %H:%M")}</i>\n\n<b>{texts[language]['reason']}</b>\n{ban['reason']}')
        formatted_ban_list.append((ban_message, await unban_user_kb(ban['user_id'], texts[language]['unban'])))
    return formatted_ban_list