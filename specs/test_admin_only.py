import pytest
from conftest import get_token_by_role, auth_headers


ENDPOINTS_ADMIN_ONLY = [
    # (method, path, body)
    ("GET", "/api/v1/admin/listar/DOCENTE", None),
    ("POST", "/api/v1/admin/crear", {
        "rut": "18000001-k",
        "email": "temp.admin.test@colegio-ohiggins.cl",
        "password": "Temp1234!",
        "nombre": "Temp",
        "apellido": "AdminTest",
        "rol": "ESTUDIANTE",
    }),
    ("POST", "/api/v1/asignacion-docente", {
        "docenteUuid": "00000000-0000-0000-0000-000000000001",
        "cursoId": 1,
        "asignaturaId": 1,
    }),
    ("GET", "/api/bff/dashboard/stats", None),
]

ROLES = [
    ("ADMIN", "not_forbidden"),
    ("DOCENTE", 403),
    ("APODERADO", 403),
    ("ESTUDIANTE", 403),
    ("SIN_TOKEN", 401),
]


class TestAdminOnly:

    @pytest.mark.admin_only
    @pytest.mark.parametrize("method,path,body", ENDPOINTS_ADMIN_ONLY)
    @pytest.mark.parametrize("role_name,expected", ROLES)
    def test_admin_only_endpoints(
        self, api_context, setup_roles, request,
        method, path, body, role_name, expected
    ):
        import json

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

    @pytest.mark.admin_only
    def test_admin_get_by_id(self, api_context, admin_token, setup_roles):
        docente_uuid = setup_roles["DOCENTE"]["uuid"]
        if not docente_uuid:
            pytest.skip("No se pudo obtener UUID del docente de prueba")

        response = api_context.get(
            f"/api/v1/admin/{docente_uuid}",
            headers=auth_headers(admin_token),
        )
        assert response.status not in (401, 403), (
            f"ADMIN deberia poder ver usuario {docente_uuid}: "
            f"obtuvo {response.status}"
        )

    @pytest.mark.admin_only
    def test_admin_actualizar(self, api_context, admin_token, setup_roles):
        docente_uuid = setup_roles["DOCENTE"]["uuid"]
        if not docente_uuid:
            pytest.skip("No se pudo obtener UUID del docente de prueba")

        import json
        response = api_context.put(
            f"/api/v1/admin/actualizar/{docente_uuid}",
            headers={
                "Content-Type": "application/json",
                **auth_headers(admin_token),
            },
            data=json.dumps({"nombre": "Docente", "apellido": "Actualizado"}),
        )
        assert response.status not in (401, 403), (
            f"ADMIN deberia poder actualizar usuario {docente_uuid}: "
            f"obtuvo {response.status}"
        )
