import pytest
from conftest import auth_headers


class TestTokenEdgeCases:

    @pytest.mark.edge_cases
    @pytest.mark.parametrize("endpoint,method", [
        ("/api/v1/admin/listar/DOCENTE", "GET"),
        ("/api/v1/cursos", "GET"),
        ("/api/bff/dashboard/stats", "GET"),
        ("/api/bff/boletin/00000000-0000-0000-0000-000000000001", "GET"),
    ])
    def test_sin_token_devuelve_401(self, api_context, endpoint, method):
        response = api_context.fetch(endpoint, method=method)
        assert response.status == 401, (
            f"{method} {endpoint} sin token deberia devolver 401, "
            f"obtuvo {response.status}"
        )

    @pytest.mark.edge_cases
    def test_token_invalido_devuelve_401(self, api_context):
        response = api_context.get(
            "/api/v1/cursos",
            headers={"Authorization": "Bearer token_invalido_12345"},
        )
        assert response.status == 401, (
            f"Token invalido deberia devolver 401, obtuvo {response.status}"
        )

    @pytest.mark.edge_cases
    def test_token_sin_role_claim_devuelve_401(self, api_context):
        token_sin_role = (
            "eyJhbGciOiJIUzI1NiJ9."
            "eyJzdWIiOiIxMjM0NTY3OC05IiwidXNlcklkIjoiMDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAxIn0."
            "firma_invalida"
        )
        response = api_context.get(
            "/api/v1/cursos",
            headers={"Authorization": f"Bearer {token_sin_role}"},
        )
        assert response.status == 401, (
            f"Token sin claim 'role' deberia devolver 401, "
            f"obtuvo {response.status}"
        )

    @pytest.mark.edge_cases
    def test_header_basic_en_vez_de_bearer_devuelve_401(self, api_context):
        response = api_context.get(
            "/api/v1/cursos",
            headers={"Authorization": "Basic dXNlcjpwYXNz"},
        )
        assert response.status == 401, (
            f"Header 'Basic' en vez de 'Bearer' deberia devolver 401, "
            f"obtuvo {response.status}"
        )

    @pytest.mark.edge_cases
    def test_token_expirado_devuelve_401(self, api_context):
        token_expirado = (
            "eyJhbGciOiJIUzI1NiJ9."
            "eyJzdWIiOiIxMjM0NTY3OC05Iiwicm9sZSI6IkFETUlOIiwidXNlcklkIjoiMDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAxIiwiZXhwIjoxNzAwMDAwMDAwfQ."
            "ZmFrZVNpZ25hdHVyZQ"
        )
        response = api_context.get(
            "/api/v1/cursos",
            headers={"Authorization": f"Bearer {token_expirado}"},
        )
        assert response.status == 401, (
            f"Token expirado deberia devolver 401, obtuvo {response.status}"
        )
