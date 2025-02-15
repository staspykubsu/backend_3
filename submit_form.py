import mysql.connector
from mysql.connector import Error
import cgi

def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host='kubsu-dev.ru',
            user='u68593',
            password='9258357',
            database='u68593'
        )
        print("Подключение к базе данных успешно")
    except Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
    return connection

def validate_form(data):
    errors = []
    if not data['fullname'] or not all(c.isalpha() or c.isspace() for c in data['fullname']):
        errors.append("ФИО должно содержать только буквы и пробелы.")

    if len(data['fullname']) > 150:
        errors.append("ФИО должно быть не длиннее 150 символов.")

    if not data['phone'] or not data['phone'].isdigit():
        errors.append("Телефон должен содержать только цифры.")

    if len(data['phone']) < 10 or len(data['phone']) > 15:
        errors.append("Телефон должен быть длиной от 10 до 15 символов.")

    if not data['email'] or '@' not in data['email'] or '.' not in data['email']:
        errors.append("Некорректный email. Пример: example@domain.com")

    if not data['birthdate']:
        errors.append("Укажите дату рождения.")

    if not data['gender'] or data['gender'] not in ['male', 'female']:
        errors.append("Выберите пол.")

    if not data['languages']:
        errors.append("Выберите хотя бы один язык программирования.")

    if not data['bio'] or len(data['bio'].strip()) < 10:
        errors.append("Биография должна содержать не менее 10 символов.")

    if not data['contract']:
        errors.append("Необходимо подтвердить ознакомление с контрактом.")

    return errors

def insert_user_data(connection, data):
    cursor = connection.cursor()
    try:
        # Вставляем данные в таблицу user_data
        cursor.execute("""
            INSERT INTO user_data (fullname, phone, email, birthdate, gender, bio, contract)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (data['fullname'], data['phone'], data['email'], data['birthdate'], data['gender'], data['bio'], data['contract']))
        
        # Получаем ID вставленной записи
        user_id = cursor.lastrowid

        # Вставляем связи в таблицу user_languages
        for language_id in data['languages']:
            cursor.execute("""
                INSERT INTO user_languages (user_id, language_id)
                VALUES (%s, %s)
            """, (user_id, language_id))
        
        # Фиксируем изменения в базе данных
        connection.commit()
        print("Данные успешно сохранены")
    except Error as e:
        print(f"Ошибка при вставке данных: {e}")
    finally:
        cursor.close()

if __name__ == "__main__":
    form = cgi.FieldStorage()
    data = {
        'fullname': form.getvalue('fullname', '').strip(),
        'phone': form.getvalue('phone', '').strip(),
        'email': form.getvalue('email', '').strip(),
        'birthdate': form.getvalue('birthdate', '').strip(),
        'gender': form.getvalue('gender', '').strip(),
        'languages': form.getlist('languages[]'),
        'bio': form.getvalue('bio', '').strip(),
        'contract': form.getvalue('contract') == 'on'
    }

    errors = validate_form(data)
    if errors:
        print("Content-Type: text/html")
        print()
        print("<h1>Ошибки:</h1>")
        for error in errors:
            print(f"<p>{error}</p>")
    else:
        connection = create_connection()
        if connection:
            insert_user_data(connection, data)
            connection.close()
            print("Content-Type: text/html")
            print()
            print("<h1>Данные успешно сохранены</h1>")