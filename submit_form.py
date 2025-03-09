#!/usr/bin/env python3

import cgi
import pymysql

def create_connection():
    connection = None
    try:
        connection = pymysql.connect(
            host='158.160.150.89',
            user='u68593',
            password='9258357',
            database='web_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
    return connection

def validate_form(data):
    errors = []
    
    if not data['last_name'] or not all(c.isalpha() or c.isspace() for c in data['last_name']):
        errors.append("Фамилия должна содержать только буквы и пробелы.")
    
    if not data['first_name'] or not all(c.isalpha() or c.isspace() for c in data['first_name']):
        errors.append("Имя должно содержать только буквы и пробелы.")
    
    if data['patronymic'] and not all(c.isalpha() or c.isspace() for c in data['patronymic']):
        errors.append("Отчество должно содержать только буквы и пробелы.")
    
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
        cursor.execute("""
            INSERT INTO applications (last_name, first_name, patronymic, phone, email, birthdate, gender, bio, contract)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['last_name'], data['first_name'], data['patronymic'],
            data['phone'], data['email'], data['birthdate'],
            data['gender'], data['bio'], data['contract']
        ))
        
        application_id = cursor.lastrowid

        language_ids = {
            'Pascal': 1,
            'C': 2,
            'C++': 3,
            'JavaScript': 4,
            'PHP': 5,
            'Python': 6,
            'Java': 7,
            'Haskel': 8,
            'Clojure': 9,
            'Prolog': 10,
            'Scala': 11,
            'Go': 12
        }

        for language in data['languages']:
            language_id = language_ids.get(language)
            if language_id:
                cursor.execute("""
                    INSERT INTO application_languages (application_id, language_id)
                    VALUES (%s, %s)
                """, (application_id, language_id))
        
        connection.commit()
    except pymysql.Error as e:
        print(f"Ошибка при вставке данных: {e}")
    finally:
        cursor.close()

if __name__ == "__main__":
    print("Content-Type: text/html; charset=utf-8\n")

    form = cgi.FieldStorage()
    data = {
        'last_name': form.getvalue('last_name', '').strip(),
        'first_name': form.getvalue('first_name', '').strip(),
        'patronymic': form.getvalue('patronymic', '').strip(),
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
        print("<h1>Ошибки:</h1>")
        for error in errors:
            print(f"<p>{error}</p>")
    else:
        connection = create_connection()
        if connection:
            insert_user_data(connection, data)
            connection.close()
            print("<h1>Данные успешно сохранены</h1>")
