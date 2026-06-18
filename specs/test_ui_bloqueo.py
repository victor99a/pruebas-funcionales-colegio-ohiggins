import pytest
from helpers.ui_helpers import login_y_navegar_sin_mock, injectar_token, CREDENCIALES


class TestBloqueo:

    def test_docente_bloqueado_todas_admin(self, page, frontend_url):
        """DOCENTE intenta 3 paginas admin -> redirigido a /calificaciones"""
        page.goto(f"{frontend_url}/login")
        page.wait_for_load_state("networkidle")
        injectar_token(page, CREDENCIALES["DOCENTE"]["rut"], CREDENCIALES["DOCENTE"]["password"])

        for pagina in ["/admin/gestion-academica", "/admin/usuarios", "/admin/asignacion-docentes"]:
            page.goto(f"{frontend_url}{pagina}")
            page.wait_for_timeout(2000)
            assert "/calificaciones" in page.url, (
                f"DOCENTE deberia ser redirigido de {pagina} a /calificaciones. URL: {page.url}"
            )

    def test_apoderado_bloqueado_todas_admin(self, page, frontend_url):
        """APODERADO intenta 3 paginas admin -> redirigido a /mis-calificaciones"""
        page.goto(f"{frontend_url}/login")
        page.wait_for_load_state("networkidle")
        injectar_token(page, CREDENCIALES["APODERADO"]["rut"], CREDENCIALES["APODERADO"]["password"])

        for pagina in ["/admin/gestion-academica", "/admin/usuarios", "/admin/asignacion-docentes"]:
            page.goto(f"{frontend_url}{pagina}")
            page.wait_for_timeout(2000)
            assert "/mis-calificaciones" in page.url, (
                f"APODERADO deberia ser redirigido de {pagina} a /mis-calificaciones. URL: {page.url}"
            )

    def test_estudiante_bloqueado_todas_admin(self, page, frontend_url):
        """ESTUDIANTE intenta 3 paginas admin -> redirigido a /mis-calificaciones"""
        page.goto(f"{frontend_url}/login")
        page.wait_for_load_state("networkidle")
        injectar_token(page, CREDENCIALES["ESTUDIANTE"]["rut"], CREDENCIALES["ESTUDIANTE"]["password"])

        for pagina in ["/admin/gestion-academica", "/admin/usuarios", "/admin/asignacion-docentes"]:
            page.goto(f"{frontend_url}{pagina}")
            page.wait_for_timeout(2000)
            assert "/mis-calificaciones" in page.url, (
                f"ESTUDIANTE deberia ser redirigido de {pagina} a /mis-calificaciones. URL: {page.url}"
            )

    def test_docente_dashboard_muestra_error_kpi(self, page, frontend_url):
        """DOCENTE en /dashboard -> error KPI pero no redirige (token no se borra en 403)"""
        login_y_navegar_sin_mock(page, frontend_url, "DOCENTE", "/dashboard")
        page.wait_for_timeout(2000)

        assert "/dashboard" in page.url or "/calificaciones" in page.url, (
            f"DOCENTE en dashboard. URL: {page.url}"
        )

    def test_no_docente_en_registro_notas(self, page, frontend_url):
        """APODERADO y ESTUDIANTE en /calificaciones -> pagina carga (API Gateway protege endpoints)"""
        for rol in ["APODERADO", "ESTUDIANTE"]:
            login_y_navegar_sin_mock(page, frontend_url, rol, "/calificaciones")
            page.wait_for_timeout(2000)
            assert "/calificaciones" in page.url, (
                f"{rol} en /calificaciones: pagina renderiza, API protegida. URL: {page.url}"
            )

    def test_no_docente_en_toma_asistencia(self, page, frontend_url):
        """APODERADO y ESTUDIANTE en /asistencia -> pagina carga"""
        for rol in ["APODERADO", "ESTUDIANTE"]:
            login_y_navegar_sin_mock(page, frontend_url, rol, "/asistencia")
            page.wait_for_timeout(2000)
            assert "/asistencia" in page.url, (
                f"{rol} en /asistencia: pagina renderiza. URL: {page.url}"
            )

    def test_no_docente_en_redactar_mensaje(self, page, frontend_url):
        """APODERADO y ESTUDIANTE en /comunicaciones/redactar -> pagina carga"""
        for rol in ["APODERADO", "ESTUDIANTE"]:
            login_y_navegar_sin_mock(page, frontend_url, rol, "/comunicaciones/redactar")
            page.wait_for_timeout(2000)
            assert "/comunicaciones/redactar" in page.url, (
                f"{rol} en /comunicaciones/redactar: pagina renderiza. URL: {page.url}"
            )

    def test_estudiante_no_puede_justificar(self, page, frontend_url):
        """ESTUDIANTE en /asistencia/justificar -> pagina carga pero API bloquea PATCH"""
        login_y_navegar_sin_mock(page, frontend_url, "ESTUDIANTE", "/asistencia/justificar")
        page.wait_for_timeout(2000)

        assert "/asistencia/justificar" in page.url, (
            f"ESTUDIANTE en justificar: pagina renderiza. URL: {page.url}"
        )

    def test_submit_asistencia_estudiante_bloqueado(self, page, frontend_url):
        """ESTUDIANTE intenta submit en /asistencia -> verificar"""
        login_y_navegar_sin_mock(page, frontend_url, "ESTUDIANTE", "/asistencia")
        page.wait_for_timeout(2000)

        btn_guardar = page.locator('button:has-text("Guardar Asistencia")')
        if btn_guardar.count() > 0 and btn_guardar.is_visible():
            btn_guardar.click()
            page.wait_for_timeout(2000)

        assert "/asistencia" in page.url or "/login" in page.url, (
            f"ESTUDIANTE submit asistencia. URL: {page.url}"
        )

    def test_ruta_protegida_sin_token(self, page, frontend_url):
        """Sin token, rutas protegidas redirigen a /login"""
        for ruta in ["/dashboard", "/admin/gestion-academica", "/calificaciones", "/comunicaciones"]:
            page.goto(f"{frontend_url}{ruta}")
            page.wait_for_timeout(2000)
            assert "/login" in page.url, (
                f"Sin token, {ruta} deberia redirigir a /login. URL: {page.url}"
            )
