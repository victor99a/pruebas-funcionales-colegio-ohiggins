import pytest
from helpers.ui_helpers import login_y_navegar
from pages.login_page import DashboardPage


class TestAdmin:

    def test_crear_curso_y_asignatura(self, page, frontend_url):
        """Gestion academica: crear curso + crear asignatura -> verificar formularios"""
        login_y_navegar(page, frontend_url, "ADMIN", "/admin/gestion-academica")

        page.locator('input[name="nombre"]').first.fill("3ro Medio Test")
        page.locator('#anio-lectivo').fill("2026")
        page.locator('button:has-text("Crear Curso")').click()
        page.wait_for_timeout(1500)

        page.locator('#nombre-asignatura').fill("Fisica Test")
        page.locator('#horas-semanales').fill("4")
        page.locator('button:has-text("Agregar Asignatura")').click()
        page.wait_for_timeout(1500)

        assert "/admin/gestion-academica" in page.url

    def test_crear_usuarios_docente_y_estudiante(self, page, frontend_url):
        """Usuarios: crear docente + cambiar tab + crear estudiante -> verificar tabs"""
        login_y_navegar(page, frontend_url, "ADMIN", "/admin/usuarios")

        tab_docentes = page.locator('button:has-text("Docentes")')
        assert tab_docentes.count() > 0, "Tab Docentes no encontrado"
        tab_docentes.click()
        page.wait_for_timeout(800)

        page.locator('#rut').fill("24000001-k")
        page.locator('#nombres').fill("Profesor")
        page.locator('#apellidos').fill("Flujo Test")
        page.locator('#email').fill("profesor.flujo@test.cl")
        page.locator('#password').fill("Flujo123!")
        page.locator('#confirmPassword').fill("Flujo123!")
        page.locator('#rol').select_option("DOCENTE")
        page.wait_for_timeout(300)

        btn_crear = page.locator('button:has-text("Crear usuario")')
        assert btn_crear.count() > 0, "Boton crear usuario no encontrado"
        btn_crear.click()
        page.wait_for_timeout(2000)

        tab_estudiantes = page.locator('button:has-text("Estudiantes")')
        assert tab_estudiantes.count() > 0, "Tab Estudiantes no encontrado"
        tab_estudiantes.click()
        page.wait_for_timeout(800)

        page.locator('#rut').fill("24000003-5")
        page.locator('#nombres').fill("Alumno")
        page.locator('#apellidos').fill("Flujo Test")
        page.locator('#email').fill("alumno.flujo@test.cl")
        page.locator('#password').fill("Flujo123!")
        page.locator('#confirmPassword').fill("Flujo123!")
        page.locator('#rol').select_option("ESTUDIANTE")
        page.wait_for_timeout(300)
        btn_crear.click()
        page.wait_for_timeout(2000)

        assert "/admin/usuarios" in page.url

    def test_asignar_docente(self, page, frontend_url):
        """Asignacion docente: verificar pagina + selects"""
        login_y_navegar(page, frontend_url, "ADMIN", "/admin/asignacion-docentes")

        assert "/admin/asignacion-docentes" in page.url

        selects = page.locator('select')
        count = selects.count()
        assert count >= 2, f"Se esperaban al menos 2 selects, hay {count}"

        for i in range(min(count, 3)):
            if selects.nth(i).locator('option').count() > 1:
                selects.nth(i).select_option(index=1)
                page.wait_for_timeout(300)

        btn = page.locator('button:has-text("Asignar"), button:has-text("Guardar")')
        if btn.count() > 0:
            btn.first.click()
            page.wait_for_timeout(1500)

    def test_admin_dashboard_carga_kpis(self, page, frontend_url):
        """Dashboard ADMIN: cargar -> verificar KPIs sin error"""
        login_y_navegar(page, frontend_url, "ADMIN", "/dashboard")

        page.wait_for_timeout(2000)
        error = page.locator('.dashboard__error, p:has-text("No se pudieron cargar")')
        assert error.count() == 0, f"Dashboard ADMIN muestra error inesperado: {error.text_content() if error.count() > 0 else ''}"

    def test_admin_navegacion_completa(self, page, frontend_url):
        """Navegar secuencialmente todas las paginas admin -> todas cargan"""
        paginas = [
            "/dashboard",
            "/admin/gestion-academica",
            "/admin/usuarios",
            "/admin/asignacion-docentes",
            "/comunicaciones",
        ]
        for i, pagina in enumerate(paginas):
            login_y_navegar(page, frontend_url, "ADMIN", pagina) if i == 0 else None
            if i > 0:
                page.goto(f"{frontend_url}{pagina}")
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(1000)
            assert pagina in page.url, f"ADMIN no pudo navegar a {pagina}: {page.url}"

    def test_admin_sidebar_todos_links(self, page, frontend_url):
        """Sidebar ADMIN: todos los links visibles, ninguno oculto"""
        login_y_navegar(page, frontend_url, "ADMIN", "/dashboard")
        dp = DashboardPage(page)

        links = dp.get_sidebar_link_texts()
        assert len(links) >= 8, f"ADMIN deberia tener >=8 links, tiene {len(links)}: {links}"

        for link in ["Dashboard", "Usuarios", "Comunicaciones", "Historial"]:
            assert dp.sidebar_has_link(link), f"ADMIN sidebar missing: {link}"
