import pytest
from helpers.ui_helpers import login_y_navegar


class TestEstudianteAcciones:

    def test_ver_mis_notas(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "ESTUDIANTE", "/mis-calificaciones")

        page.wait_for_timeout(2000)

        assert "/mis-calificaciones" in page.url

    def test_ver_mi_historial_asistencia(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "ESTUDIANTE", "/asistencia/historial")

        page.wait_for_timeout(2000)

        assert "/asistencia/historial" in page.url

    def test_ver_mis_mensajes(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "ESTUDIANTE", "/comunicaciones")

        page.wait_for_timeout(2000)

        assert "/comunicaciones" in page.url
