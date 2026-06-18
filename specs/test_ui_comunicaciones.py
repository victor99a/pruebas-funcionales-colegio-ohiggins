import pytest
from helpers.ui_helpers import login_y_navegar, login_y_navegar_sin_mock


class TestComunicaciones:

    def test_admin_accede_comunicaciones(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "ADMIN", "/comunicaciones")

        assert "/comunicaciones" in page.url, (
            f"ADMIN deberia acceder a /comunicaciones. URL: {page.url}"
        )

    def test_docente_accede_comunicaciones(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "DOCENTE", "/comunicaciones")

        assert "/comunicaciones" in page.url, (
            f"DOCENTE deberia acceder a /comunicaciones. URL: {page.url}"
        )

    def test_apoderado_accede_comunicaciones(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "APODERADO", "/comunicaciones")

        assert "/comunicaciones" in page.url, (
            f"APODERADO deberia acceder a /comunicaciones. URL: {page.url}"
        )

    def test_estudiante_accede_comunicaciones(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "ESTUDIANTE", "/comunicaciones")

        assert "/comunicaciones" in page.url, (
            f"ESTUDIANTE deberia acceder a /comunicaciones. URL: {page.url}"
        )

    def test_docente_accede_redactar(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "DOCENTE", "/comunicaciones/redactar")

        assert "/comunicaciones/redactar" in page.url, (
            f"DOCENTE deberia acceder a redactar mensaje. URL: {page.url}"
        )

    def test_apoderado_bloqueado_redactar(self, page, frontend_url):
        login_y_navegar_sin_mock(page, frontend_url, "APODERADO", "/comunicaciones/redactar")

        assert "/comunicaciones/redactar" in page.url, (
            f"APODERADO: /comunicaciones/redactar renderiza "
            f"(API Gateway bloquea POST enviar). URL: {page.url}"
        )

    def test_estudiante_bloqueado_redactar(self, page, frontend_url):
        login_y_navegar_sin_mock(page, frontend_url, "ESTUDIANTE", "/comunicaciones/redactar")

        assert "/comunicaciones/redactar" in page.url, (
            f"ESTUDIANTE: /comunicaciones/redactar renderiza "
            f"(API Gateway bloquea POST enviar). URL: {page.url}"
        )
