import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class TestAuthorization(unittest.TestCase):
    """Автотест для проверки авторизации на it-service.club"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        # Инициализация драйвера (укажите путь к chromedriver если нужно)
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.implicitly_wait(5)  # Неявное ожидание
        self.base_url = "https://dev.it-service.club/login"
        
    def tearDown(self):
        """Очистка после каждого теста"""
        self.driver.quit()

    def wait_and_find_element(self, by, value, timeout=10):
        """Вспомогательный метод для ожидания элемента"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def test_successful_login_with_valid_credentials(self):
        """
        Тест №1: Успешная авторизация с валидными учетными данными
        """
        driver = self.driver
        
        # 1. Открываем страницу авторизации
        driver.get(self.base_url)
        
        # 2. Ожидаем загрузки формы и находим поля ввода
        # Поле "Логин" (текстовое поле)
        login_field = self.wait_and_find_element(By.CSS_SELECTOR, "input[type='text'][required]")
        
        # Поле "Пароль"
        password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password'][required]")
        
        # Кнопка "Войти"
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        # 3. Очищаем поля и вводим данные
        login_field.clear()
        login_field.send_keys("iev")  # Валидный логин из вашего примера
        
        password_field.clear()
        password_field.send_keys("dLWCPE20")  # Валидный пароль из вашего примера
        
        # 4. Нажимаем кнопку "Войти"
        login_button.click()
        
        # 5. Проверяем успешную авторизацию
        # Вариант 1: Проверка изменения URL (редирект на другую страницу)
        try:
            WebDriverWait(driver, 10).until(
                EC.url_changes(self.base_url)
            )
            current_url = driver.current_url
            self.assertNotEqual(current_url, self.base_url, 
                              "URL не изменился, авторизация не выполнена")
            print(f"✓ Авторизация успешна! Текущий URL: {current_url}")
        except TimeoutException:
            self.fail("Время ожидания истекло: редирект не произошел")
        
        # Вариант 2: Проверка появления элемента, доступного только авторизованным пользователям
        # (Раскомментируйте, если знаете какой элемент искать)
        # try:
        #     dashboard_element = WebDriverWait(driver, 10).until(
        #         EC.presence_of_element_located((By.CSS_SELECTOR, ".dashboard, .user-menu, .avatar"))
        #     )
        #     self.assertTrue(dashboard_element.is_displayed(), "Элементы дашборда не отображаются")
        # except TimeoutException:
        #     self.fail("Не удалось найти элементы дашборда после авторизации")

    def test_login_with_invalid_password(self):
        """
        Тест №2: Попытка входа с неверным паролем
        """
        driver = self.driver
        driver.get(self.base_url)
        
        # Находим элементы формы
        login_field = self.wait_and_find_element(By.CSS_SELECTOR, "input[type='text'][required]")
        password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password'][required]")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        # Вводим правильный логин, но НЕВЕРНЫЙ пароль
        login_field.clear()
        login_field.send_keys("iev")
        
        password_field.clear()
        password_field.send_keys("wrong_password_123")
        
        # Нажимаем кнопку входа
        login_button.click()
        
        # Проверяем, что остались на странице логина
        current_url = driver.current_url
        self.assertEqual(current_url, self.base_url, 
                        "Произошел редирект при неверном пароле")
        
        # Проверяем наличие сообщения об ошибке
        try:
            # Ищем любое сообщение об ошибке
            error_message = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    "//*[contains(@class, 'error') or contains(@class, 'alert') or contains(text(), 'неверн') or contains(text(), 'ошибк')]"
                ))
            )
            self.assertTrue(error_message.is_displayed(), "Сообщение об ошибке не отображается")
            print(f"✓ Сообщение об ошибке отображено: {error_message.text}")
        except TimeoutException:
            # Если нет сообщения об ошибке, проверяем что поля все еще на месте
            self.assertTrue(login_field.is_displayed() and password_field.is_displayed(), 
                          "Поля ввода исчезли, но сообщения об ошибке нет")
            print("⚠ Сообщение об ошибке не найдено, но пользователь остался на странице логина")

    def test_login_with_empty_fields(self):
        """
        Тест №3: Попытка входа с пустыми полями (проверка HTML5 валидации)
        """
        driver = self.driver
        driver.get(self.base_url)
        
        # Находим кнопку и поля
        login_button = self.wait_and_find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_field = driver.find_element(By.CSS_SELECTOR, "input[type='text'][required]")
        password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password'][required]")
        
        # Очищаем поля (на случай если они предзаполнены)
        login_field.clear()
        password_field.clear()
        
        # Нажимаем кнопку входа
        login_button.click()
        
        # Небольшая пауза для срабатывания валидации
        import time
        time.sleep(1)
        
        # Проверяем атрибут required у полей
        self.assertEqual(login_field.get_attribute("required"), "true", 
                        "Поле логина не имеет атрибута required")
        self.assertEqual(password_field.get_attribute("required"), "true", 
                        "Поле пароля не имеет атрибута required")
        
        # Проверяем, что браузер запросил заполнение полей (через проверку validity)
        is_login_valid = driver.execute_script(
            "return arguments[0].checkValidity();", login_field
        )
        is_password_valid = driver.execute_script(
            "return arguments[0].checkValidity();", password_field
        )
        
        self.assertFalse(is_login_valid, "Валидация пропустила пустое поле логина")
        self.assertFalse(is_password_valid, "Валидация пропустила пустое поле пароля")
        
        # Проверяем, что остались на странице логина (редиректа не произошло)
        self.assertEqual(driver.current_url, self.base_url, 
                        "Произошел редирект при пустых полях")
        
        print("✓ HTML5 валидация отработала корректно")

    def test_login_with_wrong_username(self):
        """
        Тест №4: Попытка входа с несуществующим логином
        """
        driver = self.driver
        driver.get(self.base_url)
        
        # Находим элементы
        login_field = self.wait_and_find_element(By.CSS_SELECTOR, "input[type='text'][required]")
        password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password'][required]")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        # Вводим несуществующий логин
        login_field.clear()
        login_field.send_keys("nonexistent_user_123")
        
        password_field.clear()
        password_field.send_keys("some_password")
        
        login_button.click()
        
        # Ждем возможного сообщения об ошибке
        import time
        time.sleep(2)
        
        # Проверяем, что остались на странице логина
        self.assertIn("/login", driver.current_url, 
                     "Произошел редирект при несуществующем логине")
        
        print("✓ Система корректно отклонила несуществующий логин")

    def test_login_button_exists_and_enabled(self):
        """
        Тест №5: Проверка наличия и доступности кнопки входа
        """
        driver = self.driver
        driver.get(self.base_url)
        
        # Проверяем наличие кнопки
        login_button = self.wait_and_find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        # Проверяем, что кнопка отображается
        self.assertTrue(login_button.is_displayed(), "Кнопка 'Войти' не отображается")
        
        # Проверяем, что кнопка активна (не disabled)
        self.assertTrue(login_button.is_enabled(), "Кнопка 'Войти' неактивна (disabled)")
        
        # Проверяем текст кнопки
        button_text = login_button.text
        self.assertIn("Войти", button_text, f"Неверный текст на кнопке: {button_text}")
        
        print("✓ Кнопка 'Войти' присутствует, активна и имеет правильный текст")


if __name__ == "__main__":
    # Запуск всех тестов
    # Чтобы запустить конкретный тест, используйте:
    # unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    # Запуск с подробным выводом
    unittest.main(verbosity=2)