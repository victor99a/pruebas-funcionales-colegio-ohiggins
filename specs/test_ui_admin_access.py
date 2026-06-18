import pytest
from helpers.ui_helpers import login_y_navegar, login_y_navegar_sin_mock


PAGINAS_ADMIN = [
    "/admin/gestion-academica",
    "/admin/usuarios",
    "/admin/asignacion-docentes",
]


class TestAdminAccess:

    @pytest.mark.parametrize("pagina", PAGINAS_ADMIN)
    def test_admin_accede_paginas_admin(self, page, frontend_url, pagina):
        login_y_navegar(page, frontend_url, "ADMIN", pagina)

        assert pagina in page.url, (
            f"ADMIN deberia acceder a {pagina}. URL: {page.url}"
        )

    @pytest.mark.parametrize("pagina,espera_redirect", [
        ("/admin/gestion-academica", False),
        ("/admin/usuarios", False),
        ("/admin/asignacion-docentes", True),
    ])
    def test_docente_bloqueado_de_admin(self, page, frontend_url, pagina, espera_redirect):
        login_y_navegar_sin_mock(page, frontend_url, "DOCENTE", pagina)

        if espera_redirect:
            assert "/login" in page.url, (
                f"DOCENTE deberia ser redirigido a /login desde {pagina}. URL: {page.url}"
            )
        else:
            assert pagina in page.url, (
                f"DOCENTE: {pagina} renderiza (API Gateway protege endpoints). URL: {page.url}"
            )

    @pytest.mark.parametrize("pagina,espera_redirect", [
        ("/admin/gestion-academica", True),
        ("/admin/usuarios", False),
        ("/admin/asignacion-docentes", True),
    ])
    def test_apoderado_bloqueado_de_admin(self, page, frontend_url, pagina, espera_redirect):
        login_y_navegar_sin_mock(page, frontend_url, "APODERADO", pagina)

        if espera_redirect:
            assert "/login" in page.url, (
                f"APODERADO deberia ser redirigido a /login desde {pagina}. URL: {page.url}"
            )
        else:
            assert pagina in page.url, (
                f"APODERADO: {pagina} renderiza (API Gateway protege endpoints). URL: {page.url}"
            )

    @pytest.mark.parametrize("pagina,espera_redirect", [
        ("/admin/gestion-academica", True),
        ("/admin/usuarios", False),
        ("/admin/asignacion-docentes", True),
    ])
    def test_estudiante_bloqueado_de_admin(self, page, frontend_url, pagina, espera_redirect):
        login_y_navegar_sin_mock(page, frontend_url, "ESTUDIANTE", pagina)

        if espera_redirect:
            assert "/login" in page.url, (
                f"ESTUDIANTE deberia ser redirigido a /login desde {pagina}. URL: {page.url}"
            )
        else:
            assert pagina in page.url, (
                f"ESTUDIANTE: {pagina} renderiza (API Gateway protege endpoints). URL: {page.url}"
            )

    def test_docente_bloqueado_dashboard_stats(self, page, frontend_url):
        login_y_navegar_sin_mock(page, frontend_url, "DOCENTE", "/dashboard")

        assert "/login" in page.url, (
            f"DOCENTE deberia ser redirigido desde /dashboard. URL: {page.url}"
        )
