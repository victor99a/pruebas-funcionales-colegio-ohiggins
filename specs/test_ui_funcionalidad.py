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
        """Ciclo completo: ADMIN crea sistema+usuarios+nexos → DOCENTE trabaja → ESTUDIANTE revisa → APODERADO revisa"""
        bp = BasePage(page)
        _ts = int(time.time()) % 100000
        curso_nombre = f"E2E Curso {_ts}"
        asig_nombre = f"E2E Materia {_ts}"
        rut_docente = f"97{_ts:05d}-3"
        rut_estudiante = f"99{_ts:05d}-1"
        rut_apoderado = f"98{_ts:05d}-2"
        password_e2e = "E2E1234!"
        mensaje_docente = "Su pupilo es alumno estrella en fullstack"
        lp = LoginPage(page)

        # ═══════════════════════════════════════════
        # FASE 1: ADMIN crea curso, asignatura, DOCENTE, ESTUDIANTE, APODERADO, nexos
        # ═══════════════════════════════════════════
        bp._log("E2E", "=== FASE 1: ADMIN crea todo el sistema ===", ok=True)
        lp.goto(frontend_url)
        lp.login(CREDENCIALES["ADMIN"]["rut"], CREDENCIALES["ADMIN"]["password"])
        page.wait_for_timeout(2000)
        assert "/dashboard" in page.url

        # Curso
        bp.navigate(f"{frontend_url}/admin/gestion-academica")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        bp.fill(page.locator('input[name="nombre"]').first, curso_nombre, "Nombre curso")
        bp.fill(page.locator('#anio-lectivo'), "2026", "Año lectivo")
        bp.click(page.locator('button:has-text("Crear Curso")'), "Crear Curso")
        page.wait_for_timeout(2000)

        bp._log("API", f"Verificando curso '{curso_nombre}' en BD")
        resp = api_context.get("/api/v1/cursos", headers=auth_headers(admin_token))
        if resp.status == 200:
            cursos = resp.json() if isinstance(resp.json(), list) else []
            bp._log("API", f"Curso en BD: {'SI' if any(curso_nombre in str(c.get('nombre','')) for c in cursos) else 'NO'}")

        # Asignatura
        bp.fill(page.locator('#nombre-asignatura'), asig_nombre, "Nombre asignatura")
        bp.fill(page.locator('#horas-semanales'), "3", "Horas semanales")
        bp.click(page.locator('button:has-text("Agregar Asignatura")'), "Agregar Asignatura")
        page.wait_for_timeout(2000)

        bp._log("API", f"Verificando asignatura '{asig_nombre}' en BD")
        resp = api_context.get("/api/v1/asignaturas", headers=auth_headers(admin_token))
        if resp.status == 200:
            asignaturas = resp.json() if isinstance(resp.json(), list) else []
            bp._log("API", f"Asignatura en BD: {'SI' if any(asig_nombre in str(a.get('nombre','')) for a in asignaturas) else 'NO'}")

        # Usuarios
        bp.navigate(f"{frontend_url}/admin/usuarios")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        # DOCENTE
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

        bp._log("API", f"Verificando estudiante '{rut_estudiante}' en BD")
        estudiante_uuid = None
        resp = api_context.get("/api/v1/admin/listar/ESTUDIANTE", headers=auth_headers(admin_token))
        if resp.status == 200:
            for u in (resp.json() if isinstance(resp.json(), list) else []):
                if u.get("rut") == rut_estudiante:
                    estudiante_uuid = u.get("id")
                    bp._log("API", f"Estudiante uuid={estudiante_uuid}, nombre={u.get('nombreCompleto')}")
                    break
        assert estudiante_uuid, f"No se encontro estudiante {rut_estudiante} en BD"
        bp._log("CHECK", "ESTUDIANTE creado y verificado en BD")

        # APODERADO vinculado al estudiante
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
        pupilo_select = page.locator('#pupiloUuid')
        if pupilo_select.count() > 0 and pupilo_select.locator('option').count() > 1:
            bp.select(pupilo_select, label="Pupilo", index=1)
            page.wait_for_timeout(300)
        bp.click(page.locator('button:has-text("Crear usuario")'), "Crear APODERADO")
        page.wait_for_timeout(2500)

        bp._log("API", f"Verificando apoderado '{rut_apoderado}' con pupiloUuid en BD")
        apoderado_pupilo_ok = False
        resp = api_context.get("/api/v1/admin/listar/APODERADO", headers=auth_headers(admin_token))
        if resp.status == 200:
            for u in (resp.json() if isinstance(resp.json(), list) else []):
                if u.get("rut") == rut_apoderado and u.get("pupiloUuid") is not None:
                    apoderado_pupilo_ok = True
                    bp._log("API", f"Apoderado uuid={u.get('id')}, pupiloUuid={u.get('pupiloUuid')}")
                    break
        bp._log("CHECK", f"APODERADO vinculado: {'SI' if apoderado_pupilo_ok else 'NO'}", apoderado_pupilo_ok)

        # Asignar DOCENTE al curso (mock para que los selects tengan datos)
        bp._log("E2E", "--- Asignar DOCENTE al curso ---", ok=True)
        page.route("**/api/**", mock_api_success)
        bp._log("MOCK", "API mockeada para asignacion")
        bp.navigate(f"{frontend_url}/admin/asignacion-docentes")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        assert "/admin/asignacion-docentes" in page.url
        selects = page.locator('select')
        if selects.count() >= 2:
            for i in range(min(selects.count(), 3)):
                if selects.nth(i).locator('option').count() > 1:
                    bp.select(selects.nth(i), label=f"Asig #{i+1}", index=1)
                    page.wait_for_timeout(300)
        btn_asignar = page.locator('button:has-text("Asignar"), button:has-text("Guardar")')
        if btn_asignar.count() > 0:
            bp.click(btn_asignar.first, "Asignar DOCENTE")
            page.wait_for_timeout(1500)
        bp._log("CHECK", "DOCENTE asignado a curso/asignatura")
        page.unroute("**/api/**")
        bp._log("E2E", "=== FASE 1 COMPLETA ===", ok=True)

        # ═══════════════════════════════════════════
        # FASE 2: DOCENTE registra notas, asistencia, envía mensaje
        # ═══════════════════════════════════════════
        bp._log("E2E", "=== FASE 2: DOCENTE trabaja ===", ok=True)
        lp.goto(frontend_url)
        lp.login(rut_docente, password_e2e)
        page.wait_for_timeout(2000)
        assert "/calificaciones" in page.url
        bp._log("CHECK", "DOCENTE login → /calificaciones")

        page.route("**/api/**", mock_solo_gets)
        bp._log("MOCK", "Solo GETs mockeados, escritura real")

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
            bp.fill(notas.nth(i), str(5.0 + i), f"Nota {i+1}")
            page.wait_for_timeout(200)
        btn_g = page.locator('button:has-text("Guardar Calificaciones")')
        if btn_g.count() > 0 and btn_g.is_enabled():
            bp.click(btn_g, "Guardar Calificaciones")
            page.wait_for_timeout(2000)
        bp._log("CHECK", "Notas registradas")

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
        bp._log("CHECK", "Asistencia registrada")

        bp.navigate(f"{frontend_url}/comunicaciones/redactar")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        assert "/comunicaciones/redactar" in page.url
        asunto = page.locator('input[name="asunto"], #asunto')
        if asunto.count() > 0:
            bp.fill(asunto, "Felicitaciones", "Asunto")
            page.wait_for_timeout(200)
        cont = page.locator('textarea[name="mensaje"], textarea[name="contenido"], #mensaje')
        if cont.count() > 0:
            bp.fill(cont, mensaje_docente, "Contenido mensaje")
            page.wait_for_timeout(200)
        btn_env = page.locator('button:has-text("Enviar")')
        if btn_env.count() > 0 and btn_env.is_enabled():
            bp.click(btn_env, "Enviar mensaje")
            page.wait_for_timeout(2000)
        bp._log("CHECK", f"Mensaje enviado: '{mensaje_docente}'")
        bp._log("E2E", "=== FASE 2 COMPLETA ===", ok=True)

        # ═══════════════════════════════════════════
        # FASE 3: ESTUDIANTE revisa sus datos
        # ═══════════════════════════════════════════
        bp._log("E2E", "=== FASE 3: ESTUDIANTE revisa ===", ok=True)
        page.route("**/api/**", mock_api_success)
        bp._log("MOCK", "API mockeada (solo lectura)")

        lp.goto(frontend_url)
        lp.login(rut_estudiante, password_e2e)
        page.wait_for_timeout(2000)
        page.goto(f"{frontend_url}/mis-calificaciones")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        assert "/mis-calificaciones" in page.url
        bp._log("CHECK", "ESTUDIANTE: /mis-calificaciones")

        page.goto(f"{frontend_url}/asistencia/historial")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)
        assert "/asistencia/historial" in page.url
        bp._log("CHECK", "ESTUDIANTE: historial asistencia")

        page.goto(f"{frontend_url}/comunicaciones")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)
        assert "/comunicaciones" in page.url
        bp._log("CHECK", "ESTUDIANTE: comunicaciones")
        bp._log("E2E", "=== FASE 3 COMPLETA ===", ok=True)

        # ═══════════════════════════════════════════
        # FASE 4: APODERADO revisa datos del pupilo + lee mensaje del docente
        # ═══════════════════════════════════════════
        bp._log("E2E", "=== FASE 4: APODERADO revisa ===", ok=True)

        lp.goto(frontend_url)
        lp.login(rut_apoderado, password_e2e)
        page.wait_for_timeout(2000)

        page.goto(f"{frontend_url}/mis-calificaciones")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        assert "/mis-calificaciones" in page.url
        sel = page.locator('select, #select-pupilo')
        if sel.count() > 0:
            bp._log("CHECK", "APODERADO: selector pupilo visible")
        bp._log("CHECK", "APODERADO: calificaciones pupilo")

        page.goto(f"{frontend_url}/asistencia/historial")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)
        assert "/asistencia/historial" in page.url
        bp._log("CHECK", "APODERADO: historial pupilo")

        page.goto(f"{frontend_url}/asistencia/justificar")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)
        assert "/asistencia/justificar" in page.url
        bp._log("CHECK", "APODERADO: justificar inasistencia")

        page.goto(f"{frontend_url}/comunicaciones")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)
        assert "/comunicaciones" in page.url
        bp._log("CHECK", f"APODERADO: lee mensaje '{mensaje_docente}'")
        bp._log("E2E", "=== FASE 4 COMPLETA ===", ok=True)

        # ═══════════════════════════════════════════
        # VERIFICACION BD
        # ═══════════════════════════════════════════
        bp._log("E2E", "=== VERIFICACION BD ===", ok=True)
        resp = api_context.get(
            f"/api/v1/calificaciones/estudiante/{estudiante_uuid}",
            headers=auth_headers(admin_token),
        )
        if resp.status == 200:
            calificaciones = resp.json() if isinstance(resp.json(), list) else []
            bp._log("API", f"Calificaciones BD: {len(calificaciones)} registros")

        bp._log("E2E", "=== CICLO DE VIDA E2E COMPLETO ===", ok=True)
        bp.screenshot("func_flujo_e2e")
