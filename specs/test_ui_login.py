import pytest
from pages.login_page import LoginPage


class TestUILogin:

    def test_login_admin_exitoso(self, page, frontend_url):
        login_page = LoginPage(page)
        login_page.goto(frontend_url)

        login_page.login("12345678-9", "Admin1234!")

        login_page.wait_for_dashboard()
        assert "/dashboard" in page.url

    def test_login_rut_vacio(self, page, frontend_url):
        login_page = LoginPage(page)
        login_page.goto(frontend_url)

        login_page.fill_password("Admin1234!")
        login_page.click_login()

        assert login_page.is_on_login_page()

    def test_login_password_vacio(self, page, frontend_url):
        login_page = LoginPage(page)
        login_page.goto(frontend_url)

        login_page.fill_rut("12345678-9")
        login_page.click_login()

        assert login_page.is_on_login_page()

    def test_login_credenciales_invalidas(self, page, frontend_url):
        login_page = LoginPage(page)
        login_page.goto(frontend_url)

        login_page.login("99999999-9", "WrongPass1!")

        page.wait_for_timeout(1000)
        assert login_page.is_on_login_page()

    def test_flujo_admin_dashboard(self, page, frontend_url):
        login_page = LoginPage(page)
        login_page.goto(frontend_url)
        login_page.login("12345678-9", "Admin1234!")
        login_page.wait_for_dashboard()

        assert "/dashboard" in page.url

        page.wait_for_timeout(500)
        page.screenshot(path="screenshots/dashboard-admin.png")
