import json
import logging

logger = logging.getLogger(__name__)


class TokenManager:

    ADMIN_RUT = "12345678-9"
    ADMIN_PASSWORD = "Admin1234!"

    def __init__(self, api_context, base_url):
        self.api_context = api_context
        self.base_url = base_url
        self._cache = {}

    def get_admin_token(self):
        if "ADMIN" in self._cache:
            return self._cache["ADMIN"]
        token = self.get_token(self.ADMIN_RUT, self.ADMIN_PASSWORD)
        self._cache["ADMIN"] = token
        return token

    def get_token(self, rut, password):
        cache_key = f"{rut}:{password}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        response = self.api_context.post(
            "/api/v1/auth/login",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"rut": rut, "password": password}),
        )

        if response.status != 200:
            logger.error(
                "Login failed for RUT %s: %s — %s",
                rut, response.status, response.text()
            )
            raise RuntimeError(
                f"No se pudo autenticar como {rut}: HTTP {response.status}"
            )

        body = response.json()
        token = body.get("accessToken") or body.get("token")
        if not token:
            raise RuntimeError(f"Login response sin token para RUT {rut}: {body}")

        self._cache[cache_key] = token
        return token

    def decode_payload(self, token):
        parts = token.split(".")
        if len(parts) < 2:
            raise ValueError("Token JWT malformado")
        import base64
        padding = 4 - len(parts[1]) % 4
        if padding != 4:
            parts[1] += "=" * padding
        return json.loads(base64.urlsafe_b64decode(parts[1]))
