import os
import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def base_url():
    return os.environ.get("BASE_URL", "http://localhost:8080")


@pytest.fixture(scope="session")
def frontend_url():
    return os.environ.get("FRONTEND_URL", "http://localhost:3000")


@pytest.fixture(scope="session")
def api_context(base_url):
    with sync_playwright() as pw:
        context = pw.request.new_context(base_url=base_url)
        yield context
        context.dispose()


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright_instance):
    headless = os.environ.get("HEADED", "0") != "1"
    browser = playwright_instance.chromium.launch(
        headless=headless,
        slow_mo=int(os.environ.get("SLOW_MO", "0")),
    )
    yield browser
    browser.close()


@pytest.fixture
def browser_context(browser):
    video_dir = os.environ.get("VIDEO_DIR")
    context_kwargs = {}
    if video_dir:
        context_kwargs["record_video_dir"] = video_dir
        context_kwargs["record_video_size"] = {"width": 1280, "height": 720}
    context = browser.new_context(**context_kwargs)
    yield context
    context.close()


@pytest.fixture
def page(browser_context):
    page = browser_context.new_page()
    yield page
    page.close()


@pytest.fixture(scope="session")
def admin_token(api_context, base_url):
    from helpers.token_manager import TokenManager
    token_mgr = TokenManager(api_context, base_url)
    return token_mgr.get_admin_token()


@pytest.fixture(scope="session")
def setup_roles(api_context, base_url, admin_token):
    from helpers.user_setup import TestUserSetup
    user_setup = TestUserSetup(api_context, base_url, admin_token)
    return user_setup.ensure_users_exist()


@pytest.fixture(scope="session")
def docente_token(api_context, base_url, setup_roles):
    from helpers.token_manager import TokenManager
    token_mgr = TokenManager(api_context, base_url)
    docente = setup_roles["DOCENTE"]
    return token_mgr.get_token(docente["rut"], docente["password"])


@pytest.fixture(scope="session")
def apoderado_token(api_context, base_url, setup_roles):
    from helpers.token_manager import TokenManager
    token_mgr = TokenManager(api_context, base_url)
    apoderado = setup_roles["APODERADO"]
    return token_mgr.get_token(apoderado["rut"], apoderado["password"])


@pytest.fixture(scope="session")
def estudiante_token(api_context, base_url, setup_roles):
    from helpers.token_manager import TokenManager
    token_mgr = TokenManager(api_context, base_url)
    estudiante = setup_roles["ESTUDIANTE"]
    return token_mgr.get_token(estudiante["rut"], estudiante["password"])


@pytest.fixture(scope="session")
def estudiante_uuid(setup_roles):
    return setup_roles["ESTUDIANTE"]["uuid"]


def get_token_by_role(request, role_name):
    if role_name == "SIN_TOKEN":
        return None
    fixture_map = {
        "ADMIN": "admin_token",
        "DOCENTE": "docente_token",
        "APODERADO": "apoderado_token",
        "ESTUDIANTE": "estudiante_token",
    }
    fixture_name = fixture_map.get(role_name)
    if fixture_name is None:
        return None
    return request.getfixturevalue(fixture_name)


def auth_headers(token):
    if token is None:
        return {}
    return {"Authorization": f"Bearer {token}"}
