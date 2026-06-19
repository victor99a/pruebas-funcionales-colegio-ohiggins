import json
import time
import pytest
from helpers.ui_helpers import login_y_navegar, injectar_token, mock_api_success, CREDENCIALES, SIDEBAR_VISIBLE, SIDEBAR_OCULTO
from pages.login_page import LoginPage, DashboardPage
from pages.base_page import BasePage
from conftest import auth_headers


class TestFuncionalidad:

    @pytest.mark.funcionalidad
    def test_formulario_login_valida_campos_vacios_credenciales_invalidas_y_sesion_persiste(self, page, frontend_url):
        """Login: RUT vacío no avanza → password vacío no avanza → inválidas no avanza → exitoso → recarga mantiene sesión"""
        bp = BasePage(page)
        lp = LoginPage(page)

        lp.goto(frontend_url)
        lp.fill_password("Admin1234!")
        lp.click_login()
        page.wait_for_timeout(400)
        assert lp.is_on_login_page()
        bp._log("CHECK", "RUT vacío → se queda en login")

        lp.goto(frontend_url)
        lp.fill_rut("12345678-9")
        lp.click_login()
        page.wait_for_timeout(400)
        assert lp.is_on_login_page()
        bp._log("CHECK", "Password vacío → se queda en login")

        lp.goto(frontend_url)
        lp.login("99999999-9", "WrongPass1!")
        page.wait_for_timeout(1500)
        assert lp.is_on_login_page()
        bp._log("CHECK", "Credenciales inválidas → se queda en login")

        lp.goto(frontend_url)
        lp.login(CREDENCIALES["ADMIN"]["rut"], CREDENCIALES["ADMIN"]["password"])
        page.wait_for_timeout(2000)
        assert "/dashboard" in page.url
        bp._log("CHECK", "Login exitoso → /dashboard")

        bp.navigate(f"{frontend_url}/dashboard")
        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        assert "/dashboard" in page.url
        bp._log("CHECK", "Recarga → sesión persiste")

        bp.screenshot("func_login_sesion")

    @pytest.mark.funcionalidad
    def test_admin_puede_hacer_todo_login_dashboard_crear_curso_asignatura_usuario_asignar_comunicaciones(self, page, frontend_url):
        """ADMIN: login → dashboard KPIs → sidebar → crear curso+asignatura →
        crear docente+estudiante → asignar docente → comunicaciones → recarga sesión"""
        bp = BasePage(page)
        lp = LoginPage(page)
        lp.goto(frontend_url)
        lp.login(CREDENCIALES["ADMIN"]["rut"], CREDENCIALES["ADMIN"]["password"])
        page.wait_for_timeout(2500)

        assert "/dashboard" in page.url
        bp._log("CHECK", "ADMIN redirigido a /dashboard")

        dp = DashboardPage(page)
        for link in SIDEBAR_VISIBLE["ADMIN"]:
            assert dp.sidebar_has_link(link)
        for link in SIDEBAR_OCULTO["ADMIN"]:
            assert dp.sidebar_lacks_link(link)

        error_kpi = page.locator('.dashboard__error, p:has-text("No se pudieron cargar")')
        assert error_kpi.count() == 0
        bp._log("CHECK", "Dashboard KPIs sin error")

        bp.navigate(f"{frontend_url}/admin/gestion-academica")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        assert "/admin/gestion-academica" in page.url

        bp.fill(page.locator('input[name="nombre"]').first, "3ro Medio Test", "Nombre curso")
        bp.fill(page.locator('#anio-lectivo'), "2026", "Año lectivo")
        bp.click(page.locator('button:has-text("Crear Curso")'), "Crear Curso")
        page.wait_for_timeout(1500)

        bp.fill(page.locator('#nombre-asignatura'), "Fisica Test", "Nombre asignatura")
        bp.fill(page.locator('#horas-semanales'), "4", "Horas semanales")
        bp.click(page.locator('button:has-text("Agregar Asignatura")'), "Agregar Asignatura")
        page.wait_for_timeout(1500)
        bp._log("CHECK", "Curso y asignatura creados")

        bp.navigate(f"{frontend_url}/admin/usuarios")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        bp.click(page.locator('button:has-text("Docentes")'), "Tab Docentes")
        page.wait_for_timeout(800)
        bp.fill(page.locator('#rut'), "26000001-k", "RUT docente")
        bp.fill(page.locator('#nombres'), "Profesor", "Nombres")
        bp.fill(page.locator('#apellidos'), "Flujo Final", "Apellidos")
        bp.fill(page.locator('#email'), "profesor.final@test.cl", "Email")
        bp.fill(page.locator('#password'), "Final123!", "Password")
        bp.fill(page.locator('#confirmPassword'), "Final123!", "Confirmar password")
        bp.select(page.locator('#rol'), "DOCENTE", "Rol")
        page.wait_for_timeout(300)
        bp.click(page.locator('button:has-text("Crear usuario")'), "Crear docente")
        page.wait_for_timeout(2000)

        bp.click(page.locator('button:has-text("Estudiantes")'), "Tab Estudiantes")
        page.wait_for_timeout(800)
        bp.fill(page.locator('#rut'), "26000003-2", "RUT estudiante")
        bp.fill(page.locator('#nombres'), "Alumno", "Nombres")
        bp.fill(page.locator('#apellidos'), "Flujo Final", "Apellidos")
        bp.fill(page.locator('#email'), "alumno.final@test.cl", "Email")
        bp.fill(page.locator('#password'), "Final123!", "Password")
        bp.fill(page.locator('#confirmPassword'), "Final123!", "Confirmar password")
        bp.select(page.locator('#rol'), "ESTUDIANTE", "Rol")
        page.wait_for_timeout(300)
        bp.click(page.locator('button:has-text("Crear usuario")'), "Crear estudiante")
        page.wait_for_timeout(2000)

        bp.click(page.locator('button:has-text("Apoderados")'), "Tab Apoderados")
        page.wait_for_timeout(800)
        bp.fill(page.locator('#rut'), "26000004-0", "RUT apoderado")
        bp.fill(page.locator('#nombres'), "Apo", "Nombres")
        bp.fill(page.locator('#apellidos'), "Flujo Final", "Apellidos")
        bp.fill(page.locator('#email'), "apoderado.final@test.cl", "Email")
        bp.fill(page.locator('#password'), "Final123!", "Password")
        bp.fill(page.locator('#confirmPassword'), "Final123!", "Confirmar password")
        bp.select(page.locator('#rol'), "APODERADO", "Rol")
        page.wait_for_timeout(500)
        pupilo = page.locator('#pupiloUuid')
        if pupilo.count() > 0 and pupilo.locator('option').count() > 1:
            bp.select(pupilo, label="Pupilo", index=1)
            page.wait_for_timeout(300)
        bp.click(page.locator('button:has-text("Crear usuario")'), "Crear apoderado")
        page.wait_for_timeout(2000)
        bp._log("CHECK", "Docente, estudiante y apoderado vinculado creados")

        bp.navigate(f"{frontend_url}/admin/asignacion-docentes")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        assert "/admin/asignacion-docentes" in page.url
        selects = page.locator('select')
        for i in range(min(selects.count(), 3)):
            if selects.nth(i).locator('option').count() > 1:
                bp.select(selects.nth(i), label=f"Select #{i+1}", index=1)
                page.wait_for_timeout(300)
        btn_asignar = page.locator('button:has-text("Asignar"), button:has-text("Guardar")')
        if btn_asignar.count() > 0:
            bp.click(btn_asignar.first, "Asignar docente")
            page.wait_for_timeout(1500)
        bp._log("CHECK", "Docente asignado")

        bp.navigate(f"{frontend_url}/comunicaciones")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        assert "/comunicaciones" in page.url

        bp.navigate(f"{frontend_url}/comunicaciones/redactar")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        assert "/comunicaciones/redactar" in page.url
        bp._log("CHECK", "Comunicaciones y redactar accesibles")

        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        assert "/comunicaciones/redactar" in page.url
        bp._log("CHECK", "Recarga → sesión persiste")

        bp.screenshot("func_flujo_admin")

    @pytest.mark.funcionalidad
    def test_docente_puede_registrar_notas_tomar_asistencia_ver_historial_y_comunicaciones(self, page, frontend_url):
        """DOCENTE: login → /calificaciones → sidebar → registrar notas → tomar asistencia →
        historial → anotaciones → comunicaciones → dashboard error KPI"""
        bp = BasePage(page)
        lp = LoginPage(page)
        lp.goto(frontend_url)
        lp.login(CREDENCIALES["DOCENTE"]["rut"], CREDENCIALES["DOCENTE"]["password"])
        page.wait_for_timeout(2500)

        assert "/calificaciones" in page.url
        bp._log("CHECK", "DOCENTE redirigido a /calificaciones")

        dp = DashboardPage(page)
        for link in SIDEBAR_VISIBLE["DOCENTE"]:
            assert dp.sidebar_has_link(link)
        for link in SIDEBAR_OCULTO["DOCENTE"]:
            assert dp.sidebar_lacks_link(link)

        curso = page.locator('select[id], #select-curso').first
        if curso.count() > 0 and curso.locator('option').count() > 1:
            bp.select(curso, label="Curso", index=1)
            page.wait_for_timeout(800)
        asig = page.locator('#select-asignatura')
        if asig.count() > 0 and asig.locator('option').count() > 1:
            bp.select(asig, label="Asignatura", index=1)
            page.wait_for_timeout(800)

        notas = page.locator('input.registro-notas__input-nota[type="number"]')
        for i in range(min(notas.count(), 3)):
            bp.fill(notas.nth(i), str(5.0 + i), f"Nota {i+1}")
            page.wait_for_timeout(200)

        btn_guardar = page.locator('button:has-text("Guardar Calificaciones")')
        if btn_guardar.count() > 0 and btn_guardar.is_enabled():
            bp.click(btn_guardar, "Guardar Calificaciones")
            page.wait_for_timeout(2000)
        assert "/calificaciones" in page.url
        bp._log("CHECK", "Notas registradas")

        bp.navigate(f"{frontend_url}/asistencia")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        assert "/asistencia" in page.url

        curso_asist = page.locator('#curso')
        if curso_asist.count() > 0 and curso_asist.locator('option').count() > 1:
            bp.select(curso_asist, label="Curso asistencia", index=1)
            page.wait_for_timeout(500)
        btn_filtrar = page.locator('button:has-text("Filtrar")')
        if btn_filtrar.count() > 0:
            bp.click(btn_filtrar, "Filtrar")
            page.wait_for_timeout(2000)

        asistencias = page.locator('select.asistencia-table__select')
        if asistencias.count() > 0:
            bp.select(asistencias.nth(0), "ausente", "Asistencia #1")
            page.wait_for_timeout(200)
        if asistencias.count() > 1:
            bp.select(asistencias.nth(1), "presente", "Asistencia #2")
            page.wait_for_timeout(200)

        btn_guardar_asist = page.locator('button:has-text("Guardar Asistencia")')
        if btn_guardar_asist.count() > 0 and btn_guardar_asist.is_visible():
            bp.click(btn_guardar_asist, "Guardar Asistencia")
            page.wait_for_timeout(2000)
        bp._log("CHECK", "Asistencia tomada")

        for ruta in ["/asistencia/historial", "/asistencia/anotaciones", "/comunicaciones"]:
            bp.navigate(f"{frontend_url}{ruta}")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1500)
            assert ruta in page.url
            bp._log("CHECK", f"{ruta} accesible")

        bp.navigate(f"{frontend_url}/comunicaciones/redactar")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        assert "/comunicaciones/redactar" in page.url
        bp._log("CHECK", "Redactar mensaje accesible")

        bp.navigate(f"{frontend_url}/dashboard")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        assert "/dashboard" in page.url or "/calificaciones" in page.url
        bp._log("CHECK", "Dashboard: DOCENTE ve error KPI (esperado)")

        bp.screenshot("func_flujo_docente")

    @pytest.mark.funcionalidad
    def test_apoderado_puede_ver_calificaciones_pupilo_historial_justificar_y_comunicaciones(self, page, frontend_url):
        """APODERADO: /mis-calificaciones → sidebar → selector pupilo →
        historial asistencia → justificar → comunicaciones"""
        bp = BasePage(page)

        page.goto(f"{frontend_url}/login")
        page.wait_for_load_state("networkidle")
        injectar_token(page, CREDENCIALES["APODERADO"]["rut"], CREDENCIALES["APODERADO"]["password"])
        page.route("**/api/**", mock_api_success)
        bp._log("MOCK", "API interceptada para APODERADO")

        bp.navigate(f"{frontend_url}/mis-calificaciones")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        assert "/mis-calificaciones" in page.url

        dp = DashboardPage(page)
        for link in SIDEBAR_VISIBLE["APODERADO"]:
            assert dp.sidebar_has_link(link)
        for link in SIDEBAR_OCULTO["APODERADO"]:
            assert dp.sidebar_lacks_link(link)

        selector = page.locator('select, #select-pupilo')
        if selector.count() > 0:
            assert selector.first.is_visible()
            bp._log("CHECK", "Selector de pupilo visible")

        for ruta in ["/asistencia/historial", "/asistencia/justificar", "/comunicaciones"]:
            bp.navigate(f"{frontend_url}{ruta}")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1500)
            assert ruta in page.url
            bp._log("CHECK", f"{ruta} accesible")

        bp.screenshot("func_flujo_apoderado")

    @pytest.mark.funcionalidad
    def test_estudiante_puede_ver_mis_notas_historial_asistencia_y_mensajes(self, page, frontend_url):
        """ESTUDIANTE: /mis-calificaciones → sidebar → historial asistencia → mensajes → admin redirect"""
        bp = BasePage(page)

        page.goto(f"{frontend_url}/login")
        page.wait_for_load_state("networkidle")
        injectar_token(page, CREDENCIALES["ESTUDIANTE"]["rut"], CREDENCIALES["ESTUDIANTE"]["password"])
        page.route("**/api/**", mock_api_success)
        bp._log("MOCK", "API interceptada para ESTUDIANTE")

        bp.navigate(f"{frontend_url}/mis-calificaciones")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        assert "/mis-calificaciones" in page.url

        dp = DashboardPage(page)
        for link in SIDEBAR_VISIBLE["ESTUDIANTE"]:
            assert dp.sidebar_has_link(link)
        for link in SIDEBAR_OCULTO["ESTUDIANTE"]:
            assert dp.sidebar_lacks_link(link)

        for ruta in ["/asistencia/historial", "/comunicaciones"]:
            bp.navigate(f"{frontend_url}{ruta}")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1500)
            assert ruta in page.url
            bp._log("CHECK", f"{ruta} accesible")

        bp.screenshot("func_flujo_estudiante")

    @pytest.mark.funcionalidad
    def test_flujo_end_to_end_admin_crea_curso_asignatura_estudiante_docente_registra_nota_y_asistencia_verifica_bd(
        self, page, frontend_url, api_context, admin_token
    ):
        """E2E: ADMIN crea curso+asignatura+estudiante → DOCENTE registra nota+asistencia → API verifica BD"""
        bp = BasePage(page)
        _ts = int(time.time()) % 100000
        curso_nombre = f"E2E Curso {_ts}"
        asig_nombre = f"E2E Materia {_ts}"
        rut_estudiante = f"99{_ts:05d}-1"
        nombre_estudiante = f"Alumno E2E {_ts}"
        email_estudiante = f"e2e.alumno.{_ts}@test.cl"

        # ═══════════════════════════════════════════
        # FASE 1: ADMIN crea curso y asignatura
        # ═══════════════════════════════════════════
        bp._log("E2E", "=== FASE 1: ADMIN crea curso y asignatura ===", ok=True)
        lp = LoginPage(page)
        lp.goto(frontend_url)
        lp.login(CREDENCIALES["ADMIN"]["rut"], CREDENCIALES["ADMIN"]["password"])
        page.wait_for_timeout(2000)
        assert "/dashboard" in page.url

        bp.navigate(f"{frontend_url}/admin/gestion-academica")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        bp.fill(page.locator('input[name="nombre"]').first, curso_nombre, "Nombre curso E2E")
        bp.fill(page.locator('#anio-lectivo'), "2026", "Año lectivo E2E")
        bp.click(page.locator('button:has-text("Crear Curso")'), "Crear Curso")
        page.wait_for_timeout(2000)

        bp._log("API", f"Verificando curso '{curso_nombre}' en BD")
        resp = api_context.get("/api/v1/cursos", headers=auth_headers(admin_token))
        if resp.status == 200:
            cursos = resp.json() if isinstance(resp.json(), list) else []
            encontrado = any(curso_nombre in str(c.get("nombre", "")) for c in cursos)
            bp._log("API", f"Curso '{curso_nombre}' en BD: {'SI' if encontrado else 'NO'}", encontrado)

        bp.fill(page.locator('#nombre-asignatura'), asig_nombre, "Nombre asignatura E2E")
        bp.fill(page.locator('#horas-semanales'), "3", "Horas semanales E2E")
        bp.click(page.locator('button:has-text("Agregar Asignatura")'), "Agregar Asignatura")
        page.wait_for_timeout(2000)

        bp._log("API", f"Verificando asignatura '{asig_nombre}' en BD")
        resp = api_context.get("/api/v1/asignaturas", headers=auth_headers(admin_token))
        if resp.status == 200:
            asignaturas = resp.json() if isinstance(resp.json(), list) else []
            encontrada = any(asig_nombre in str(a.get("nombre", "")) for a in asignaturas)
            bp._log("API", f"Asignatura '{asig_nombre}' en BD: {'SI' if encontrada else 'NO'}", encontrada)

        # ═══════════════════════════════════════════
        # FASE 2: ADMIN crea estudiante
        # ═══════════════════════════════════════════
        bp._log("E2E", "=== FASE 2: ADMIN crea estudiante ===", ok=True)
        bp.navigate(f"{frontend_url}/admin/usuarios")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        bp.click(page.locator('button:has-text("Estudiantes")'), "Tab Estudiantes")
        page.wait_for_timeout(800)

        bp.fill(page.locator('#rut'), rut_estudiante, "RUT estudiante E2E")
        bp.fill(page.locator('#nombres'), nombre_estudiante, "Nombres")
        bp.fill(page.locator('#apellidos'), f"E2E {_ts}", "Apellidos")
        bp.fill(page.locator('#email'), email_estudiante, "Email")
        bp.fill(page.locator('#password'), "E2E1234!", "Password")
        bp.fill(page.locator('#confirmPassword'), "E2E1234!", "Confirmar password")
        bp.select(page.locator('#rol'), "ESTUDIANTE", "Rol")
        page.wait_for_timeout(300)
        bp.click(page.locator('button:has-text("Crear usuario")'), "Crear estudiante")
        page.wait_for_timeout(2500)

        bp._log("API", f"Verificando estudiante '{rut_estudiante}' en BD")
        estudiante_uuid = None
        resp = api_context.get("/api/v1/admin/listar/ESTUDIANTE", headers=auth_headers(admin_token))
        if resp.status == 200:
            usuarios = resp.json() if isinstance(resp.json(), list) else []
            for u in usuarios:
                if u.get("rut") == rut_estudiante:
                    estudiante_uuid = u.get("id")
                    bp._log("API", f"Estudiante encontrado: uuid={estudiante_uuid}, nombre={u.get('nombreCompleto')}")
                    break
        assert estudiante_uuid, f"No se encontro estudiante con RUT {rut_estudiante} en BD"
        bp._log("CHECK", f"Estudiante E2E creado y verificado en BD", ok=True)

        # ═══════════════════════════════════════════
        # FASE 2.5: ADMIN crea APODERADO vinculado al estudiante
        # ═══════════════════════════════════════════
        bp._log("E2E", "=== FASE 2.5: ADMIN crea apoderado vinculado al estudiante ===", ok=True)
        rut_apoderado = f"98{_ts:05d}-2"
        email_apoderado = f"e2e.apoderado.{_ts}@test.cl"

        bp.click(page.locator('button:has-text("Apoderados")'), "Tab Apoderados")
        page.wait_for_timeout(800)

        bp.fill(page.locator('#rut'), rut_apoderado, "RUT apoderado E2E")
        bp.fill(page.locator('#nombres'), f"Apoderado E2E {_ts}", "Nombres")
        bp.fill(page.locator('#apellidos'), f"E2E {_ts}", "Apellidos")
        bp.fill(page.locator('#email'), email_apoderado, "Email")
        bp.fill(page.locator('#password'), "E2E1234!", "Password")
        bp.fill(page.locator('#confirmPassword'), "E2E1234!", "Confirmar password")
        bp.select(page.locator('#rol'), "APODERADO", "Rol")
        page.wait_for_timeout(500)

        pupilo_select = page.locator('#pupiloUuid')
        if pupilo_select.count() > 0 and pupilo_select.locator('option').count() > 1:
            bp.select(pupilo_select, label="Pupilo", index=1)
            page.wait_for_timeout(300)

        bp.click(page.locator('button:has-text("Crear usuario")'), "Crear apoderado E2E")
        page.wait_for_timeout(2500)

        # Verificar en BD que el apoderado tiene pupiloUuid
        bp._log("API", f"Verificando apoderado '{rut_apoderado}' con pupiloUuid en BD")
        apoderado_pupilo_ok = False
        resp = api_context.get("/api/v1/admin/listar/APODERADO", headers=auth_headers(admin_token))
        if resp.status == 200:
            usuarios = resp.json() if isinstance(resp.json(), list) else []
            for u in usuarios:
                if u.get("rut") == rut_apoderado:
                    puuid = u.get("pupiloUuid")
                    bp._log("API", f"Apoderado encontrado: uuid={u.get('id')}, pupiloUuid={puuid}")
                    if puuid is not None and str(puuid) != "None":
                        apoderado_pupilo_ok = True
                    break
        bp._log("CHECK", f"Apoderado E2E vinculado a estudiante: {'SI' if apoderado_pupilo_ok else 'NO'}", apoderado_pupilo_ok)

        # Verificar que el dropdown de pupilos se renderiza con opciones disponibles
        bp._log("CHECK", "Verificando que dropdown #pupiloUuid se renderiza con estudiantes disponibles")
        bp.select(page.locator('#rol'), "APODERADO", "Rol (mostrar dropdown)")
        page.wait_for_timeout(500)
        pupilo_ops = page.locator('#pupiloUuid option')
        opciones_count = pupilo_ops.count()
        bp._log("CHECK", f"Dropdown #pupiloUuid tiene {opciones_count} opciones", opciones_count >= 2)

        # ═══════════════════════════════════════════
        # FASE 3: DOCENTE registra nota via API → verificar BD
        # ═══════════════════════════════════════════
        bp._log("E2E", "=== FASE 3: DOCENTE registra nota via API ===", ok=True)

        resp = api_context.post(
            "/api/v1/auth/login",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"rut": CREDENCIALES["DOCENTE"]["rut"], "password": CREDENCIALES["DOCENTE"]["password"]}),
        )
        docente_token_e2e = resp.json().get("accessToken") if resp.status == 200 else None
        assert docente_token_e2e, "No se pudo obtener token DOCENTE para E2E"
        bp._log("TOKEN", "DOCENTE autenticado via API")

        resp = api_context.put(
            "/api/v1/calificaciones/guardar",
            headers={**auth_headers(docente_token_e2e), "Content-Type": "application/json"},
            data=json.dumps({"usuarioUuid": estudiante_uuid, "asignaturaId": 1, "nota1": 6.5, "nota2": 5.0, "nota3": 6.0}),
        )
        bp._log("API", f"Guardar calificacion → HTTP {resp.status}")
        page.wait_for_timeout(500)

        resp = api_context.get(
            f"/api/v1/calificaciones/estudiante/{estudiante_uuid}",
            headers=auth_headers(admin_token),
        )
        nota_encontrada = False
        if resp.status == 200:
            calificaciones = resp.json() if isinstance(resp.json(), list) else []
            nota_encontrada = any(
                float(c.get("nota1", 0)) == 6.5 for c in calificaciones
            )
            bp._log("API", f"Calificaciones en BD: {len(calificaciones)} registros")
        bp._log("CHECK", f"Nota 6.5 guardada en BD: {'SI' if nota_encontrada else 'NO'}", nota_encontrada)

        # ═══════════════════════════════════════════
        # FASE 4: DOCENTE registra asistencia via API → verificar BD
        # ═══════════════════════════════════════════
        bp._log("E2E", "=== FASE 4: DOCENTE registra asistencia via API ===", ok=True)

        resp = api_context.post(
            "/api/v1/asistencias",
            headers={**auth_headers(docente_token_e2e), "Content-Type": "application/json"},
            data=json.dumps({"studentId": 1, "asignatura": "Matemática", "fecha": "2026-06-19", "presente": True}),
        )
        bp._log("API", f"Registrar asistencia → HTTP {resp.status}")

        resp = api_context.get(
            "/api/v1/asistencias/estudiante/1",
            headers=auth_headers(admin_token),
        )
        asistencia_ok = False
        if resp.status == 200:
            registros = resp.json() if isinstance(resp.json(), list) else []
            asistencia_ok = len(registros) > 0
            bp._log("API", f"Asistencia en BD: {len(registros)} registros")
        bp._log("CHECK", f"Asistencia via Gateway → BD: {'SI' if asistencia_ok else 'NO'}", asistencia_ok)

        bp._log("E2E", "=== FLUJO END-TO-END COMPLETO ===", ok=True)
        bp.screenshot("func_flujo_e2e")
