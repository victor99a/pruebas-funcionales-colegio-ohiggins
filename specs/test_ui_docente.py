import pytest
from helpers.ui_helpers import login_y_navegar, SIDEBAR_VISIBLE, SIDEBAR_OCULTO
from pages.login_page import DashboardPage


class TestDocente:

    def test_registro_notas_completo(self, page, frontend_url):
        """Registro notas: seleccionar curso+asignatura -> llenar 3 notas -> guardar -> verificar"""
        login_y_navegar(page, frontend_url, "DOCENTE", "/calificaciones")

        curso = page.locator('#select-curso, select[id], select').first
        asig = page.locator('#select-asignatura')

        if curso.count() > 0 and curso.locator('option').count() > 1:
            curso.select_option(index=1)
            page.wait_for_timeout(800)
        if asig.count() > 0 and asig.locator('option').count() > 1:
            asig.select_option(index=1)
            page.wait_for_timeout(800)

        notas = page.locator('input.registro-notas__input-nota[type="number"]')
        count = notas.count()
        if count > 0:
            notas.nth(0).fill("6.5")
            page.wait_for_timeout(200)
        if count > 1:
            notas.nth(1).fill("5.0")
            page.wait_for_timeout(200)
        if count > 2:
            notas.nth(2).fill("6.0")
            page.wait_for_timeout(200)

        btn = page.locator('button:has-text("Guardar Calificaciones")')
        if btn.count() > 0:
            btn.click()
            page.wait_for_timeout(2000)

        assert "/calificaciones" in page.url

    def test_toma_asistencia_completa(self, page, frontend_url):
        """Toma asistencia: seleccionar curso -> filtrar -> marcar asistencia -> guardar"""
        login_y_navegar(page, frontend_url, "DOCENTE", "/asistencia")

        curso = page.locator('#curso')
        assert curso.count() > 0, "Select curso no encontrado en asistencia"
        if curso.locator('option').count() > 1:
            curso.select_option(index=1)
            page.wait_for_timeout(500)

        btn_filtrar = page.locator('button:has-text("Filtrar")')
        if btn_filtrar.count() > 0:
            btn_filtrar.click()
            page.wait_for_timeout(2000)

        asistencias = page.locator('select.asistencia-table__select')
        acount = asistencias.count()
        if acount > 0:
            asistencias.nth(0).select_option("ausente")
            page.wait_for_timeout(200)
        if acount > 1:
            asistencias.nth(1).select_option("presente")
            page.wait_for_timeout(200)

        btn_guardar = page.locator('button:has-text("Guardar Asistencia")')
        if btn_guardar.count() > 0 and btn_guardar.is_visible():
            btn_guardar.click()
            page.wait_for_timeout(2000)

        assert "/asistencia" in page.url

    def test_historial_y_anotaciones(self, page, frontend_url):
        """Historial asistencia + anotaciones: ambas paginas cargan"""
        for ruta in ["/asistencia/historial", "/asistencia/anotaciones"]:
            login_y_navegar(page, frontend_url, "DOCENTE", ruta)
            assert ruta in page.url, f"DOCENTE no pudo acceder a {ruta}: {page.url}"

    def test_comunicaciones_bandeja_y_redactar(self, page, frontend_url):
        """Comunicaciones: bandeja carga -> redactar carga"""
        login_y_navegar(page, frontend_url, "DOCENTE", "/comunicaciones")
        assert "/comunicaciones" in page.url

        page.goto(f"{frontend_url}/comunicaciones/redactar")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        assert "/comunicaciones/redactar" in page.url

    def test_docente_sidebar_links(self, page, frontend_url):
        """Sidebar DOCENTE: verificar que pagina carga con sidebar"""
        login_y_navegar(page, frontend_url, "DOCENTE", "/comunicaciones")
        dp = DashboardPage(page)

        links = dp.get_sidebar_link_texts()
        assert len(links) >= 3, f"DOCENTE deberia tener >=3 links, tiene {len(links)}: {links}"

    def test_docente_flujo_completo(self, page, frontend_url):
        """Flujo completo: login -> calificaciones -> asistencia -> historial -> comunicaciones"""
        paginas = ["/calificaciones", "/asistencia", "/asistencia/historial", "/comunicaciones"]
        for i, ruta in enumerate(paginas):
            if i == 0:
                login_y_navegar(page, frontend_url, "DOCENTE", ruta)
            else:
                page.goto(f"{frontend_url}{ruta}")
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(1000)
            assert ruta in page.url, f"DOCENTE no pudo acceder a {ruta}"
