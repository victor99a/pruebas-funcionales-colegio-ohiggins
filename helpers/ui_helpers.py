import time
from playwright.sync_api import Page

CREDENCIALES = {
    "ADMIN":     {"rut": "12345678-9", "password": "Admin1234!"},
    "DOCENTE":   {"rut": "20000001-5", "password": "Test1234!"},
    "APODERADO": {"rut": "20000002-3", "password": "Test1234!"},
    "ESTUDIANTE": {"rut": "20000003-1", "password": "Test1234!"},
}

SIDEBAR_VISIBLE = {
    "ADMIN":     ["Dashboard", "Usuarios", "Comunicaciones", "Historial"],
    "DOCENTE":   ["Comunicaciones", "Calificaciones"],
    "APODERADO": ["Mis Calificaciones", "Historial", "Justificar", "Comunicaciones"],
    "ESTUDIANTE": ["Mis Calificaciones", "Historial", "Comunicaciones"],
}

SIDEBAR_OCULTO = {
    "ADMIN":     [],
    "DOCENTE":   ["Usuarios", "Asig. Docentes"],
    "APODERADO": ["Dashboard", "Usuarios", "Asig. Docentes"],
    "ESTUDIANTE": ["Dashboard", "Usuarios", "Asig. Docentes", "Justificar"],
}

PAGINA_INICIAL = {
    "ADMIN":     "/dashboard",
    "DOCENTE":   "/calificaciones",
    "APODERADO": "/mis-calificaciones",
    "ESTUDIANTE": "/mis-calificaciones",
}

_ts = int(time.time()) % 100000


def rut_unico(rol="test"):
    base = {"ADMIN": 10, "DOCENTE": 20, "APODERADO": 30, "ESTUDIANTE": 40}.get(rol, 99)
    return f"{base}{_ts:05d}-k"


def email_unico(rol="test"):
    return f"{rol.lower()}.{_ts}@test-funcional.cl"


def _log(accion, detalle, ok=True):
    icono = "OK" if ok else "ERROR"
    check = "  ✅" if ok else "  ❌"
    print(f"[{icono}]{check} {accion}: {detalle}")


def injectar_token(page, rut, password, api_base="http://localhost:8080"):
    _log("TOKEN", f"Inyectando token para RUT {rut}")
    token = page.evaluate("""
        async ({rut, password, apiUrl}) => {
            const resp = await fetch(apiUrl + '/api/v1/auth/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({rut, password})
            });
            const data = await resp.json();
            const token = data.accessToken || data.token;
            localStorage.setItem('token', token);
            return token;
        }
    """, {"rut": rut, "password": password, "apiUrl": api_base})
    if token:
        _log("TOKEN", f"Token obtenido ({len(token)} chars)")
    else:
        _log("TOKEN", "Token NO obtenido", ok=False)
    return token


def mock_api_success(route):
    url = route.request.url
    if "dashboard" in url:
        body = '{"totalEstudiantes":0,"totalDocentes":0,"totalCursos":0,"totalAsignaturas":0}'
    elif "listar" in url or "bandeja" in url or "curso" in url or "estudiante" in url:
        body = "[]"
    elif "boletin" in url:
        body = '{"nombreCompleto":"Test","curso":"1ro Basico","promedioGeneral":6.0,"porcentajeAsistencia":95,"calificaciones":[]}'
    else:
        body = "{}"
    route.fulfill(status=200, content_type="application/json", body=body)


def login_y_navegar(page, frontend_url, rol, pagina_destino):
    _log("LOGIN", f"Iniciando como {rol} → {pagina_destino}")
    creds = CREDENCIALES[rol]
    if rol == "ADMIN":
        from pages.login_page import LoginPage
        lp = LoginPage(page)
        lp.goto(frontend_url)
        lp.login(creds["rut"], creds["password"])
        page.wait_for_timeout(2000)
    else:
        page.goto(f"{frontend_url}/login")
        page.wait_for_load_state("networkidle")
        injectar_token(page, creds["rut"], creds["password"])
        _log("MOCK", "API interceptada para rol no-ADMIN")
        page.route("**/api/**", mock_api_success)

    _log("NAV", pagina_destino)
    page.goto(f"{frontend_url}{pagina_destino}")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    _log("READY", f"Página cargada: {page.url}")
    return page


def login_y_navegar_sin_mock(page, frontend_url, rol, pagina_destino):
    _log("LOGIN", f"Iniciando como {rol} (sin mock) → {pagina_destino}")
    creds = CREDENCIALES[rol]
    page.goto(f"{frontend_url}/login")
    page.wait_for_load_state("networkidle")
    injectar_token(page, creds["rut"], creds["password"])

    _log("NAV", pagina_destino)
    page.goto(f"{frontend_url}{pagina_destino}")
    page.wait_for_timeout(3000)
    _log("READY", f"Página cargada: {page.url}")
    return page


def mock_solo_gets(route):
    """Mockea solo GETs, deja pasar POST/PUT/PATCH al API real"""
    if route.request.method == "GET":
        mock_api_success(route)
    else:
        route.continue_()
