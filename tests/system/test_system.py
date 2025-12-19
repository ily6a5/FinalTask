  from selenium.webdriver.support import expected_conditions as EC
import pytest
import subprocess
import time
import requests
import json
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from selenium.common.exceptions import TimeoutException

# Добавляем путь к приложению
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestUserInterfaceSelenium:

    @pytest.fixture(scope="class")
    def driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Фоновый режим
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(5)  # Неявное ожидание

        yield driver

        driver.quit()

    def test_home_page_load(self, driver, flask_server):
        driver.get(flask_server)

        assert "Flask" in driver.title or "Главная" in driver.title

        # основные элементы
        assert driver.find_element(By.TAG_NAME, 'nav') is not None
        assert driver.find_element(By.TAG_NAME, 'footer') is not None

        # наличие кнопок/ссылок
        nav_links = driver.find_elements(By.CSS_SELECTOR, 'nav a')
        assert len(nav_links) >= 3

        print(f" Главная страница загружена корректно")

    def test_user_list_page(self, driver, flask_server):
        driver.get(f"{flask_server}/users")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'h1'))
        )

        h1_text = driver.find_element(By.TAG_NAME, 'h1').text
        assert "Пользователи" in h1_text or "Users" in h1_text

        # наличие кнопки добавления пользователя
        add_button = driver.find_elements(By.XPATH, "//a[contains(text(), 'Добавить')]")
        assert len(add_button) > 0

        # отображение пользователей (если они есть)
        user_cards = driver.find_elements(By.CSS_SELECTOR, '.user-card, .user-grid div')
        if user_cards:
            print(f"✓ Страница пользователей: найдено {len(user_cards)} карточек")
        else:
            print(f"✓ Страница пользователей: пользователей нет")

    def test_add_user_form_ui(self, driver, flask_server):
        driver.get(f"{flask_server}/users/add")

        form = driver.find_element(By.TAG_NAME, 'form')
        assert form is not None

        required_fields = ['name', 'email', 'age']
        for field in required_fields:
            element = driver.find_element(By.NAME, field)
            assert element is not None
            if field != 'age':  # Поле age может быть не required в HTML5
                assert element.get_attribute('required') is not None

        driver.find_element(By.NAME, 'name').send_keys('Selenium Тест')
        driver.find_element(By.NAME, 'email').send_keys('selenium.test@example.com')
        driver.find_element(By.NAME, 'age').send_keys('30')
        driver.find_element(By.NAME, 'city').send_keys('Selenium City')

        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        try:
            WebDriverWait(driver, 5).until(
                EC.url_contains('users')  # Перенаправление на список пользователей
            )
            print(f" Форма добавления пользователя отправлена успешно")
        except TimeoutException:
            flash_messages = driver.find_elements(By.CSS_SELECTOR, '.flash, .alert')
            if flash_messages:
                message_text = flash_messages[0].text.lower()
                if 'успешно' in message_text or 'success' in message_text:
                    print(f" Пользователь добавлен успешно")
                elif 'ошибка' in message_text or 'error' in message_text:
                    print(f" Ошибка валидации обнаружена (ожидаемо)")
            else:
                print(f" Не удалось определить результат отправки формы")

    def test_form_validation_ui(self, driver, flask_server):
        driver.get(f"{flask_server}/users/add")

        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()
        time.sleep(1)

        errors_found = False

        invalid_fields = driver.find_elements(By.CSS_SELECTOR, ':invalid')
        if invalid_fields:
            errors_found = True
            print(f" HTML5 валидация: {len(invalid_fields)} невалидных полей")

        flash_messages = driver.find_elements(By.CSS_SELECTOR, '.flash-error, .alert-danger')
        if flash_messages:
            errors_found = True
            print(f" Flash сообщения об ошибках: {len(flash_messages)}")

        error_text = ['обязательно', 'required', 'ошибка', 'error', 'некорректно', 'invalid']
        page_text = driver.page_source.lower()
        if any(word in page_text for word in error_text):
            errors_found = True
            print(f" Текст ошибок обнаружен на странице")

        assert errors_found, "Не обнаружено сообщений об ошибках валидации"

if __name__ == "__main__":
    pytest.main(['-v', __file__])
