import mysql.connector 
from mysql.connector import Error 

def create_connection(host_name, user_name, user_password): 
    connection = None 
    try: 
        connection = mysql.connector.connect( 
            host=host_name, 
            user=user_name, 
            password=user_password 
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

# Создание подключения 
connection = create_connection(host, user, password) 

# Создание базы данных 
create_database_query = "CREATE DATABASE IF NOT EXISTS task_manager" 
execute_query(connection, create_database_query) 

# Подключение к созданной базе данных 
connection.database = 'task_manager' 

# Создание таблицы 'users' 
create_users = """ 
CREATE TABLE IF NOT EXISTS users ( 
    user_id INT PRIMARY KEY AUTO_INCREMENT, 
    login VARCHAR(255) NOT NULL, 
    password VARCHAR(255) NOT NULL 
); 
""" 
execute_query(connection, create_users) 

# Создание таблицы 'task' 
create_task = """ 
CREATE TABLE IF NOT EXISTS task ( 
    task_id INT PRIMARY KEY AUTO_INCREMENT, 
    user_id INT, 
    created_at DATETIME, 
    important BOOLEAN DEFAULT FALSE, 
    completed BOOLEAN DEFAULT FALSE, 
    heading TEXT, 
    task_text TEXT, 
    data_stop DATETIME, 
    prize TEXT, 
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE 
); 
""" 
execute_query(connection, create_task) 



# Закрытие соединения 
if connection.is_connected(): 
    connection.close() 
    print("Соединение с MySQL закрыто")
