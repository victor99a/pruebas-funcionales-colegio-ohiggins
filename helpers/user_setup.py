import json
import logging
import uuid

logger = logging.getLogger(__name__)


class TestUserSetup:

    TEST_USERS = {
        "DOCENTE": {
            "rut": "20000001-5",
            "password": "Test1234!",
            "email": "docente.prueba@colegio-ohiggins.cl",
            "nombre": "Docente",
            "apellido": "Prueba",
            "rol": "DOCENTE",
        },
        "APODERADO": {
            "rut": "20000002-3",
            "password": "Test1234!",
            "email": "apoderado.prueba@colegio-ohiggins.cl",
            "nombre": "Apoderado",
            "apellido": "Prueba",
            "rol": "APODERADO",
        },
        "ESTUDIANTE": {
            "rut": "20000003-1",
            "password": "Test1234!",
            "email": "estudiante.prueba@colegio-ohiggins.cl",
            "nombre": "Estudiante",
            "apellido": "Prueba",
            "rol": "ESTUDIANTE",
        },
    }

    def __init__(self, api_context, base_url, admin_token):
        self.api_context = api_context
        self.base_url = base_url
        self.admin_token = admin_token
        self._users = {}

    def ensure_users_exist(self):
        if self._users:
            return self._users

        for role, user_data in self.TEST_USERS.items():
            user_info = self._try_create_or_retrieve(role, user_data)
            self._users[role] = user_info

        logger.info("Users ready: %s",
                     {r: u["rut"] for r, u in self._users.items()})
        return self._users

    def _try_create_or_retrieve(self, role, user_data):
        existing = self._find_existing_by_rut(user_data["rut"])
        if existing:
            logger.info("User %s (%s) already exists: %s",
                        role, user_data["rut"], existing.get("id"))
            return {
                "rut": user_data["rut"],
                "password": user_data["password"],
                "uuid": existing.get("id"),
                "email": user_data["email"],
            }

        return self._create_user(role, user_data)

    def _find_existing_by_rut(self, rut):
        response = self.api_context.get(
            f"/api/v1/admin/buscar/rut/{rut}",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        if response.status == 200:
            body = response.json()
            if body and body.get("id"):
                return body
        return None

    def _create_user(self, role, user_data):
        response = self.api_context.post(
            "/api/v1/admin/crear",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.admin_token}",
            },
            data=json.dumps({
                "rut": user_data["rut"],
                "email": user_data["email"],
                "password": user_data["password"],
                "nombre": user_data["nombre"],
                "apellido": user_data["apellido"],
                "rol": user_data["rol"],
            }),
        )

        if response.status not in (200, 201):
            logger.error(
                "Failed to create %s user: %s — %s",
                role, response.status, response.text()
            )

        body = response.json() if response.text else {}
        user_uuid = body.get("id") or body.get("uuid") or body.get("userId")

        logger.info("Created %s user: rut=%s uuid=%s",
                    role, user_data["rut"], user_uuid)

        return {
            "rut": user_data["rut"],
            "password": user_data["password"],
            "uuid": user_uuid,
            "email": user_data["email"],
        }
