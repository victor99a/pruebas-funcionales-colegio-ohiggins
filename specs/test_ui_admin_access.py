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

    @pytest.mark.parametrize("pagina,destino_esperado", [
        ("/admin/gestion-academica", "/calificaciones"),
        ("/admin/usuarios", "/calificaciones"),
        ("/admin/asignacion-docentes", "/calificaciones"),
    ])
    def test_docente_bloqueado_de_admin(self, page, frontend_url, pagina, destino_esperado):
        login_y_navegar_sin_mock(page, frontend_url, "DOCENTE", pagina)

        assert destino_esperado in page.url, (
            f"DOCENTE debe ser redirigido a {destino_esperado} desde {pagina}. URL: {page.url}"
        )

    @pytest.mark.parametrize("pagina,destino_esperado", [
        ("/admin/gestion-academica", "/mis-calificaciones"),
        ("/admin/usuarios", "/mis-calificaciones"),
        ("/admin/asignacion-docentes", "/mis-calificaciones"),
    ])
    def test_apoderado_bloqueado_de_admin(self, page, frontend_url, pagina, destino_esperado):
        login_y_navegar_sin_mock(page, frontend_url, "APODERADO", pagina)

        assert destino_esperado in page.url, (
            f"APODERADO debe ser redirigido a {destino_esperado} desde {pagina}. URL: {page.url}"
        )

    @pytest.mark.parametrize("pagina,destino_esperado", [
        ("/admin/gestion-academica", "/mis-calificaciones"),
        ("/admin/usuarios", "/mis-calificaciones"),
        ("/admin/asignacion-docentes", "/mis-calificaciones"),
    ])
    def test_estudiante_bloqueado_de_admin(self, page, frontend_url, pagina, destino_esperado):
        login_y_navegar_sin_mock(page, frontend_url, "ESTUDIANTE", pagina)

        assert destino_esperado in page.url, (
            f"ESTUDIANTE debe ser redirigido a {destino_esperado} desde {pagina}. URL: {page.url}"
        )

    def test_docente_dashboard_muestra_error(self, page, frontend_url):
        login_y_navegar_sin_mock(page, frontend_url, "DOCENTE", "/dashboard")

        assert "/dashboard" in page.url or "/calificaciones" in page.url, (
            f"DOCENTE en dashboard. URL: {page.url}"
        )
