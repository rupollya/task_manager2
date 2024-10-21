import mysql.connector
from mysql.connector import Error


def create_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name, user=user_name, password=user_password
        )
        print("Подключение к MySQL успешно")
    except Error as e:
        print(f"Ошибка '{e}' при подключении к MySQL")
    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Запрос выполнен успешно")
    except Error as e:
        print(f"Ошибка '{e}' при выполнении запроса")


# Параметры подключения
host = "localhost"
user = "root"
password = "owIbyag820022013"

connection = create_connection(host, user, password)
connection.database = "task_manager"

# insert_users = """ 
# INSERT INTO users (login, password) 
# VALUES ('polina', 'mashkova') 
# """
#execute_query(connection, insert_users)
insert_task = """
INSERT INTO task (user_id, created_at, important, completed, heading, task_text, data_stop, prize) VALUES 
(10, NOW(), TRUE, FALSE, 'Купить продукты', 'Сходить в магазин и купить молоко, хлеб, яйца.', '2023-10-15 18:00:00', 'Угощение на ужин'),
(10, NOW(), TRUE, FALSE, 'Подготовить отчет', 'Собрать данные и подготовить отчет по продажам за квартал.', '2023-10-20 12:00:00', 'Чай с печеньем после завершения'),
(10, NOW(), TRUE, FALSE, 'Написать курсовую работу', 'Исследовать тему и написать минимум 20 страниц.', '2023-11-01 23:59:59', 'Встреча с друзьями после сдачи'),
(10, NOW(), TRUE, FALSE, 'Пробежать марафон', 'Подготовиться к марафону, тренироваться три раза в неделю.', '2023-12-10 09:00:00', 'Покупка новой спортивной формы'),
(10, NOW(), FALSE, TRUE, 'Завершить проект по рисованию', 'Закончить картину и выставить её на выставке.', '2023-10-30 17:00:00', 'Поход в кафе после завершения'),
(10, NOW(), FALSE, FALSE, 'Организовать встречу с друзьями', 'Согласовать дату и место встречи, пригласить всех.', '2023-10-25 19:00:00', 'Веселый вечер с друзьями');

"""
execute_query(connection, insert_task)
connection.commit()
# Закрытие соединения
if connection.is_connected():
    connection.close()
    print("Соединение с MySQL закрыто")
