import pytest
import json
from conftest import get_token_by_role, auth_headers


COMUNICACIONES_READ_ENDPOINTS = [
    ("GET", "/api/bff/comunicaciones/destinatarios"),
]

COMUNICACIONES_WRITE_ENDPOINTS = [
    ("POST", "/api/bff/comunicaciones/enviar", {
        "destinatarioId": "00000000-0000-0000-0000-000000000001",
        "asunto": "Prueba RBAC",
        "contenido": "Mensaje de prueba de permisos",
    }),
]


class TestComunicacionesRBAC:

    @pytest.mark.comunicaciones
    @pytest.mark.parametrize("method,path", COMUNICACIONES_READ_ENDPOINTS)
    @pytest.mark.parametrize("role_name,expected", [
        ("ADMIN", "not_forbidden"),
        ("DOCENTE", "not_forbidden"),
        ("APODERADO", "not_forbidden"),
        ("ESTUDIANTE", "not_forbidden"),
        ("SIN_TOKEN", 401),
    ])
    def test_comunicaciones_lectura_todos_autenticados(
        self, api_context, setup_roles, request,
        method, path, role_name, expected
    ):
        token = get_token_by_role(request, role_name)
        response = api_context.fetch(
            path, method=method, headers=auth_headers(token),
        )

        error_msg = (
            f"[{role_name}] {method} {path}: "
            f"esperado {expected}, obtuvo {response.status} — "
            f"{response.text()[:200]}"
        )

        if expected == "not_forbidden":
            assert response.status not in (401, 403), error_msg
        else:
            assert response.status == expected, error_msg

    @pytest.mark.comunicaciones
    @pytest.mark.parametrize("method,path,body", COMUNICACIONES_WRITE_ENDPOINTS)
    @pytest.mark.parametrize("role_name,expected", [
        ("ADMIN", "not_forbidden"),
        ("DOCENTE", "not_forbidden"),
        ("APODERADO", 403),
        ("ESTUDIANTE", 403),
        ("SIN_TOKEN", 401),
    ])
    def test_comunicaciones_escritura_solo_admin_docente(
        self, api_context, setup_roles, request,
        method, path, body, role_name, expected
    ):
        token = get_token_by_role(request, role_name)
        headers = {
            "Content-Type": "application/json",
            **auth_headers(token),
        }

        response = api_context.fetch(
            path, method=method, headers=headers,
            data=json.dumps(body),
        )

        error_msg = (
            f"[{role_name}] {method} {path}: "
            f"esperado {expected}, obtuvo {response.status} — "
            f"{response.text()[:200]}"
        )

        if expected == "not_forbidden":
            assert response.status not in (401, 403), error_msg
        else:
            assert response.status == expected, error_msg

    @pytest.mark.comunicaciones
    @pytest.mark.parametrize("role_name,expected", [
        ("ADMIN", "not_forbidden"),
        ("DOCENTE", "not_forbidden"),
        ("APODERADO", "not_forbidden"),
        ("ESTUDIANTE", "not_forbidden"),
        ("SIN_TOKEN", 401),
    ])
    def test_comunicaciones_bandeja(
        self, api_context, setup_roles, request,
        role_name, expected
    ):
        token = get_token_by_role(request, role_name)
        usuario_uuid = setup_roles.get(role_name, {}).get("uuid", "unknown")
        path = f"/api/bff/comunicaciones/bandeja/{usuario_uuid}"

        response = api_context.get(path, headers=auth_headers(token))

        error_msg = (
            f"[{role_name}] GET {path}: "
            f"esperado {expected}, obtuvo {response.status}"
        )

        if expected == "not_forbidden":
            assert response.status not in (401, 403), error_msg
        else:
            assert response.status == expected, error_msg
