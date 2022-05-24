# Current test is checking adding several Large Duck to cart and removing it from cart
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pytest

import allure
from selenium.webdriver.support.wait import WebDriverWait
from allure_commons.types import AttachmentType

class Helper:
    def __init__(self):
        self.browser = webdriver.Chrome()
        self.browser.maximize_window()
        self.browser.implicitly_wait(10)
        self.url = 'https://litecart.stqa.ru/en/'

    # Method for opening start-page (url) in browser
    def open_start_page(self):
        self.browser.get(self.url)

    # Method which realising business-logic of duck purchasing
    def put_duck_to_cart(self, duck_quantity):
        if self.cart_is_empty():
            self.browser.find_element(By.CSS_SELECTOR, '.box#box-campaigns .campaign-price').click()
            self.browser.find_element(By.CSS_SELECTOR, '.buy_now table tr td.options select[name="options[Size]"] option[value="Large"]').click()
            self.browser.find_element(By.CSS_SELECTOR, '.buy_now .quantity [type="number"][name="quantity"]').clear()
            self.browser.find_element(By.CSS_SELECTOR, '.buy_now .quantity [type="number"][name="quantity"]').send_keys(duck_quantity)
            self.browser.find_element(By.CSS_SELECTOR, '.buy_now form[name="buy_now_form"] td.quantity button[type="submit"]').click()

    # Method which realising business-logic of removing duck from user's filled cart
    def remove_duck_from_cart(self):
        if self.cart_is_filled():
            self.browser.find_element(By.CSS_SELECTOR, '#cart-wrapper #cart .image img[style]').click()
            self.browser.find_element(By.CSS_SELECTOR, '.items .item button[name="remove_cart_item"]').click()
            if self.back_link_is_present():
                self.browser.find_element(By.XPATH, '//*[@id="checkout-cart-wrapper"]/p[2]/a').click()

    # Method closes browser window
    def quit(self):
        self.browser.quit()

    # Additional method - current state of needed element on UI
    def element_state(self, method, locator):
        self.browser.implicitly_wait(2)
        try:
            self.browser.find_element(method, locator)
            return True
        except NoSuchElementException:
            return False
        finally:
            self.browser.implicitly_wait(3)

    # Additional method - defines that empty cart icon is presented on UI by CSS-locator or not
    def cart_is_empty(self):
        return self.element_state(By.CSS_SELECTOR,
                                  '#header-wrapper #header .image [src="/includes/templates/default.catalog/images/cart.png"]')

    # Additional method - defines that filled cart icon is presented on UI by CSS-locator or not
    def cart_is_filled(self):
        return self.element_state(By.CSS_SELECTOR,
            '#header-wrapper #header .image [src="/includes/templates/default.catalog/images/cart_filled.png"]')

    # Additional method - defines and returns current quantity of goods in cart (number in icon on header)
    def current_quantity_in_cart(self):
        return self.browser.find_element(By.CSS_SELECTOR, '#cart-wrapper #cart .quantity').text

    # Additional method - defines that "back" link is presented on UI by XPath-locator or not
    def back_link_is_present(self):
        return self.element_state(By.XPATH, '//*[@id="checkout-cart-wrapper"]/p[2]/a')

    # Additional method - provides screenshots for tests
    def screen_shot(self, name):
        wait = WebDriverWait(self.browser, 5)
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        allure.attach(self.browser.get_screenshot_as_png(), name=name, attachment_type=AttachmentType.PNG)


fixture = None
@pytest.fixture()
def app():
    global fixture
    if fixture is None:
        fixture = Helper()
        fixture.open_start_page()

    fixture.screen_shot("Стартовая страница магазина успешно открыта")
    return fixture

@pytest.fixture(autouse=True, scope='session')
def stop(request):
    def teardown():
        fixture.quit()
    request.addfinalizer(teardown)


@pytest.mark.parametrize('duck_quantity', [1, 15, 30])
def test_suite_add_and_remove_several_ducks(app, duck_quantity):
    with allure.step('Положить уточку в корзину'):
        app.put_duck_to_cart(duck_quantity)

        assert app.cart_is_filled() is True, \
            "Возникла проблема на начальном этапе добавления товара в корзину!!!"
        assert app.current_quantity_in_cart() == str(duck_quantity), \
            f"Количество товара заданное пользователем {str(duck_quantity)} не совпадает с количеством товара, " \
            f"положенного в корзину - {app.current_quantity_in_cart()}!!!"
        app.screen_shot("Выбранный товар успешно добавлен в корзину")

    with allure.step('Удалить уточку из корзины'):
        app.remove_duck_from_cart()
        app.screen_shot("Выбранный товар успешно удалён из корзины")
        assert app.cart_is_empty() is True, \
            "Возникла проблема на конечном этапе возврата на стартовую страницу после удаления товара из корзины!!!"
        assert app.current_quantity_in_cart() == '0', \
            f"Финальное состояние корзины на стартовой странице после удаления товаров - не пуста, " \
            f"в корзине не {app.current_quantity_in_cart()} товаров!!!"