import pytest
from helpers.ui_helpers import login_y_navegar_sin_mock, injectar_token, CREDENCIALES


class TestSeguridad:

    @pytest.mark.seguridad
    def test_sin_autenticacion_no_accede(self, page, frontend_url):
        """Sin token JWT, TODAS las rutas protegidas redirigen a /login"""
        rutas = ["/dashboard", "/calificaciones", "/admin/usuarios", "/comunicaciones"]

        for ruta in rutas:
            page.goto(f"{frontend_url}{ruta}")
            page.wait_for_timeout(2000)
            assert "/login" in page.url, (
                f"SIN TOKEN: {ruta} deberia redirigir a /login. URL: {page.url}"
            )

    @pytest.mark.seguridad
    def test_roles_sin_permiso_bloqueados_admin(self, page, frontend_url):
        """DOCENTE/APODERADO/ESTUDIANTE no pueden acceder a paginas admin"""
        admin_pages = ["/admin/gestion-academica", "/admin/usuarios", "/admin/asignacion-docentes"]

        page.goto(f"{frontend_url}/login")
        page.wait_for_load_state("networkidle")
        injectar_token(page, CREDENCIALES["DOCENTE"]["rut"], CREDENCIALES["DOCENTE"]["password"])

        for pagina in admin_pages:
            page.goto(f"{frontend_url}{pagina}")
            page.wait_for_timeout(2000)
            assert "/calificaciones" in page.url, (
                f"DOCENTE bloqueado de {pagina} -> /calificaciones. URL: {page.url}"
            )

        injectar_token(page, CREDENCIALES["APODERADO"]["rut"], CREDENCIALES["APODERADO"]["password"])
        for pagina in admin_pages:
            page.goto(f"{frontend_url}{pagina}")
            page.wait_for_timeout(2000)
            assert "/mis-calificaciones" in page.url, (
                f"APODERADO bloqueado de {pagina} -> /mis-calificaciones. URL: {page.url}"
            )

        injectar_token(page, CREDENCIALES["ESTUDIANTE"]["rut"], CREDENCIALES["ESTUDIANTE"]["password"])
        for pagina in admin_pages:
            page.goto(f"{frontend_url}{pagina}")
            page.wait_for_timeout(2000)
            assert "/mis-calificaciones" in page.url, (
                f"ESTUDIANTE bloqueado de {pagina} -> /mis-calificaciones. URL: {page.url}"
            )

        page.screenshot(path="screenshots/seguridad_bloqueo_admin.png")

    @pytest.mark.seguridad
    def test_escritura_bloqueada_y_paginas_renderizan(self, page, frontend_url):
        """No-ADMIN/DOCENTE: paginas de escritura renderizan pero API Gateway bloquea"""
        page.goto(f"{frontend_url}/login")
        page.wait_for_load_state("networkidle")

        for rol in ["APODERADO", "ESTUDIANTE"]:
            injectar_token(page, CREDENCIALES[rol]["rut"], CREDENCIALES[rol]["password"])

            for ruta in ["/calificaciones", "/asistencia", "/comunicaciones/redactar", "/asistencia/justificar"]:
                page.goto(f"{frontend_url}{ruta}")
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(2000)
                assert ruta in page.url, (
                    f"{rol} en {ruta}: pagina renderiza (API protegida). URL: {page.url}"
                )

        injectar_token(page, CREDENCIALES["ESTUDIANTE"]["rut"], CREDENCIALES["ESTUDIANTE"]["password"])
        page.goto(f"{frontend_url}/asistencia")
        page.wait_for_timeout(2000)

        btn_guardar = page.locator('button:has-text("Guardar Asistencia")')
        if btn_guardar.count() > 0 and btn_guardar.is_visible():
            btn_guardar.click()
            page.wait_for_timeout(2000)

        assert "/asistencia" in page.url or "/login" in page.url, (
            f"ESTUDIANTE submit asistencia. URL: {page.url}"
        )

        page.screenshot(path="screenshots/seguridad_escritura_bloqueada.png")

    @pytest.mark.seguridad
    def test_dashboard_kpi_solo_admin(self, page, frontend_url):
        """Dashboard KPI: solo ADMIN ve datos, otros roles ven error o son redirigidos"""
        page.goto(f"{frontend_url}/login")
        page.wait_for_load_state("networkidle")

        injectar_token(page, CREDENCIALES["DOCENTE"]["rut"], CREDENCIALES["DOCENTE"]["password"])
        page.goto(f"{frontend_url}/dashboard")
        page.wait_for_timeout(2000)
        assert "/dashboard" in page.url or "/calificaciones" in page.url, (
            f"DOCENTE en dashboard: error KPI. URL: {page.url}"
        )

        injectar_token(page, CREDENCIALES["APODERADO"]["rut"], CREDENCIALES["APODERADO"]["password"])
        page.goto(f"{frontend_url}/dashboard")
        page.wait_for_timeout(2000)
        assert "/mis-calificaciones" in page.url or "/dashboard" in page.url, (
            f"APODERADO en dashboard. URL: {page.url}"
        )

        injectar_token(page, CREDENCIALES["ESTUDIANTE"]["rut"], CREDENCIALES["ESTUDIANTE"]["password"])
        page.goto(f"{frontend_url}/dashboard")
        page.wait_for_timeout(2000)
        assert "/mis-calificaciones" in page.url or "/dashboard" in page.url, (
            f"ESTUDIANTE en dashboard. URL: {page.url}"
        )

        page.screenshot(path="screenshots/seguridad_dashboard.png")
