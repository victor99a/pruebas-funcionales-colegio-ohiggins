import pytest
import json
from conftest import get_token_by_role, auth_headers


ENDPOINTS_ADMIN_DOCENTE = [
    # (method, path, body)
    ("GET", "/api/v1/cursos", None),
    ("POST", "/api/v1/cursos/crear", {
        "nombre": "1ro Basico Test",
        "anioEscolar": 2025,
    }),
    ("GET", "/api/v1/asignaturas", None),
    ("POST", "/api/v1/asignaturas/crear", {
        "nombre": "Matematicas Test",
        "horasSemanales": 4,
    }),
    ("GET", "/api/v1/matriculas", None),
    ("GET", "/api/v1/calificaciones/curso/1/asignatura/1", None),
]


ROLES_ADMIN_DOCENTE = [
    ("ADMIN", "not_forbidden"),
    ("DOCENTE", "not_forbidden"),
    ("APODERADO", 403),
    ("ESTUDIANTE", 403),
    ("SIN_TOKEN", 401),
]


class TestAdminDocente:

    @pytest.mark.admin_docente
    @pytest.mark.parametrize("method,path,body", ENDPOINTS_ADMIN_DOCENTE)
    @pytest.mark.parametrize("role_name,expected", ROLES_ADMIN_DOCENTE)
    def test_admin_docente_endpoints(
        self, api_context, setup_roles, request,
        method, path, body, role_name, expected
    ):
        token = get_token_by_role(request, role_name)
        headers = auth_headers(token)

        if body is not None:
            headers["Content-Type"] = "application/json"
            response = api_context.fetch(
                path, method=method, headers=headers,
                data=json.dumps(body),
            )
        else:
            response = api_context.fetch(
                path, method=method, headers=headers,
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

    @pytest.mark.admin_docente
    @pytest.mark.parametrize("role_name,expected", [
        ("ADMIN", "not_forbidden"),
        ("DOCENTE", "not_forbidden"),
        ("APODERADO", 403),
        ("ESTUDIANTE", 403),
        ("SIN_TOKEN", 401),
    ])
    def test_matricular_estudiante(
        self, api_context, setup_roles, request, role_name, expected
    ):
        token = get_token_by_role(request, role_name)
        estudiante_uuid = setup_roles.get("ESTUDIANTE", {}).get("uuid")
        if not estudiante_uuid:
            pytest.skip("No se pudo obtener UUID del estudiante de prueba")

        path = "/api/v1/matriculas/matricular"
        body = {"usuarioUuid": estudiante_uuid, "cursoId": 1}
        headers = {
            "Content-Type": "application/json",
            **auth_headers(token),
        }

        response = api_context.post(path, headers=headers, data=json.dumps(body))

        error_msg = (
            f"[{role_name}] POST {path}: "
            f"esperado {expected}, obtuvo {response.status} — "
            f"{response.text()[:200]}"
        )

        if expected == "not_forbidden":
            assert response.status not in (401, 403), error_msg
        else:
            assert response.status == expected, error_msg

    @pytest.mark.admin_docente
    @pytest.mark.parametrize("role_name,expected", [
        ("ADMIN", "not_forbidden"),
        ("DOCENTE", "not_forbidden"),
        ("APODERADO", 403),
        ("ESTUDIANTE", 403),
        ("SIN_TOKEN", 401),
    ])
    def test_guardar_calificacion(
        self, api_context, setup_roles, request, role_name, expected
    ):
        token = get_token_by_role(request, role_name)
        estudiante_uuid = setup_roles.get("ESTUDIANTE", {}).get("uuid")
        if not estudiante_uuid:
            pytest.skip("No se pudo obtener UUID del estudiante de prueba")

        path = "/api/v1/calificaciones/guardar"
        body = {
            "usuarioUuid": estudiante_uuid,
            "asignaturaId": 1,
            "nota1": 6.5,
            "nota2": 5.0,
            "nota3": 6.0,
        }
        headers = {
            "Content-Type": "application/json",
            **auth_headers(token),
        }

        response = api_context.put(path, headers=headers, data=json.dumps(body))

        error_msg = (
            f"[{role_name}] PUT {path}: "
            f"esperado {expected}, obtuvo {response.status} — "
            f"{response.text()[:200]}"
        )

        if expected == "not_forbidden":
            assert response.status not in (401, 403), error_msg
        else:
            assert response.status == expected, error_msg
