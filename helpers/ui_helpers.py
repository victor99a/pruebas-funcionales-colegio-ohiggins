import time
import pytest
from playwright.sync_api import Page

CREDENCIALES = {
    "ADMIN":     {"rut": "12345678-9", "password": "Admin1234!"},
    "DOCENTE":   {"rut": "20000001-5", "password": "Test1234!"},
    "APODERADO": {"rut": "20000002-3", "password": "Test1234!"},
    "ESTUDIANTE": {"rut": "20000003-1", "password": "Test1234!"},
}

_ts = int(time.time()) % 100000


def rut_unico(rol="test"):
    base = {"ADMIN": 10, "DOCENTE": 20, "APODERADO": 30, "ESTUDIANTE": 40}.get(rol, 99)
    return f"{base}{_ts:05d}-k"


def email_unico(rol="test"):
    return f"{rol.lower()}.{_ts}@test-funcional.cl"


def injectar_token(page, rut, password, api_base="http://localhost:8080"):
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
    creds = CREDENCIALES[rol]
    if rol == "ADMIN":
        from pages.login_page import LoginPage
        login_page = LoginPage(page)
        login_page.goto(frontend_url)
        login_page.login(creds["rut"], creds["password"])
        page.wait_for_timeout(2000)
    else:
        page.goto(f"{frontend_url}/login")
        page.wait_for_load_state("networkidle")
        injectar_token(page, creds["rut"], creds["password"])
        page.route("**/api/**", mock_api_success)

    page.goto(f"{frontend_url}{pagina_destino}")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    return page


def login_y_navegar_sin_mock(page, frontend_url, rol, pagina_destino):
    creds = CREDENCIALES[rol]
    page.goto(f"{frontend_url}/login")
    page.wait_for_load_state("networkidle")
    injectar_token(page, creds["rut"], creds["password"])

    page.goto(f"{frontend_url}{pagina_destino}")
    page.wait_for_timeout(3000)
    return page
