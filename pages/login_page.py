from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class LoginPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    def goto(self, base_url):
        self.page.goto(f"{base_url}/login")

    def fill_rut(self, rut):
        self.page.locator('input[placeholder*="RUT"]').fill(rut)

    def fill_password(self, password):
        self.page.locator('input[type="password"]').fill(password)

    def click_login(self):
        self.page.locator('button[type="submit"]').click()

    def login(self, rut, password):
        self.fill_rut(rut)
        self.fill_password(password)
        self.click_login()

    def get_error_message(self):
        error = self.page.locator('[role="alert"], .error, .text-red-500, .MuiAlert-root')
        if error.is_visible():
            return error.text_content()
        return None

    def wait_for_dashboard(self):
        self.page.wait_for_url("**/dashboard**", timeout=15000)

    def is_on_login_page(self):
        return "/login" in self.page.url
