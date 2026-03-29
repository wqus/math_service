from keyboards.inline_kbs import page_keyboard


async def format_history_list(rows, next_cursor, prev_cursor, texts, language):
    """
    Форматирует список истории сообщений для отображения.
    """
    pagination_kb = await page_keyboard(next_cursor, prev_cursor)

    history_text = ''
    for row in rows:
        input_message = row['input_message'].replace(">", "&gt;").replace("<", "&lt;")
        output_message = row['output_message'].replace(">", "&gt;").replace("<", "&lt;")
        history_text += f"• {input_message};\t{texts[language]['answer']} <b>{output_message}</b>\n"

    if not history_text:
        history_text = texts[language]['no_history_saves']

    return history_text, pagination_kb