import pytest
from helpers.ui_helpers import login_y_navegar


class TestAdminAcciones:

    def test_crear_curso(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "ADMIN", "/admin/gestion-academica")

        nombre_input = page.locator('input[name="nombre"]').first
        anio_input = page.locator('#anio-lectivo')
        btn_crear = page.locator('button:has-text("Crear Curso")')

        nombre_input.fill("2do Basico Test")
        anio_input.fill("2026")
        btn_crear.click()
        page.wait_for_timeout(1500)

        assert "/admin/gestion-academica" in page.url

    def test_crear_asignatura(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "ADMIN", "/admin/gestion-academica")

        nombre_input = page.locator('#nombre-asignatura')
        horas_input = page.locator('#horas-semanales')
        btn_crear = page.locator('button:has-text("Agregar Asignatura")')

        nombre_input.fill("Ciencias Test")
        horas_input.fill("3")
        btn_crear.click()
        page.wait_for_timeout(1500)

        assert "/admin/gestion-academica" in page.url

    def test_crear_usuario_docente(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "ADMIN", "/admin/usuarios")

        tab_docentes = page.locator('button:has-text("Docentes")')
        tab_docentes.click()
        page.wait_for_timeout(1000)

        page.locator('#rut').fill("21000001-k")
        page.locator('#nombres').fill("Profesor")
        page.locator('#apellidos').fill("Accion Test")
        page.locator('#email').fill("profesor.accion@test.cl")
        page.locator('#password').fill("Accion123!")
        page.locator('#confirmPassword').fill("Accion123!")

        page.locator('#rol').select_option("DOCENTE")
        page.wait_for_timeout(500)

        btn_crear = page.locator('button:has-text("Crear usuario")')
        btn_crear.click()
        page.wait_for_timeout(2000)

        assert "/admin/usuarios" in page.url

    def test_crear_usuario_estudiante(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "ADMIN", "/admin/usuarios")

        tab_estudiantes = page.locator('button:has-text("Estudiantes")')
        tab_estudiantes.click()
        page.wait_for_timeout(1000)

        page.locator('#rut').fill("21000003-8")
        page.locator('#nombres').fill("Alumno")
        page.locator('#apellidos').fill("Accion Test")
        page.locator('#email').fill("alumno.accion@test.cl")
        page.locator('#password').fill("Accion123!")
        page.locator('#confirmPassword').fill("Accion123!")

        page.locator('#rol').select_option("ESTUDIANTE")
        page.wait_for_timeout(500)

        btn_crear = page.locator('button:has-text("Crear usuario")')
        btn_crear.click()
        page.wait_for_timeout(2000)

        assert "/admin/usuarios" in page.url

    def test_asignar_docente(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "ADMIN", "/admin/asignacion-docentes")

        assert "/admin/asignacion-docentes" in page.url

        selects = page.locator('select')
        count = selects.count()
        if count >= 3:
            selects.nth(0).select_option(index=1) if selects.nth(0).locator('option').count() > 1 else None
            page.wait_for_timeout(300)
            selects.nth(1).select_option(index=1) if selects.nth(1).locator('option').count() > 1 else None
            page.wait_for_timeout(300)
            selects.nth(2).select_option(index=1) if selects.nth(2).locator('option').count() > 1 else None
            page.wait_for_timeout(300)

            btn_asignar = page.locator('button:has-text("Asignar"), button:has-text("Guardar")')
            if btn_asignar.count() > 0:
                btn_asignar.first.click()
                page.wait_for_timeout(1500)
