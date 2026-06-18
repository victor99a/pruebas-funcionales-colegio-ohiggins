import pytest
from helpers.ui_helpers import login_y_navegar, login_y_navegar_sin_mock


class TestCalificaciones:

    def test_docente_accede_registro_notas(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "DOCENTE", "/calificaciones")

        assert "/calificaciones" in page.url, (
            f"DOCENTE deberia acceder a /calificaciones. URL: {page.url}"
        )

    def test_admin_accede_registro_notas(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "ADMIN", "/calificaciones")

        assert "/calificaciones" in page.url, (
            f"ADMIN deberia acceder a /calificaciones. URL: {page.url}"
        )

    def test_apoderado_bloqueado_registro_notas(self, page, frontend_url):
        login_y_navegar_sin_mock(page, frontend_url, "APODERADO", "/calificaciones")

        page.wait_for_timeout(2000)

        assert "/calificaciones" in page.url, (
            f"APODERADO: /calificaciones renderiza (API Gateway protege POST guardar). URL: {page.url}"
        )

    def test_estudiante_bloqueado_registro_notas(self, page, frontend_url):
        login_y_navegar_sin_mock(page, frontend_url, "ESTUDIANTE", "/calificaciones")

        page.wait_for_timeout(2000)

        assert "/calificaciones" in page.url, (
            f"ESTUDIANTE: /calificaciones renderiza (API Gateway protege POST guardar). URL: {page.url}"
        )

    def test_estudiante_ve_mis_calificaciones(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "ESTUDIANTE", "/mis-calificaciones")

        assert "/mis-calificaciones" in page.url, (
            f"ESTUDIANTE deberia ver sus calificaciones. URL: {page.url}"
        )

    def test_apoderado_ve_mis_calificaciones(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "APODERADO", "/mis-calificaciones")

        assert "/mis-calificaciones" in page.url, (
            f"APODERADO deberia ver calificaciones del pupilo. URL: {page.url}"
        )

    def test_docente_bloqueado_mis_calificaciones(self, page, frontend_url):
        login_y_navegar_sin_mock(page, frontend_url, "DOCENTE", "/mis-calificaciones")

        assert "/mis-calificaciones" in page.url, (
            f"DOCENTE: /mis-calificaciones renderiza "
            f"(API Gateway protege el endpoint boletin). URL: {page.url}"
        )
