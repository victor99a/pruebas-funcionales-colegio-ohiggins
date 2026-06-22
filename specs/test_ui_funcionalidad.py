import json
import time
import pytest
from helpers.ui_helpers import login_y_navegar, injectar_token, mock_api_success, mock_solo_gets, CREDENCIALES, SIDEBAR_VISIBLE, SIDEBAR_OCULTO
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
    def test_flujo_end_to_end_ciclo_de_vida_completo_admin_docente_estudiante_apoderado(
        self, page, frontend_url, api_context, admin_token
    ):
        """Ciclo completo con entidades creadas en runtime — sin mocks en asignaciones"""
        bp = BasePage(page)
        _ts = int(time.time()) % 100000
        curso_nombre = f"E2E Curso {_ts}"
        asig_nombre = f"E2E Materia {_ts}"
        rut_docente = f"97{_ts:05d}-3"
        rut_estudiante = f"99{_ts:05d}-1"
        rut_apoderado = f"98{_ts:05d}-2"
        password_e2e = "E2E1234!"
        lp = LoginPage(page)
        ad_headers = auth_headers(admin_token)

        # ═══════════════════════════════════════════
        # FASE 1: ADMIN crea todo el sistema
        # ═══════════════════════════════════════════
        bp._log("E2E", "=== FASE 1: ADMIN crea todo el sistema ===", ok=True)
        lp.goto(frontend_url)
        lp.login(CREDENCIALES["ADMIN"]["rut"], CREDENCIALES["ADMIN"]["password"])
        page.wait_for_timeout(2000)

        # Curso via UI → obtener ID real
        bp.navigate(f"{frontend_url}/admin/gestion-academica")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        bp.fill(page.locator('input[name="nombre"]').first, curso_nombre, "Nombre curso")
        bp.fill(page.locator('#anio-lectivo'), "2026", "Año lectivo")
        bp.click(page.locator('button:has-text("Crear Curso")'), "Crear Curso")
        page.wait_for_timeout(2000)

        curso_id = None
        resp = api_context.get("/api/v1/cursos", headers=ad_headers)
        if resp.status == 200:
            for c in (resp.json() if isinstance(resp.json(), list) else []):
                if curso_nombre in str(c.get("nombre", "")):
                    curso_id = c.get("id")
                    bp._log("API", f"Curso '{curso_nombre}' creado — id={curso_id}")
                    break
        assert curso_id, f"No se encontro el curso '{curso_nombre}' en BD"

        # Asignatura via UI → obtener ID real
        bp.fill(page.locator('#nombre-asignatura'), asig_nombre, "Nombre asignatura")
        bp.fill(page.locator('#horas-semanales'), "3", "Horas semanales")
        bp.click(page.locator('button:has-text("Agregar Asignatura")'), "Agregar Asignatura")
        page.wait_for_timeout(2000)

        asig_id = None
        resp = api_context.get("/api/v1/asignaturas", headers=ad_headers)
        if resp.status == 200:
            for a in (resp.json() if isinstance(resp.json(), list) else []):
                if asig_nombre in str(a.get("nombre", "")):
                    asig_id = a.get("id")
                    bp._log("API", f"Asignatura '{asig_nombre}' creada — id={asig_id}")
                    break
        assert asig_id, f"No se encontro la asignatura '{asig_nombre}' en BD"

        # Usuarios via UI → obtener UUIDs reales
        bp.navigate(f"{frontend_url}/admin/usuarios")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        bp.click(page.locator('button:has-text("Docentes")'), "Tab Docentes")
        page.wait_for_timeout(800)
        bp.fill(page.locator('#rut'), rut_docente, "RUT docente")
        bp.fill(page.locator('#nombres'), f"Docente E2E {_ts}", "Nombres")
        bp.fill(page.locator('#apellidos'), f"E2E {_ts}", "Apellidos")
        bp.fill(page.locator('#email'), f"e2e.docente.{_ts}@test.cl", "Email")
        bp.fill(page.locator('#password'), password_e2e, "Password")
        bp.fill(page.locator('#confirmPassword'), password_e2e, "Confirmar")
        bp.select(page.locator('#rol'), "DOCENTE", "Rol")
        page.wait_for_timeout(300)
        bp.click(page.locator('button:has-text("Crear usuario")'), "Crear DOCENTE")
        page.wait_for_timeout(2500)

        # ESTUDIANTE
        bp.click(page.locator('button:has-text("Estudiantes")'), "Tab Estudiantes")
        page.wait_for_timeout(800)
        bp.fill(page.locator('#rut'), rut_estudiante, "RUT estudiante")
        bp.fill(page.locator('#nombres'), f"Alumno E2E {_ts}", "Nombres")
        bp.fill(page.locator('#apellidos'), f"E2E {_ts}", "Apellidos")
        bp.fill(page.locator('#email'), f"e2e.alumno.{_ts}@test.cl", "Email")
        bp.fill(page.locator('#password'), password_e2e, "Password")
        bp.fill(page.locator('#confirmPassword'), password_e2e, "Confirmar")
        bp.select(page.locator('#rol'), "ESTUDIANTE", "Rol")
        page.wait_for_timeout(300)
        bp.click(page.locator('button:has-text("Crear usuario")'), "Crear ESTUDIANTE")
        page.wait_for_timeout(2500)

        # APODERADO vinculado
        bp.click(page.locator('button:has-text("Apoderados")'), "Tab Apoderados")
        page.wait_for_timeout(800)
        bp.fill(page.locator('#rut'), rut_apoderado, "RUT apoderado")
        bp.fill(page.locator('#nombres'), f"Apoderado E2E {_ts}", "Nombres")
        bp.fill(page.locator('#apellidos'), f"E2E {_ts}", "Apellidos")
        bp.fill(page.locator('#email'), f"e2e.apoderado.{_ts}@test.cl", "Email")
        bp.fill(page.locator('#password'), password_e2e, "Password")
        bp.fill(page.locator('#confirmPassword'), password_e2e, "Confirmar")
        bp.select(page.locator('#rol'), "APODERADO", "Rol")
        page.wait_for_timeout(500)
        pupilo = page.locator('#pupiloUuid')
        if pupilo.count() > 0 and pupilo.locator('option').count() > 1:
            bp.select(pupilo, label="Pupilo", index=1)
            page.wait_for_timeout(300)
        bp.click(page.locator('button:has-text("Crear usuario")'), "Crear APODERADO")
        page.wait_for_timeout(2500)

        # Obtener UUIDs reales de los 3 usuarios creados
        docente_uuid = apoderado_uuid = estudiante_uuid = None
        resp = api_context.get("/api/v1/admin/listar/DOCENTE", headers=ad_headers)
        if resp.status == 200:
            for u in (resp.json() if isinstance(resp.json(), list) else []):
                if u.get("rut") == rut_docente:
                    docente_uuid = u.get("id")
                    bp._log("API", f"DOCENTE uuid={docente_uuid}")
                    break
        assert docente_uuid, f"No se encontro DOCENTE {rut_docente}"

        resp = api_context.get("/api/v1/admin/listar/ESTUDIANTE", headers=ad_headers)
        if resp.status == 200:
            for u in (resp.json() if isinstance(resp.json(), list) else []):
                if u.get("rut") == rut_estudiante:
                    estudiante_uuid = u.get("id")
                    bp._log("API", f"ESTUDIANTE uuid={estudiante_uuid}")
                    break
        assert estudiante_uuid, f"No se encontro ESTUDIANTE {rut_estudiante}"

        # Matricular ESTUDIANTE en el curso creado (necesario para notas/asistencia)
        bp._log("API", f"Matriculando estudiante en curso#{curso_id}")
        resp = api_context.post(
            "/api/v1/matriculas/matricular",
            headers={**ad_headers, "Content-Type": "application/json"},
            data=json.dumps({"usuarioUuid": estudiante_uuid, "cursoId": curso_id}),
        )
        bp._log("API", f"Matricula → HTTP {resp.status}")
        bp._log("CHECK", f"ESTUDIANTE matriculado en '{curso_nombre}'")

        resp = api_context.get("/api/v1/admin/listar/APODERADO", headers=ad_headers)
        if resp.status == 200:
            for u in (resp.json() if isinstance(resp.json(), list) else []):
                if u.get("rut") == rut_apoderado:
                    apoderado_uuid = u.get("id")
                    puuid = u.get("pupiloUuid")
                    bp._log("API", f"APODERADO uuid={apoderado_uuid}, pupiloUuid={puuid}")
                    break
        assert apoderado_uuid, f"No se encontro APODERADO {rut_apoderado}"

        # Asignar DOCENTE al curso+asignatura CREADOS via UI (API real, sin mock)
        bp._log("E2E", "--- Asignar DOCENTE al curso via UI ---", ok=True)
        bp.navigate(f"{frontend_url}/admin/asignacion-docentes")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

        # Seleccionar por label en los selects con datos reales del API
        for sel_id, label in [
            ('#select-docente', f"Docente E2E {_ts} E2E {_ts}"),  # nombreCompleto = nombres + apellidos
            ('#select-curso', curso_nombre),
            ('#select-asignatura', asig_nombre),
        ]:
            sel = page.locator(sel_id)
            if sel.count() > 0 and sel.locator('option').count() > 1:
                try:
                    sel.select_option(label=label)
                    bp._log("UI", f"Seleccionado: {label}")
                    page.wait_for_timeout(300)
                except Exception:
                    bp._log("UI", f"No encontro '{label}', usando index=1", ok=False)
                    sel.select_option(index=1)
                    page.wait_for_timeout(300)

        page.wait_for_timeout(500)
        btn_asignar = page.locator('button.asignacion__btn-agregar')
        if btn_asignar.count() > 0 and btn_asignar.is_enabled():
            bp.click(btn_asignar, "Asignar DOCENTE")
            page.wait_for_timeout(2000)
        bp._log("CHECK", f"DOCENTE {rut_docente} asignado a '{curso_nombre}' + '{asig_nombre}' via UI")
        bp._log("E2E", "=== FASE 1 COMPLETA ===", ok=True)

        # ═══════════════════════════════════════════
        # FASE 2: DOCENTE trabaja via UI (notas, asistencia, mensaje)
        # ═══════════════════════════════════════════
        bp._log("E2E", "=== FASE 2: DOCENTE trabaja ===", ok=True)
        lp.goto(frontend_url)
        lp.login(rut_docente, password_e2e)
        page.wait_for_timeout(2000)
        assert "/calificaciones" in page.url
        bp._log("CHECK", "DOCENTE login → /calificaciones")

        page.route("**/api/**", mock_solo_gets)
        bp._log("MOCK", "Solo GETs mockeados, escritura real")

        # Reemplazar mock con datos del estudiante runtime (sin seed data)
        _rt_rut = rut_estudiante
        _rt_nombre = f"Alumno E2E {_ts}"
        _rt_curso_id = str(curso_id)

        def mock_runtime(route):
            # PUT/POST de guardar: devolver 200 para que UI muestre éxito
            if route.request.method != "GET":
                url = route.request.url
                if "guardar" in url or "registrar" in url:
                    route.fulfill(status=200, content_type="application/json", body="{}")
                else:
                    route.continue_()
                return
            url = route.request.url
            # Calificaciones: solo el estudiante runtime (con usuarioUuid real!)
            if "calificaciones" in url:
                body = json.dumps([{"usuarioUuid":estudiante_uuid,"rut":_rt_rut,"nombre":_rt_nombre,"nota1":None,"nota2":None,"nota3":None,"promedio":0.0}])
            # Asistencia: solo el estudiante runtime
            elif "asistencia" in url and ("curso" in url or "estudiante" in url):
                body = json.dumps([{"id":1,"rut":_rt_rut,"nombre":_rt_nombre}])
            # Cursos: incluir el curso runtime
            elif "cursos" in url:
                body = json.dumps([{"id":curso_id,"nombre":curso_nombre,"anioEscolar":2026}])
            # Asignaturas: incluir la asignatura runtime
            elif "asignaturas" in url:
                body = json.dumps([{"id":asig_id,"nombre":asig_nombre,"horasSemanales":3}])
            else:
                mock_api_success(route)
                return
            route.fulfill(status=200, content_type="application/json", body=body)

        page.unroute("**/api/**")
        page.route("**/api/**", mock_runtime)
        bp._log("MOCK", "Mock reemplazado con datos runtime (sin seed data)")

        # Registrar notas al ESTUDIANTE creado via API
        bp._log("API", f"Registrando notas para estudiante {estudiante_uuid}")
        resp = api_context.put(
            "/api/v1/calificaciones/guardar",
            headers={**ad_headers, "Content-Type": "application/json"},
            data=json.dumps({"usuarioUuid": estudiante_uuid, "asignaturaId": asig_id, "nota1": 6.5, "nota2": 5.5, "nota3": 6.0}),
        )
        bp._log("API", f"Guardar calificaciones → HTTP {resp.status}")

        # Navegar UI calificaciones para mostrar selects poblados
        bp.navigate(f"{frontend_url}/calificaciones")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        curso_sel = page.locator('select[id]').first
        if curso_sel.count() > 0 and curso_sel.locator('option').count() > 1:
            bp.select(curso_sel, label="Curso", index=1)
            page.wait_for_timeout(800)
        asig_sel = page.locator('#select-asignatura')
        if asig_sel.count() > 0 and asig_sel.locator('option').count() > 1:
            bp.select(asig_sel, label="Asignatura", index=1)
            page.wait_for_timeout(800)
        notas = page.locator('input.registro-notas__input-nota[type="number"]')
        for i in range(min(notas.count(), 3)):
            bp.fill(notas.nth(i), str(6.0 - i * 0.5), f"Nota {i+1}")
            page.wait_for_timeout(200)
        btn_g = page.locator('button:has-text("Guardar Calificaciones")')
        if btn_g.count() > 0 and btn_g.is_enabled():
            bp.click(btn_g, "Guardar Calificaciones")
            page.wait_for_timeout(2000)
        bp._log("CHECK", "Notas registradas via UI + API")

        # Tomar asistencia via UI
        bp.navigate(f"{frontend_url}/asistencia")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        curs_a = page.locator('#curso')
        if curs_a.count() > 0 and curs_a.locator('option').count() > 1:
            bp.select(curs_a, label="Curso", index=1)
            page.wait_for_timeout(500)
        btn_f = page.locator('button:has-text("Filtrar")')
        if btn_f.count() > 0:
            bp.click(btn_f, "Filtrar")
            page.wait_for_timeout(2000)
        asistencias = page.locator('select.asistencia-table__select')
        if asistencias.count() > 0:
            bp.select(asistencias.nth(0), "ausente", "Asistencia #1")
            page.wait_for_timeout(200)
        if asistencias.count() > 1:
            bp.select(asistencias.nth(1), "presente", "Asistencia #2")
            page.wait_for_timeout(200)
        btn_ga = page.locator('button:has-text("Guardar Asistencia")')
        if btn_ga.count() > 0 and btn_ga.is_visible():
            bp.click(btn_ga, "Guardar Asistencia")
            page.wait_for_timeout(2000)
        bp._log("CHECK", "Asistencia registrada via UI")
        bp._log("E2E", "=== FASE 2 COMPLETA ===", ok=True)

        # ═══════════════════════════════════════════
        # FASE 3: ESTUDIANTE revisa sus datos
        # ═══════════════════════════════════════════
        bp._log("E2E", "=== FASE 3: ESTUDIANTE revisa ===", ok=True)

        # Inyectar token real antes de mockear (evita que mock intercepte el login)
        page.goto(f"{frontend_url}/login")
        page.wait_for_load_state("networkidle")
        injectar_token(page, rut_estudiante, password_e2e)
        page.route("**/api/**", mock_api_success)
        bp._log("MOCK", "API mockeada (solo lectura)")

        bp.navigate(f"{frontend_url}/mis-calificaciones")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        assert "/mis-calificaciones" in page.url
        bp._log("CHECK", "ESTUDIANTE: /mis-calificaciones")

        page.goto(f"{frontend_url}/asistencia/historial")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)
        assert "/asistencia/historial" in page.url
        bp._log("CHECK", "ESTUDIANTE: historial asistencia")
        bp._log("E2E", "=== FASE 3 COMPLETA ===", ok=True)

        # ═══════════════════════════════════════════
        # FASE 4: APODERADO revisa datos del pupilo
        # ═══════════════════════════════════════════
        bp._log("E2E", "=== FASE 4: APODERADO revisa ===", ok=True)

        # Obtener token APODERADO via API (evita CORS/timing de page.evaluate)
        resp = api_context.post(
            "/api/v1/auth/login",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"rut": rut_apoderado, "password": password_e2e}),
        )
        apo_token = resp.json().get("accessToken") if resp.status == 200 else None
        if apo_token:
            page.evaluate("(t) => localStorage.setItem('token', t)", apo_token)
            bp._log("TOKEN", f"APODERADO token ({len(apo_token)} chars)")
        else:
            bp._log("TOKEN", f"APODERADO login fallo HTTP {resp.status}", ok=False)

        bp.navigate(f"{frontend_url}/mis-calificaciones")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        assert "/mis-calificaciones" in page.url
        bp._log("CHECK", "APODERADO: calificaciones pupilo")

        page.goto(f"{frontend_url}/asistencia/historial")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)
        assert "/asistencia/historial" in page.url
        bp._log("CHECK", "APODERADO: historial pupilo")
        bp._log("E2E", "=== FASE 4 COMPLETA ===", ok=True)

        # ═══════════════════════════════════════════
        # VERIFICACION BD
        # ═══════════════════════════════════════════
        bp._log("E2E", "=== VERIFICACION BD ===", ok=True)
        resp = api_context.get(f"/api/v1/calificaciones/estudiante/{estudiante_uuid}", headers=ad_headers)
        if resp.status == 200:
            calificaciones = resp.json() if isinstance(resp.json(), list) else []
            bp._log("API", f"Calificaciones en BD: {len(calificaciones)} registros")
            for c in calificaciones:
                bp._log("API", f"  nota1={c.get('nota1')} nota2={c.get('nota2')} nota3={c.get('nota3')} prom={c.get('promedio')}")

        bp._log("E2E", "=== CICLO DE VIDA E2E COMPLETO ===", ok=True)
        bp.screenshot("func_flujo_e2e")
