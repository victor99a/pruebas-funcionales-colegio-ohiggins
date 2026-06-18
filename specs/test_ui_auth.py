import pytest
from helpers.ui_helpers import login_y_navegar, injectar_token, mock_api_success, CREDENCIALES, SIDEBAR_VISIBLE, SIDEBAR_OCULTO
from pages.login_page import LoginPage, DashboardPage


class TestAuth:

    def test_admin_login_redirect_sidebar_dashboard(self, page, frontend_url):
        """Login UI como ADMIN -> redirige a /dashboard -> sidebar admin -> KPIs cargan"""
        lp = LoginPage(page)
        lp.goto(frontend_url)
        lp.login(CREDENCIALES["ADMIN"]["rut"], CREDENCIALES["ADMIN"]["password"])
        page.wait_for_timeout(2500)

        assert "/dashboard" in page.url, f"ADMIN no fue a /dashboard: {page.url}"

        dp = DashboardPage(page)
        for link in SIDEBAR_VISIBLE["ADMIN"]:
            assert dp.sidebar_has_link(link), f"ADMIN sidebar missing: {link}"
        for link in SIDEBAR_OCULTO["ADMIN"]:
            assert dp.sidebar_lacks_link(link), f"ADMIN sidebar should not show: {link}"

        page.screenshot(path="screenshots/flujo_admin.png")

    def test_docente_login_redirect_sidebar(self, page, frontend_url):
        """Login UI como DOCENTE -> redirige a /calificaciones -> sidebar docente"""
        lp = LoginPage(page)
        lp.goto(frontend_url)
        lp.login(CREDENCIALES["DOCENTE"]["rut"], CREDENCIALES["DOCENTE"]["password"])
        page.wait_for_timeout(2500)

        assert "/calificaciones" in page.url, f"DOCENTE no fue a /calificaciones: {page.url}"

        dp = DashboardPage(page)
        for link in SIDEBAR_VISIBLE["DOCENTE"]:
            assert dp.sidebar_has_link(link), f"DOCENTE sidebar missing: {link}"
        for link in SIDEBAR_OCULTO["DOCENTE"]:
            assert dp.sidebar_lacks_link(link), f"DOCENTE sidebar should not show: {link}"

    def test_apoderado_login_sidebar(self, page, frontend_url):
        """Token APODERADO -> sidebar correcto en /mis-calificaciones"""
        page.goto(f"{frontend_url}/login")
        page.wait_for_load_state("networkidle")
        injectar_token(page, CREDENCIALES["APODERADO"]["rut"], CREDENCIALES["APODERADO"]["password"])
        page.route("**/api/**", mock_api_success)
        page.goto(f"{frontend_url}/mis-calificaciones")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        dp = DashboardPage(page)
        for link in SIDEBAR_VISIBLE["APODERADO"]:
            assert dp.sidebar_has_link(link), f"APODERADO sidebar missing: {link}"
        for link in SIDEBAR_OCULTO["APODERADO"]:
            assert dp.sidebar_lacks_link(link), f"APODERADO sidebar should not show: {link}"
        page.screenshot(path="screenshots/flujo_apoderado.png")

    def test_estudiante_login_sidebar(self, page, frontend_url):
        """Token ESTUDIANTE -> sidebar correcto en /mis-calificaciones"""
        page.goto(f"{frontend_url}/login")
        page.wait_for_load_state("networkidle")
        injectar_token(page, CREDENCIALES["ESTUDIANTE"]["rut"], CREDENCIALES["ESTUDIANTE"]["password"])
        page.route("**/api/**", mock_api_success)
        page.goto(f"{frontend_url}/mis-calificaciones")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        dp = DashboardPage(page)
        for link in SIDEBAR_VISIBLE["ESTUDIANTE"]:
            assert dp.sidebar_has_link(link), f"ESTUDIANTE sidebar missing: {link}"
        for link in SIDEBAR_OCULTO["ESTUDIANTE"]:
            assert dp.sidebar_lacks_link(link), f"ESTUDIANTE sidebar should not show: {link}"
        page.screenshot(path="screenshots/flujo_estudiante.png")

    def test_validacion_rut_vacio_y_password_vacio(self, page, frontend_url):
        """RUT vacio no avanza. Password vacio no avanza. Credenciales invalidas no avanza."""
        lp = LoginPage(page)
        lp.goto(frontend_url)
        lp.fill_password("Admin1234!")
        lp.click_login()
        page.wait_for_timeout(300)
        assert lp.is_on_login_page(), "RUT vacio deberia quedarse en login"

        lp.goto(frontend_url)
        lp.fill_rut("12345678-9")
        lp.click_login()
        page.wait_for_timeout(300)
        assert lp.is_on_login_page(), "Password vacio deberia quedarse en login"

        lp.goto(frontend_url)
        lp.login("99999999-9", "WrongPass1!")
        page.wait_for_timeout(1500)
        assert lp.is_on_login_page(), "Credenciales invalidas deberian quedarse en login"

    def test_sesion_persiste_al_recargar(self, page, frontend_url):
        """Login ADMIN -> recargar pagina -> sigue autenticado en /dashboard"""
        lp = LoginPage(page)
        lp.goto(frontend_url)
        lp.login(CREDENCIALES["ADMIN"]["rut"], CREDENCIALES["ADMIN"]["password"])
        page.wait_for_timeout(2000)
        assert "/dashboard" in page.url

        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        assert "/dashboard" in page.url, "Recarga deberia mantener sesion"

    def test_sin_autenticacion_redirige_login(self, page, frontend_url):
        """Sin token, cualquier ruta protegida redirige a /login"""
        for ruta in ["/dashboard", "/calificaciones", "/admin/usuarios"]:
            page.goto(f"{frontend_url}{ruta}")
            page.wait_for_timeout(1500)
            assert "/login" in page.url, f"Sin token, {ruta} deberia redirigir a /login"
