import sqlite3

user_id_to_delete = '1192730057'

# Подключение к базе данных
conn = sqlite3.connect("bot_data.db")
cursor = conn.cursor()

# Удаление строк с заданным user_id
cursor.execute("""
    DELETE FROM users
    WHERE user_id = ?
""", (user_id_to_delete,))

# Сохраняем изменения
conn.commit()

# Закрываем соединение
conn.close()
