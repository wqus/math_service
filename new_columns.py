import sqlite3

def check_and_add_column(db_path, table, column, ctype="TEXT", default_value=None):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Получаем информацию о таблице
    cursor.execute(f"PRAGMA table_info({table})")
    columns_info = cursor.fetchall()
    existing_columns = [col[1] for col in columns_info]

    # Проверяем, существует ли столбец
    if column in existing_columns:
        print(f"Столбец {column} уже существует")
        return False

    # Формируем запрос с дефолтным значением
    try:
        if default_value is not None:
            # Экранируем строковые значения
            if isinstance(default_value, str):
                default_sql = f"DEFAULT '{default_value}'"
            else:
                default_sql = f"DEFAULT {default_value}"
        else:
            default_sql = ""

        sql = f"ALTER TABLE {table} ADD COLUMN {column} {ctype} {default_sql}"
        cursor.execute(sql)
        conn.commit()
        print(f"Столбец {column} успешно добавлен с DEFAULT {default_value}")
        return True
    except sqlite3.Error as e:
        print(f"Ошибка: {e}")
        return False
    finally:
        conn.close()
check_and_add_column("bot_data.db", "users", "user_states", "TEXT", default_value="nothing")
