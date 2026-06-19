from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class LoginPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    def goto(self, base_url):
        self._log("NAV", f"{base_url}/login")
        self.page.goto(f"{base_url}/login")

    def fill_rut(self, rut):
        self.fill(self.page.locator('#rut'), rut, "RUT")

    def fill_password(self, password):
        self.fill(self.page.locator('#password'), password, "Password")

    def click_login(self):
        self.click(self.page.locator('button.register-form__btn'), "Botón Entrar")

    def login(self, rut, password):
        self.fill_rut(rut)
        self.fill_password(password)
        self.click_login()

    def get_error_message(self):
        error = self.page.locator('.register-form__error')
        if error.is_visible():
            return error.text_content()
        return None

    def wait_for_dashboard(self):
        self._log("WAIT", "URL contiene /dashboard")
        self.page.wait_for_url("**/dashboard**", timeout=15000)

    def is_on_login_page(self):
        return "/login" in self.page.url


class DashboardPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    def get_sidebar_link_texts(self):
        self.page.wait_for_timeout(1000)
        links = self.page.locator('.sidebar__link')
        count = links.count()
        texts = []
        for i in range(count):
            text = links.nth(i).text_content() or ""
            texts.append(text.strip())
        self.info(f"Sidebar: {len(texts)} links → {texts}")
        return texts

    def sidebar_has_link(self, label):
        self._log("CHECK", f"Sidebar contiene '{label}'")
        self.page.wait_for_timeout(500)
        links = self.page.locator(f'.sidebar a:has-text("{label}")')
        found = links.count() > 0 and links.first.is_visible()
        self._log("CHECK", f"Sidebar contiene '{label}'", found)
        return found

    def sidebar_lacks_link(self, label):
        self._log("CHECK", f"Sidebar NO contiene '{label}'")
        links = self.page.locator(f'.sidebar a:has-text("{label}")')
        missing = links.count() == 0
        self._log("CHECK", f"Sidebar NO contiene '{label}'", missing)
        return missing

    def navigate_to(self, path, base_url):
        self.navigate(f"{base_url}{path}")

    def is_on_page(self, path_segment):
        return path_segment in self.page.url
