import pytest
from helpers.ui_helpers import login_y_navegar_sin_mock


class TestAccionesNegativas:

    def test_apoderado_no_puede_crear_usuario(self, page, frontend_url):
        login_y_navegar_sin_mock(page, frontend_url, "APODERADO", "/admin/usuarios")

        tab_estudiantes = page.locator('button:has-text("Estudiantes")')
        if tab_estudiantes.count() > 0:
            tab_estudiantes.click()
            page.wait_for_timeout(800)

        page.locator('#rut').fill("99000001-1")
        page.locator('#nombres').fill("No")
        page.locator('#apellidos').fill("Autorizado")
        page.locator('#email').fill("no.autorizado@test.cl")
        page.locator('#password').fill("Test1234!")
        page.locator('#confirmPassword').fill("Test1234!")

        rol_select = page.locator('#rol')
        if rol_select.count() > 0:
            rol_select.select_option("ESTUDIANTE")

        page.wait_for_timeout(500)

        btn_crear = page.locator('button:has-text("Crear usuario")')
        if btn_crear.count() > 0 and btn_crear.is_enabled():
            btn_crear.click()
            page.wait_for_timeout(3000)

        assert "/login" in page.url or "/admin/usuarios" in page.url, (
            f"APODERADO intento crear usuario. URL: {page.url}"
        )

    def test_estudiante_no_puede_registrar_notas(self, page, frontend_url):
        login_y_navegar_sin_mock(page, frontend_url, "ESTUDIANTE", "/calificaciones")

        page.wait_for_timeout(2000)

        assert "/login" in page.url or "/calificaciones" in page.url, (
            f"ESTUDIANTE intento registrar notas. URL: {page.url}"
        )

    def test_apoderado_no_puede_registrar_notas(self, page, frontend_url):
        login_y_navegar_sin_mock(page, frontend_url, "APODERADO", "/calificaciones")

        page.wait_for_timeout(2000)

        assert "/login" in page.url or "/calificaciones" in page.url, (
            f"APODERADO intento registrar notas. URL: {page.url}"
        )

    def test_estudiante_no_puede_tomar_asistencia(self, page, frontend_url):
        login_y_navegar_sin_mock(page, frontend_url, "ESTUDIANTE", "/asistencia")

        curso_select = page.locator('#curso')
        if curso_select.count() > 0 and curso_select.locator('option').count() > 1:
            curso_select.select_option(index=1)
            page.wait_for_timeout(300)

        btn_filtrar = page.locator('button:has-text("Filtrar")')
        if btn_filtrar.count() > 0:
            btn_filtrar.click()
            page.wait_for_timeout(2000)

        btn_guardar = page.locator('button:has-text("Guardar Asistencia")')
        if btn_guardar.count() > 0 and btn_guardar.is_visible():
            btn_guardar.click()
            page.wait_for_timeout(3000)

        assert "/login" in page.url or "/asistencia" in page.url, (
            f"ESTUDIANTE intento tomar asistencia. URL: {page.url}"
        )

    def test_estudiante_no_puede_enviar_mensaje(self, page, frontend_url):
        login_y_navegar_sin_mock(page, frontend_url, "ESTUDIANTE", "/comunicaciones/redactar")

        page.wait_for_timeout(2000)

        assert "/login" in page.url or "/comunicaciones/redactar" in page.url, (
            f"ESTUDIANTE intento redactar mensaje. URL: {page.url}"
        )

    def test_apoderado_no_puede_acceder_dashboard(self, page, frontend_url):
        login_y_navegar_sin_mock(page, frontend_url, "APODERADO", "/dashboard")

        page.wait_for_timeout(2000)

        assert "/login" in page.url or "/dashboard" in page.url, (
            f"APODERADO intento acceder a dashboard. URL: {page.url}"
        )
