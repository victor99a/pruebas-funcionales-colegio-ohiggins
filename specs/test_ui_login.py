import pytest
from pages.login_page import LoginPage, DashboardPage


CREDENCIALES = {
    "ADMIN":     {"rut": "12345678-9", "password": "Admin1234!"},
    "DOCENTE":   {"rut": "20000001-5", "password": "Test1234!"},
    "APODERADO": {"rut": "20000002-3", "password": "Test1234!"},
    "ESTUDIANTE": {"rut": "20000003-1", "password": "Test1234!"},
}

SIDEBAR_VISIBLE = {
    "ADMIN":     ["Dashboard", "Gestión Académica", "Usuarios", "Comunicaciones"],
    "DOCENTE":   ["Toma Asistencia", "Historial", "Comunicaciones"],
    "APODERADO": ["Mis Calificaciones", "Historial", "Justificar", "Comunicaciones"],
    "ESTUDIANTE": ["Mis Calificaciones", "Historial", "Comunicaciones"],
}

SIDEBAR_OCULTO = {
    "ADMIN":     [],
    "DOCENTE":   ["Gestión Académica", "Usuarios", "Asig. Docentes", "Justificar"],
    "APODERADO": ["Dashboard", "Gestión Académica", "Usuarios", "Asig. Docentes"],
    "ESTUDIANTE": ["Dashboard", "Gestión Académica", "Usuarios", "Asig. Docentes", "Justificar"],
}

PAGINA_INICIAL_POR_ROL = {
    "ADMIN":     "/dashboard",
    "DOCENTE":   "/calificaciones",
    "APODERADO": "/mis-calificaciones",
    "ESTUDIANTE": "/mis-calificaciones",
}


def _injectar_token(page, rut, password, base_url):
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
    """, {"rut": rut, "password": password, "apiUrl": base_url})
    return token


class TestUILogin:

    @pytest.mark.parametrize("rol", ["ADMIN", "DOCENTE", "APODERADO", "ESTUDIANTE"])
    def test_login_y_acceso_pagina_inicial(self, page, frontend_url, rol):
        creds = CREDENCIALES[rol]
        pagina = PAGINA_INICIAL_POR_ROL[rol]

        if rol == "ADMIN":
            login_page = LoginPage(page)
            login_page.goto(frontend_url)
            login_page.login(creds["rut"], creds["password"])
            page.wait_for_timeout(2000)
        else:
            page.goto(f"{frontend_url}/login")
            page.wait_for_load_state("networkidle")
            _injectar_token(page, creds["rut"], creds["password"], "http://localhost:8080")
            page.route("**/api/**", self._api_mock_success)

        page.goto(f"{frontend_url}{pagina}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        assert pagina in page.url, (
            f"{rol}: no pudo acceder a {pagina}. URL actual: {page.url}"
        )

    @pytest.mark.parametrize("rol", ["ADMIN", "DOCENTE", "APODERADO", "ESTUDIANTE"])
    def test_sidebar_muestra_links_correctos(self, page, frontend_url, rol):
        creds = CREDENCIALES[rol]
        pagina = PAGINA_INICIAL_POR_ROL[rol]

        if rol == "ADMIN":
            login_page = LoginPage(page)
            login_page.goto(frontend_url)
            login_page.login(creds["rut"], creds["password"])
            page.wait_for_timeout(2000)
        else:
            page.goto(f"{frontend_url}/login")
            page.wait_for_load_state("networkidle")
            _injectar_token(page, creds["rut"], creds["password"], "http://localhost:8080")
            page.route("**/api/**", self._api_mock_success)

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        page.goto(f"{frontend_url}{pagina}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        dashboard = DashboardPage(page)

        visible = SIDEBAR_VISIBLE.get(rol, [])
        for link_label in visible:
            assert dashboard.sidebar_has_link(link_label), (
                f"[{rol}] Link '{link_label}' debe estar visible. "
                f"Links: {dashboard.get_sidebar_link_texts()}"
            )

        hidden = SIDEBAR_OCULTO.get(rol, [])
        for link_label in hidden:
            assert dashboard.sidebar_lacks_link(link_label), (
                f"[{rol}] Link '{link_label}' NO debe aparecer. "
                f"Links: {dashboard.get_sidebar_link_texts()}"
            )

        page.screenshot(path=f"screenshots/sidebar-{rol.lower()}.png")

    def _api_mock_success(self, route):
        url = route.request.url
        if "dashboard" in url:
            body = '{"totalEstudiantes":0,"totalDocentes":0,"totalCursos":0,"totalAsignaturas":0}'
        else:
            body = "[]"
        route.fulfill(status=200, content_type="application/json", body=body)

    def test_login_rut_vacio(self, page, frontend_url):
        login_page = LoginPage(page)
        login_page.goto(frontend_url)
        login_page.fill_password("Admin1234!")
        login_page.click_login()
        page.wait_for_timeout(300)
        assert login_page.is_on_login_page()

    def test_login_password_vacio(self, page, frontend_url):
        login_page = LoginPage(page)
        login_page.goto(frontend_url)
        login_page.fill_rut("12345678-9")
        login_page.click_login()
        page.wait_for_timeout(300)
        assert login_page.is_on_login_page()

    def test_login_credenciales_invalidas(self, page, frontend_url):
        login_page = LoginPage(page)
        login_page.goto(frontend_url)
        login_page.login("99999999-9", "WrongPass1!")
        page.wait_for_timeout(1000)
        assert login_page.is_on_login_page()
