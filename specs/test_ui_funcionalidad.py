import pytest
from helpers.ui_helpers import login_y_navegar, injectar_token, mock_api_success, CREDENCIALES, SIDEBAR_VISIBLE, SIDEBAR_OCULTO
from pages.login_page import LoginPage, DashboardPage


class TestFuncionalidad:

    @pytest.mark.funcionalidad
    def test_login_validacion_y_sesion(self, page, frontend_url):
        """Validacion de formulario login + sesion persiste al recargar"""
        lp = LoginPage(page)

        lp.goto(frontend_url)
        lp.fill_password("Admin1234!")
        lp.click_login()
        page.wait_for_timeout(400)
        assert lp.is_on_login_page(), "RUT vacio deberia quedarse en login"

        lp.goto(frontend_url)
        lp.fill_rut("12345678-9")
        lp.click_login()
        page.wait_for_timeout(400)
        assert lp.is_on_login_page(), "Password vacio deberia quedarse en login"

        lp.goto(frontend_url)
        lp.login("99999999-9", "WrongPass1!")
        page.wait_for_timeout(1500)
        assert lp.is_on_login_page(), "Credenciales invalidas deberian quedarse en login"

        lp.goto(frontend_url)
        lp.login(CREDENCIALES["ADMIN"]["rut"], CREDENCIALES["ADMIN"]["password"])
        page.wait_for_timeout(2000)
        assert "/dashboard" in page.url, f"Login exitoso deberia ir a /dashboard: {page.url}"

        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        assert "/dashboard" in page.url, "Recarga deberia mantener sesion"

        page.screenshot(path="screenshots/func_login_sesion.png")

    @pytest.mark.funcionalidad
    def test_flujo_admin(self, page, frontend_url):
        """ADMIN: login -> dashboard KPIs -> sidebar -> crear curso+asignatura ->
        crear docente+estudiante -> asignar docente -> comunicaciones -> recarga"""
        lp = LoginPage(page)
        lp.goto(frontend_url)
        lp.login(CREDENCIALES["ADMIN"]["rut"], CREDENCIALES["ADMIN"]["password"])
        page.wait_for_timeout(2500)

        assert "/dashboard" in page.url, f"ADMIN no fue a /dashboard: {page.url}"

        dp = DashboardPage(page)
        for link in SIDEBAR_VISIBLE["ADMIN"]:
            assert dp.sidebar_has_link(link), f"ADMIN sidebar missing: {link}"
        for link in SIDEBAR_OCULTO["ADMIN"]:
            assert dp.sidebar_lacks_link(link), f"ADMIN sidebar should not show: {link}"

        error_kpi = page.locator('.dashboard__error, p:has-text("No se pudieron cargar")')
        assert error_kpi.count() == 0, "Dashboard ADMIN no deberia mostrar error KPI"

        page.goto(f"{frontend_url}/admin/gestion-academica")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        assert "/admin/gestion-academica" in page.url

        page.locator('input[name="nombre"]').first.fill("3ro Medio Test")
        page.locator('#anio-lectivo').fill("2026")
        page.locator('button:has-text("Crear Curso")').click()
        page.wait_for_timeout(1500)

        page.locator('#nombre-asignatura').fill("Fisica Test")
        page.locator('#horas-semanales').fill("4")
        page.locator('button:has-text("Agregar Asignatura")').click()
        page.wait_for_timeout(1500)

        page.goto(f"{frontend_url}/admin/usuarios")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        assert "/admin/usuarios" in page.url

        tab_docentes = page.locator('button:has-text("Docentes")')
        assert tab_docentes.count() > 0, "Tab Docentes no encontrado"
        tab_docentes.click()
        page.wait_for_timeout(800)

        page.locator('#rut').fill("26000001-k")
        page.locator('#nombres').fill("Profesor")
        page.locator('#apellidos').fill("Flujo Final")
        page.locator('#email').fill("profesor.final@test.cl")
        page.locator('#password').fill("Final123!")
        page.locator('#confirmPassword').fill("Final123!")
        page.locator('#rol').select_option("DOCENTE")
        page.wait_for_timeout(300)
        page.locator('button:has-text("Crear usuario")').click()
        page.wait_for_timeout(2000)

        tab_estudiantes = page.locator('button:has-text("Estudiantes")')
        assert tab_estudiantes.count() > 0, "Tab Estudiantes no encontrado"
        tab_estudiantes.click()
        page.wait_for_timeout(800)

        page.locator('#rut').fill("26000003-2")
        page.locator('#nombres').fill("Alumno")
        page.locator('#apellidos').fill("Flujo Final")
        page.locator('#email').fill("alumno.final@test.cl")
        page.locator('#password').fill("Final123!")
        page.locator('#confirmPassword').fill("Final123!")
        page.locator('#rol').select_option("ESTUDIANTE")
        page.wait_for_timeout(300)
        page.locator('button:has-text("Crear usuario")').click()
        page.wait_for_timeout(2000)

        page.goto(f"{frontend_url}/admin/asignacion-docentes")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        assert "/admin/asignacion-docentes" in page.url
        selects = page.locator('select')
        for i in range(min(selects.count(), 3)):
            if selects.nth(i).locator('option').count() > 1:
                selects.nth(i).select_option(index=1)
                page.wait_for_timeout(300)
        btn_asignar = page.locator('button:has-text("Asignar"), button:has-text("Guardar")')
        if btn_asignar.count() > 0:
            btn_asignar.first.click()
            page.wait_for_timeout(1500)

        page.goto(f"{frontend_url}/comunicaciones")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        assert "/comunicaciones" in page.url

        page.goto(f"{frontend_url}/comunicaciones/redactar")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        assert "/comunicaciones/redactar" in page.url

        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        assert "/comunicaciones/redactar" in page.url, "Recarga deberia mantener sesion"

        page.screenshot(path="screenshots/func_flujo_admin.png")

    @pytest.mark.funcionalidad
    def test_flujo_docente(self, page, frontend_url):
        """DOCENTE: login -> /calificaciones -> sidebar -> registrar notas ->
        tomar asistencia -> historial -> anotaciones -> comunicaciones -> dashboard error KPI"""
        lp = LoginPage(page)
        lp.goto(frontend_url)
        lp.login(CREDENCIALES["DOCENTE"]["rut"], CREDENCIALES["DOCENTE"]["password"])
        page.wait_for_timeout(2500)

        assert "/calificaciones" in page.url, f"DOCENTE no fue a /calificaciones: {page.url}"

        dp = DashboardPage(page)
        for link in SIDEBAR_VISIBLE["DOCENTE"]:
            assert dp.sidebar_has_link(link), f"DOCENTE sidebar missing: {link}"
        for link in SIDEBAR_OCULTO["DOCENTE"]:
            assert dp.sidebar_lacks_link(link), f"DOCENTE sidebar should not show: {link}"

        curso = page.locator('select[id], #select-curso').first
        if curso.count() > 0 and curso.locator('option').count() > 1:
            curso.select_option(index=1)
            page.wait_for_timeout(800)
        asig = page.locator('#select-asignatura')
        if asig.count() > 0 and asig.locator('option').count() > 1:
            asig.select_option(index=1)
            page.wait_for_timeout(800)

        notas = page.locator('input.registro-notas__input-nota[type="number"]')
        for i in range(min(notas.count(), 3)):
            notas.nth(i).fill(str(5.0 + i))
            page.wait_for_timeout(200)

        btn_guardar = page.locator('button:has-text("Guardar Calificaciones")')
        if btn_guardar.count() > 0 and btn_guardar.is_enabled():
            btn_guardar.click()
            page.wait_for_timeout(2000)
        assert "/calificaciones" in page.url

        page.goto(f"{frontend_url}/asistencia")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        assert "/asistencia" in page.url

        curso_asist = page.locator('#curso')
        if curso_asist.count() > 0 and curso_asist.locator('option').count() > 1:
            curso_asist.select_option(index=1)
            page.wait_for_timeout(500)
        btn_filtrar = page.locator('button:has-text("Filtrar")')
        if btn_filtrar.count() > 0:
            btn_filtrar.click()
            page.wait_for_timeout(2000)

        asistencias = page.locator('select.asistencia-table__select')
        if asistencias.count() > 0:
            asistencias.nth(0).select_option("ausente")
            page.wait_for_timeout(200)
        if asistencias.count() > 1:
            asistencias.nth(1).select_option("presente")
            page.wait_for_timeout(200)

        btn_guardar_asist = page.locator('button:has-text("Guardar Asistencia")')
        if btn_guardar_asist.count() > 0 and btn_guardar_asist.is_visible():
            btn_guardar_asist.click()
            page.wait_for_timeout(2000)
        assert "/asistencia" in page.url

        for ruta in ["/asistencia/historial", "/asistencia/anotaciones", "/comunicaciones"]:
            page.goto(f"{frontend_url}{ruta}")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1500)
            assert ruta in page.url, f"DOCENTE no pudo acceder a {ruta}: {page.url}"

        page.goto(f"{frontend_url}/comunicaciones/redactar")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        assert "/comunicaciones/redactar" in page.url

        page.goto(f"{frontend_url}/dashboard")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        assert "/dashboard" in page.url or "/calificaciones" in page.url, (
            f"DOCENTE en dashboard. URL: {page.url}"
        )

        page.screenshot(path="screenshots/func_flujo_docente.png")

    @pytest.mark.funcionalidad
    def test_flujo_apoderado(self, page, frontend_url):
        """APODERADO: /mis-calificaciones -> sidebar -> selector pupilo ->
        historial asistencia -> justificar -> comunicaciones"""
        page.goto(f"{frontend_url}/login")
        page.wait_for_load_state("networkidle")
        injectar_token(page, CREDENCIALES["APODERADO"]["rut"], CREDENCIALES["APODERADO"]["password"])
        page.route("**/api/**", mock_api_success)

        page.goto(f"{frontend_url}/mis-calificaciones")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        assert "/mis-calificaciones" in page.url

        dp = DashboardPage(page)
        for link in SIDEBAR_VISIBLE["APODERADO"]:
            assert dp.sidebar_has_link(link), f"APODERADO sidebar missing: {link}"
        for link in SIDEBAR_OCULTO["APODERADO"]:
            assert dp.sidebar_lacks_link(link), f"APODERADO sidebar should not show: {link}"

        selector = page.locator('select, #select-pupilo')
        if selector.count() > 0:
            assert selector.first.is_visible(), "Selector de pupilo deberia ser visible"

        for ruta in ["/asistencia/historial", "/asistencia/justificar", "/comunicaciones"]:
            page.goto(f"{frontend_url}{ruta}")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1500)
            assert ruta in page.url, f"APODERADO no pudo acceder a {ruta}: {page.url}"

        page.screenshot(path="screenshots/func_flujo_apoderado.png")

    @pytest.mark.funcionalidad
    def test_flujo_estudiante(self, page, frontend_url):
        """ESTUDIANTE: /mis-calificaciones -> sidebar -> historial asistencia -> mensajes"""
        page.goto(f"{frontend_url}/login")
        page.wait_for_load_state("networkidle")
        injectar_token(page, CREDENCIALES["ESTUDIANTE"]["rut"], CREDENCIALES["ESTUDIANTE"]["password"])
        page.route("**/api/**", mock_api_success)

        page.goto(f"{frontend_url}/mis-calificaciones")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        assert "/mis-calificaciones" in page.url

        dp = DashboardPage(page)
        for link in SIDEBAR_VISIBLE["ESTUDIANTE"]:
            assert dp.sidebar_has_link(link), f"ESTUDIANTE sidebar missing: {link}"
        for link in SIDEBAR_OCULTO["ESTUDIANTE"]:
            assert dp.sidebar_lacks_link(link), f"ESTUDIANTE sidebar should not show: {link}"

        for ruta in ["/asistencia/historial", "/comunicaciones"]:
            page.goto(f"{frontend_url}{ruta}")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1500)
            assert ruta in page.url, f"ESTUDIANTE no pudo acceder a {ruta}: {page.url}"

        page.screenshot(path="screenshots/func_flujo_estudiante.png")
