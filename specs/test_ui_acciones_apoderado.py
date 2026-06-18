import pytest
from helpers.ui_helpers import login_y_navegar


class TestApoderadoAcciones:

    def test_ver_calificaciones_pupilo(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "APODERADO", "/mis-calificaciones")

        page.wait_for_timeout(2000)

        selector_pupilo = page.locator('#select-pupilo, select')
        if selector_pupilo.count() > 0 and selector_pupilo.locator('option').count() > 1:
            selector_pupilo.first.select_option(index=1)
            page.wait_for_timeout(1500)

        assert "/mis-calificaciones" in page.url

    def test_justificar_inasistencia(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "APODERADO", "/asistencia/justificar")

        page.wait_for_timeout(2000)

        assert "/asistencia/justificar" in page.url

    def test_ver_historial_asistencia_pupilo(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "APODERADO", "/asistencia/historial")

        page.wait_for_timeout(2000)

        assert "/asistencia/historial" in page.url
