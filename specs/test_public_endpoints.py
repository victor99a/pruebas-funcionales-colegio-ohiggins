import pytest
from conftest import auth_headers


class TestPublicEndpoints:

    @pytest.mark.public
    @pytest.mark.parametrize("endpoint,method", [
        ("/api/v1/auth/health", "GET"),
        ("/actuator/health", "GET"),
        ("/health", "GET"),
    ])
    def test_public_endpoints_sin_token(self, api_context, endpoint, method):
        response = api_context.fetch(endpoint, method=method)
        assert response.status == 200, (
            f"{method} {endpoint} deberia ser publico, "
            f"obtuvo {response.status}: {response.text()}"
        )

    @pytest.mark.public
    @pytest.mark.parametrize("endpoint,method", [
        ("/api/v1/auth/health", "GET"),
        ("/actuator/health", "GET"),
        ("/health", "GET"),
    ])
    def test_public_endpoints_con_token(
        self, api_context, admin_token, endpoint, method
    ):
        response = api_context.fetch(
            endpoint,
            method=method,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status == 200, (
            f"{method} {endpoint} con token deberia ser accesible, "
            f"obtuvo {response.status}: {response.text()}"
        )

    @pytest.mark.public
    def test_login_devuelve_token(self, api_context):
        response = api_context.post(
            "/api/v1/auth/login",
            headers={"Content-Type": "application/json"},
            data='{"rut":"12345678-9","password":"Admin1234!"}',
        )
        assert response.status == 200
        body = response.json()
        assert "token" in body

    @pytest.mark.public
    def test_login_credenciales_invalidas(self, api_context):
        response = api_context.post(
            "/api/v1/auth/login",
            headers={"Content-Type": "application/json"},
            data='{"rut":"99999999-9","password":"WrongPass1!"}',
        )
        assert response.status in (401, 403)
