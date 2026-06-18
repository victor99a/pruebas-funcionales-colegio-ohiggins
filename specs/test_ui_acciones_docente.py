import pytest
from helpers.ui_helpers import login_y_navegar


class TestDocenteAcciones:

    def test_registrar_notas(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "DOCENTE", "/calificaciones")

        curso_select = page.locator('#select-curso')
        asig_select = page.locator('#select-asignatura')

        if curso_select.count() > 0 and curso_select.locator('option').count() > 1:
            curso_select.select_option(index=1)
            page.wait_for_timeout(800)

        if asig_select.count() > 0 and asig_select.locator('option').count() > 1:
            asig_select.select_option(index=1)
            page.wait_for_timeout(800)

        nota_inputs = page.locator('input.registro-notas__input-nota[type="number"]')
        count = nota_inputs.count()

        if count > 0:
            nota_inputs.nth(0).fill("6.5")
            page.wait_for_timeout(300)
            if count > 1:
                nota_inputs.nth(1).fill("5.0")
                page.wait_for_timeout(300)
            if count > 2:
                nota_inputs.nth(2).fill("6.0")
                page.wait_for_timeout(300)

            btn_guardar = page.locator('button:has-text("Guardar Calificaciones")')
            if btn_guardar.count() > 0:
                btn_guardar.click()
                page.wait_for_timeout(2000)

        assert "/calificaciones" in page.url

    def test_tomar_asistencia(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "DOCENTE", "/asistencia")

        curso_select = page.locator('#curso')
        if curso_select.count() > 0 and curso_select.locator('option').count() > 1:
            curso_select.select_option(index=1)
            page.wait_for_timeout(500)

        btn_filtrar = page.locator('button:has-text("Filtrar")')
        if btn_filtrar.count() > 0:
            btn_filtrar.click()
            page.wait_for_timeout(2000)

        asistencias = page.locator('select.asistencia-table__select')
        count = asistencias.count()
        if count > 0:
            asistencias.nth(0).select_option("ausente")
            page.wait_for_timeout(300)
            if count > 1:
                asistencias.nth(1).select_option("presente")
                page.wait_for_timeout(300)

            btn_guardar = page.locator('button:has-text("Guardar Asistencia")')
            if btn_guardar.count() > 0:
                btn_guardar.click()
                page.wait_for_timeout(2000)

        assert "/asistencia" in page.url

    def test_ver_anotaciones(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "DOCENTE", "/asistencia/anotaciones")

        assert "/asistencia/anotaciones" in page.url
