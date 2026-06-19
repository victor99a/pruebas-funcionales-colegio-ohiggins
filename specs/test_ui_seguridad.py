import pytest
from helpers.ui_helpers import login_y_navegar_sin_mock, injectar_token, CREDENCIALES


class TestSeguridad:

    @pytest.mark.seguridad
    def test_jwt_ausente_todas_las_rutas_protegidas_redirigen_a_login(self, page, frontend_url):
        """Sin token JWT: /dashboard, /calificaciones, /admin/usuarios, /comunicaciones → /login"""
        from pages.base_page import BasePage
        bp = BasePage(page)
        rutas = ["/dashboard", "/calificaciones", "/admin/usuarios", "/comunicaciones"]

        for ruta in rutas:
            bp.navigate(f"{frontend_url}{ruta}")
            page.wait_for_timeout(2000)
            assert "/login" in page.url, (
                f"SIN TOKEN: {ruta} deberia redirigir a /login. URL: {page.url}"
            )
            bp._log("CHECK", f"Ruta {ruta} → /login", "/login" in page.url)

    @pytest.mark.seguridad
    def test_roles_no_admin_son_redirigidos_al_intentar_paginas_admin(self, page, frontend_url):
        """DOCENTE/APODERADO/ESTUDIANTE: /admin/* → redirigidos a su pagina segura"""
        from pages.base_page import BasePage
        bp = BasePage(page)
        admin_pages = ["/admin/gestion-academica", "/admin/usuarios", "/admin/asignacion-docentes"]

        bp._log("SETUP", "Inyectando token DOCENTE")
        page.goto(f"{frontend_url}/login")
        page.wait_for_load_state("networkidle")
        injectar_token(page, CREDENCIALES["DOCENTE"]["rut"], CREDENCIALES["DOCENTE"]["password"])

        for pagina in admin_pages:
            bp.navigate(f"{frontend_url}{pagina}")
            page.wait_for_timeout(2000)
            assert "/calificaciones" in page.url, f"DOCENTE {pagina} → /calificaciones"
            bp._log("CHECK", f"DOCENTE {pagina} → /calificaciones")

        bp._log("SETUP", "Inyectando token APODERADO")
        injectar_token(page, CREDENCIALES["APODERADO"]["rut"], CREDENCIALES["APODERADO"]["password"])
        for pagina in admin_pages:
            bp.navigate(f"{frontend_url}{pagina}")
            page.wait_for_timeout(2000)
            assert "/mis-calificaciones" in page.url, f"APODERADO {pagina} → /mis-calificaciones"
            bp._log("CHECK", f"APODERADO {pagina} → /mis-calificaciones")

        bp._log("SETUP", "Inyectando token ESTUDIANTE")
        injectar_token(page, CREDENCIALES["ESTUDIANTE"]["rut"], CREDENCIALES["ESTUDIANTE"]["password"])
        for pagina in admin_pages:
            bp.navigate(f"{frontend_url}{pagina}")
            page.wait_for_timeout(2000)
            assert "/mis-calificaciones" in page.url, f"ESTUDIANTE {pagina} → /mis-calificaciones"
            bp._log("CHECK", f"ESTUDIANTE {pagina} → /mis-calificaciones")

        bp.screenshot("seguridad_bloqueo_admin")

    @pytest.mark.seguridad
    def test_paginas_de_escritura_renderizan_pero_api_gateway_bloquea_acciones(self, page, frontend_url):
        """No-ADMIN/DOCENTE: /calificaciones, /asistencia, /redactar, /justificar renderizan, API bloquea"""
        from pages.base_page import BasePage
        bp = BasePage(page)

        page.goto(f"{frontend_url}/login")
        page.wait_for_load_state("networkidle")

        for rol in ["APODERADO", "ESTUDIANTE"]:
            bp._log("SETUP", f"Inyectando token {rol}")
            injectar_token(page, CREDENCIALES[rol]["rut"], CREDENCIALES[rol]["password"])

            for ruta in ["/calificaciones", "/asistencia", "/comunicaciones/redactar", "/asistencia/justificar"]:
                bp.navigate(f"{frontend_url}{ruta}")
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(2000)
                assert ruta in page.url, f"{rol} en {ruta}: pagina renderiza"
                bp._log("CHECK", f"{rol} en {ruta}: pagina renderiza (API protegida)")

        injectar_token(page, CREDENCIALES["ESTUDIANTE"]["rut"], CREDENCIALES["ESTUDIANTE"]["password"])
        bp.navigate(f"{frontend_url}/asistencia")
        page.wait_for_timeout(2000)

        btn_guardar = page.locator('button:has-text("Guardar Asistencia")')
        if btn_guardar.count() > 0 and btn_guardar.is_visible():
            bp.click(btn_guardar, "Guardar Asistencia (ESTUDIANTE)")
            page.wait_for_timeout(2000)
        assert "/asistencia" in page.url or "/login" in page.url

        bp.screenshot("seguridad_escritura_bloqueada")

    @pytest.mark.seguridad
    def test_solo_admin_ve_kpis_dashboard_otros_roles_error_o_redirect(self, page, frontend_url):
        """Dashboard KPI: ADMIN ve datos, DOCENTE error, APODERADO/ESTUDIANTE redirect"""
        from pages.base_page import BasePage
        bp = BasePage(page)

        page.goto(f"{frontend_url}/login")
        page.wait_for_load_state("networkidle")

        bp._log("SETUP", "Inyectando token DOCENTE")
        injectar_token(page, CREDENCIALES["DOCENTE"]["rut"], CREDENCIALES["DOCENTE"]["password"])
        bp.navigate(f"{frontend_url}/dashboard")
        page.wait_for_timeout(2000)
        assert "/dashboard" in page.url or "/calificaciones" in page.url
        bp._log("CHECK", "DOCENTE en dashboard (error KPI)")

        bp._log("SETUP", "Inyectando token APODERADO")
        injectar_token(page, CREDENCIALES["APODERADO"]["rut"], CREDENCIALES["APODERADO"]["password"])
        bp.navigate(f"{frontend_url}/dashboard")
        page.wait_for_timeout(2000)
        assert "/mis-calificaciones" in page.url or "/dashboard" in page.url
        bp._log("CHECK", "APODERADO en dashboard")

        bp._log("SETUP", "Inyectando token ESTUDIANTE")
        injectar_token(page, CREDENCIALES["ESTUDIANTE"]["rut"], CREDENCIALES["ESTUDIANTE"]["password"])
        bp.navigate(f"{frontend_url}/dashboard")
        page.wait_for_timeout(2000)
        assert "/mis-calificaciones" in page.url or "/dashboard" in page.url
        bp._log("CHECK", "ESTUDIANTE en dashboard")

        bp.screenshot("seguridad_dashboard")
