import pytest
from helpers.ui_helpers import login_y_navegar, SIDEBAR_VISIBLE, SIDEBAR_OCULTO
from pages.login_page import DashboardPage


class TestApoderado:

    def test_calificaciones_pupilo(self, page, frontend_url):
        """Apoderado: /mis-calificaciones carga con contenido"""
        login_y_navegar(page, frontend_url, "APODERADO", "/mis-calificaciones")
        page.wait_for_timeout(2000)

        assert "/mis-calificaciones" in page.url

        selector = page.locator('select, #select-pupilo')
        if selector.count() > 0:
            assert selector.first.is_visible(), "Selector de pupilo deberia ser visible"

    def test_historial_y_justificar(self, page, frontend_url):
        """Apoderado: historial asistencia + justificar inasistencias"""
        for ruta in ["/asistencia/historial", "/asistencia/justificar"]:
            login_y_navegar(page, frontend_url, "APODERADO", ruta)
            assert ruta in page.url, f"APODERADO no pudo acceder a {ruta}: {page.url}"

    def test_comunicaciones_bandeja(self, page, frontend_url):
        """Apoderado: bandeja de mensajes carga"""
        login_y_navegar(page, frontend_url, "APODERADO", "/comunicaciones")
        assert "/comunicaciones" in page.url

    def test_apoderado_sidebar(self, page, frontend_url):
        """Sidebar APODERADO: links visibles + ocultos correctos"""
        login_y_navegar(page, frontend_url, "APODERADO", "/mis-calificaciones")
        dp = DashboardPage(page)

        for link in SIDEBAR_VISIBLE["APODERADO"]:
            assert dp.sidebar_has_link(link), f"APODERADO sidebar missing: {link}"
        for link in SIDEBAR_OCULTO["APODERADO"]:
            assert dp.sidebar_lacks_link(link), f"APODERADO sidebar should not show: {link}"

    def test_apoderado_flujo_completo(self, page, frontend_url):
        """Flujo apoderado: mis-calificaciones -> historial -> justificar -> comunicaciones"""
        paginas = ["/mis-calificaciones", "/asistencia/historial", "/asistencia/justificar", "/comunicaciones"]
        for i, ruta in enumerate(paginas):
            if i == 0:
                login_y_navegar(page, frontend_url, "APODERADO", ruta)
            else:
                page.goto(f"{frontend_url}{ruta}")
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(1000)
            assert ruta in page.url, f"APODERADO no pudo acceder a {ruta}"


class TestEstudiante:

    def test_mis_notas(self, page, frontend_url):
        """Estudiante: /mis-calificaciones carga con contenido"""
        login_y_navegar(page, frontend_url, "ESTUDIANTE", "/mis-calificaciones")
        page.wait_for_timeout(2000)

        assert "/mis-calificaciones" in page.url

    def test_historial_asistencia(self, page, frontend_url):
        """Estudiante: historial de asistencia carga"""
        login_y_navegar(page, frontend_url, "ESTUDIANTE", "/asistencia/historial")
        assert "/asistencia/historial" in page.url

    def test_mensajes(self, page, frontend_url):
        """Estudiante: bandeja de mensajes carga"""
        login_y_navegar(page, frontend_url, "ESTUDIANTE", "/comunicaciones")
        assert "/comunicaciones" in page.url

    def test_estudiante_sidebar(self, page, frontend_url):
        """Sidebar ESTUDIANTE: links visibles + ocultos correctos"""
        login_y_navegar(page, frontend_url, "ESTUDIANTE", "/mis-calificaciones")
        dp = DashboardPage(page)

        for link in SIDEBAR_VISIBLE["ESTUDIANTE"]:
            assert dp.sidebar_has_link(link), f"ESTUDIANTE sidebar missing: {link}"
        for link in SIDEBAR_OCULTO["ESTUDIANTE"]:
            assert dp.sidebar_lacks_link(link), f"ESTUDIANTE sidebar should not show: {link}"

    def test_estudiante_flujo_completo(self, page, frontend_url):
        """Flujo estudiante: mis-calificaciones -> historial -> comunicaciones"""
        paginas = ["/mis-calificaciones", "/asistencia/historial", "/comunicaciones"]
        for i, ruta in enumerate(paginas):
            if i == 0:
                login_y_navegar(page, frontend_url, "ESTUDIANTE", ruta)
            else:
                page.goto(f"{frontend_url}{ruta}")
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(1000)
            assert ruta in page.url, f"ESTUDIANTE no pudo acceder a {ruta}"
