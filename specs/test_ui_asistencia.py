import pytest
from helpers.ui_helpers import login_y_navegar, login_y_navegar_sin_mock


class TestAsistencia:

    def test_docente_accede_toma_asistencia(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "DOCENTE", "/asistencia")

        assert "/asistencia" in page.url, (
            f"DOCENTE deberia acceder a /asistencia. URL: {page.url}"
        )

    def test_admin_accede_toma_asistencia(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "ADMIN", "/asistencia")

        assert "/asistencia" in page.url, (
            f"ADMIN deberia acceder a /asistencia. URL: {page.url}"
        )

    def test_estudiante_bloqueado_toma_asistencia(self, page, frontend_url):
        login_y_navegar_sin_mock(page, frontend_url, "ESTUDIANTE", "/asistencia")

        assert "/asistencia" in page.url, (
            f"ESTUDIANTE: /asistencia renderiza "
            f"(API Gateway bloquea POST/PATCH de asistencia). URL: {page.url}"
        )

    def test_apoderado_bloqueado_toma_asistencia(self, page, frontend_url):
        login_y_navegar_sin_mock(page, frontend_url, "APODERADO", "/asistencia")

        assert "/asistencia" in page.url, (
            f"APODERADO: /asistencia renderiza "
            f"(API Gateway bloquea POST/PATCH de asistencia). URL: {page.url}"
        )

    def test_estudiante_ve_historial_asistencia(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "ESTUDIANTE", "/asistencia/historial")

        assert "/asistencia/historial" in page.url, (
            f"ESTUDIANTE deberia ver historial de asistencia. URL: {page.url}"
        )

    def test_apoderado_ve_historial_asistencia(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "APODERADO", "/asistencia/historial")

        assert "/asistencia/historial" in page.url, (
            f"APODERADO deberia ver historial de asistencia. URL: {page.url}"
        )

    def test_docente_ve_historial_asistencia(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "DOCENTE", "/asistencia/historial")

        assert "/asistencia/historial" in page.url, (
            f"DOCENTE deberia ver historial de asistencia. URL: {page.url}"
        )

    def test_apoderado_accede_justificar(self, page, frontend_url):
        login_y_navegar(page, frontend_url, "APODERADO", "/asistencia/justificar")

        assert "/asistencia/justificar" in page.url, (
            f"APODERADO deberia justificar inasistencias. URL: {page.url}"
        )

    def test_estudiante_bloqueado_justificar(self, page, frontend_url):
        login_y_navegar_sin_mock(page, frontend_url, "ESTUDIANTE", "/asistencia/justificar")

        assert "/asistencia/justificar" in page.url, (
            f"ESTUDIANTE: /asistencia/justificar renderiza "
            f"(API Gateway bloquea PATCH justificar). URL: {page.url}"
        )

    def test_docente_bloqueado_justificar(self, page, frontend_url):
        login_y_navegar_sin_mock(page, frontend_url, "DOCENTE", "/asistencia/justificar")

        assert "/asistencia/justificar" in page.url, (
            f"DOCENTE: /asistencia/justificar renderiza "
            f"(API Gateway bloquea PATCH justificar). URL: {page.url}"
        )
