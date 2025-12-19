from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Для flash сообщений

def load_users():
    try:
        with open('users.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        initial_users = [
            {"id": 1, "name": "Иван Иванов", "email": "ivan@example.com", "age": 25, "phone": "+7 (999) 123-45-67",
             "city": "Москва"},
            {"id": 2, "name": "Мария Петрова", "email": "maria@example.com", "age": 30, "phone": "+7 (999) 234-56-78",
             "city": "Санкт-Петербург"},
            {"id": 3, "name": "Алексей Сидоров", "email": "alex@example.com", "age": 22, "phone": "+7 (999) 345-67-89",
             "city": "Казань"}
        ]
        save_users(initial_users)
        return initial_users


def save_users(users):
    with open('users.json', 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


users = load_users()


# Главная страница
@app.route('/')
def index():
    return render_template('index.html',
                           title="Главная страница",
                           current_time=datetime.now().strftime("%H:%M:%S"))


# Страница "О нас"
@app.route('/about')
def about():
    return render_template('about.html', title="О нас")


# Страница "Контакты"
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Здесь можно сохранить сообщение в БД
        flash(f'Спасибо, {name}! Ваше сообщение отправлено.', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html', title="Контакты")


# Страница со списком пользователей
@app.route('/users')
def users_list():
    users = load_users()
    return render_template('users.html',
                           title="Пользователи",
                           users=users,
                           total_users=len(users))


# Форма добавления пользователя
@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        age = request.form.get('age', '').strip()
        phone = request.form.get('phone', '').strip()
        city = request.form.get('city', '').strip()

        # Валидация
        errors = []

        if not name:
            errors.append('Имя обязательно для заполнения')
        if not email:
            errors.append('Email обязателен для заполнения')
        elif '@' not in email:
            errors.append('Некорректный email адрес')

        if not age.isdigit():
            errors.append('Возраст должен быть числом')
        elif int(age) < 0 or int(age) > 150:
            errors.append('Некорректный возраст')

        # Проверка на уникальность email
        users = load_users()
        if any(user['email'].lower() == email.lower() for user in users):
            errors.append('Пользователь с таким email уже существует')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('add_user.html',
                                   title="Добавить пользователя",
                                   form_data=request.form)

        # Создаем нового пользователя
        new_id = max(user['id'] for user in users) + 1 if users else 1
        new_user = {
            "id": new_id,
            "name": name,
            "email": email,
            "age": int(age),
            "phone": phone,
            "city": city,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        users.append(new_user)
        save_users(users)

        flash(f'Пользователь {name} успешно добавлен!', 'success')
        return redirect(url_for('users_list'))

    return render_template('add_user.html', title="Добавить пользователя")


# Редактирование пользователя
@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    users = load_users()
    user = next((u for u in users if u['id'] == user_id), None)

    if not user:
        flash('Пользователь не найден', 'error')
        return redirect(url_for('users_list'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        age = request.form.get('age', '').strip()
        phone = request.form.get('phone', '').strip()
        city = request.form.get('city', '').strip()

        # Валидация
        errors = []

        if not name:
            errors.append('Имя обязательно для заполнения')
        if not email:
            errors.append('Email обязателен для заполнения')
        elif '@' not in email:
            errors.append('Некорректный email адрес')

        if not age.isdigit():
            errors.append('Возраст должен быть числом')
        elif int(age) < 0 or int(age) > 150:
            errors.append('Некорректный возраст')

        # Проверка на уникальность email (исключая текущего пользователя)
        if any(u['email'].lower() == email.lower() and u['id'] != user_id for u in users):
            errors.append('Пользователь с таким email уже существует')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('edit_user.html',
                                   title="Редактировать пользователя",
                                   user=user)

        # Обновляем данные пользователя
        user['name'] = name
        user['email'] = email
        user['age'] = int(age)
        user['phone'] = phone
        user['city'] = city
        user['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        save_users(users)
        flash(f'Данные пользователя {name} успешно обновлены!', 'success')
        return redirect(url_for('users_list'))

    return render_template('edit_user.html',
                           title="Редактировать пользователя",
                           user=user)


# Удаление пользователя
@app.route('/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    users = load_users()
    user = next((u for u in users if u['id'] == user_id), None)

    if user:
        users = [u for u in users if u['id'] != user_id]
        save_users(users)
        flash(f'Пользователь {user["name"]} успешно удален', 'success')
    else:
        flash('Пользователь не найден', 'error')

    return redirect(url_for('users_list'))


# Динамическая страница пользователя
@app.route('/user/<int:user_id>')
def user_profile(user_id):
    users = load_users()
    user = next((u for u in users if u['id'] == user_id), None)
    if user:
        return render_template('user_profile.html',
                               title=f"Профиль: {user['name']}",
                               user=user)
    return "Пользователь не найден", 404


# API endpoint для получения данных о пользователях
@app.route('/api/users')
def api_users():
    users = load_users()
    return jsonify(users)


# API endpoint для получения одного пользователя
@app.route('/api/users/<int:user_id>')
def api_user(user_id):
    users = load_users()
    user = next((u for u in users if u['id'] == user_id), None)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404


# API endpoint для добавления пользователя (JSON)
@app.route('/api/users/add', methods=['POST'])
def api_add_user():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        users = load_users()

        # Валидация
        required_fields = ['name', 'email', 'age']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        # Проверка email
        if any(user['email'].lower() == data['email'].lower() for user in users):
            return jsonify({"error": "User with this email already exists"}), 400

        # Создаем нового пользователя
        new_id = max(user['id'] for user in users) + 1 if users else 1
        new_user = {
            "id": new_id,
            "name": data['name'],
            "email": data['email'],
            "age": int(data['age']),
            "phone": data.get('phone', ''),
            "city": data.get('city', ''),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        users.append(new_user)
        save_users(users)

        return jsonify({
            "success": True,
            "message": "User added successfully",
            "user": new_user
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Простой калькулятор (API endpoint)
@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    a = float(data.get('a', 0))
    b = float(data.get('b', 0))
    operation = data.get('operation', 'add')

    result = 0
    if operation == 'add':
        result = a + b
    elif operation == 'subtract':
        result = a - b
    elif operation == 'multiply':
        result = a * b
    elif operation == 'divide':
        if b != 0:
            result = a / b
        else:
            return jsonify({"error": "Division by zero"}), 400

    return jsonify({"result": result})


# Страница с информацией о сервере
@app.route('/info')
def server_info():
    users = load_users()
    info = {
        "Время на сервере": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Всего пользователей": len(users),
        "Метод запроса": request.method,
        "User-Agent": request.headers.get('User-Agent')
    }
    return render_template('info.html',
                           title="Информация о сервере",
                           info=info)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title="Страница не найдена"), 404


if __name__ == '__main__':
    if not os.path.exists('users.json'):
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)

    app.run(debug=True, port=5000)
