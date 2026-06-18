import pytest
from conftest import get_token_by_role, auth_headers


class TestBoletin:

    @pytest.mark.boletin
    @pytest.mark.parametrize("role_name,expected", [
        ("ADMIN", "not_forbidden"),
        ("DOCENTE", "not_forbidden"),
        ("APODERADO", "not_forbidden"),
    ])
    def test_boletin_admin_docente_apoderado(
        self, api_context, setup_roles, estudiante_uuid,
        request, role_name, expected
    ):
        token = get_token_by_role(request, role_name)
        path = f"/api/bff/boletin/{estudiante_uuid}"

        response = api_context.get(path, headers=auth_headers(token))

        error_msg = (
            f"[{role_name}] GET {path}: "
            f"esperado {expected}, obtuvo {response.status}"
        )

        assert response.status not in (401, 403), error_msg

    @pytest.mark.boletin
    def test_estudiante_ve_su_propio_boletin(
        self, api_context, estudiante_token, estudiante_uuid
    ):
        path = f"/api/bff/boletin/{estudiante_uuid}"
        response = api_context.get(path, headers=auth_headers(estudiante_token))

        error_msg = (
            f"ESTUDIANTE deberia ver su propio boletin {estudiante_uuid}: "
            f"obtuvo {response.status}"
        )
        assert response.status not in (401, 403), error_msg

    @pytest.mark.boletin
    def test_estudiante_no_puede_ver_boletin_ajeno(
        self, api_context, estudiante_token, setup_roles
    ):
        otro_uuid = setup_roles.get("DOCENTE", {}).get("uuid", "00000000-0000-0000-0000-000000000099")
        path = f"/api/bff/boletin/{otro_uuid}"

        response = api_context.get(path, headers=auth_headers(estudiante_token))

        error_msg = (
            f"ESTUDIANTE NO deberia ver boletin de otro ({otro_uuid}): "
            f"obtuvo {response.status}"
        )
        assert response.status == 403, error_msg

    @pytest.mark.boletin
    def test_boletin_sin_token(self, api_context, estudiante_uuid):
        path = f"/api/bff/boletin/{estudiante_uuid}"
        response = api_context.get(path)

        assert response.status == 401, (
            f"GET {path} sin token deberia devolver 401, "
            f"obtuvo {response.status}"
        )
