# Pruebas Funcionales — API Gateway RBAC

Pruebas funcionales del API Gateway de la plataforma Colegio Bernardo O'Higgins usando **Playwright + Python + pytest**.

Verifica que el `JwtValidationFilter` del Gateway aplique correctamente las reglas RBAC por rol: ADMIN, DOCENTE, APODERADO, ESTUDIANTE.

## Requisitos

- Python 3.9+
- Docker (para levantar el stack de test)
- `docker compose -f docker-compose.test.yml up --build -d` (desde el repo principal)

## Instalación

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Ejecución

```bash
# Todos los tests
pytest -v

# Con reporte HTML
pytest -v --html=report.html --self-contained-html

# Paralelo (4 workers)
pytest -v -n 4
```

## Estructura

```
├── conftest.py              # Fixtures: tokens por rol, API context, setup de usuarios
├── helpers/
│   ├── token_manager.py     # Login y cache de JWT por rol
│   └── user_setup.py        # Creación de usuarios de prueba (DOCENTE, APODERADO, ESTUDIANTE)
└── specs/
    ├── test_public_endpoints.py        # Rutas públicas (sin token)
    ├── test_admin_only.py              # Solo ADMIN
    ├── test_admin_docente.py           # ADMIN + DOCENTE
    ├── test_boletin.py                 # Boletín (self-check ESTUDIANTE)
    ├── test_asistencia_rbac.py         # Asistencia (lectura/escritura)
    ├── test_comunicaciones_rbac.py     # Comunicaciones (lectura/escritura)
    └── test_token_edge_cases.py        # Tokens inválidos, expirados, malformados
```

## Matriz RBAC

| Rol | admin/** | cursos/** | boletin/{uuid} | asistencia GET | asistencia POST |
|-----|---------|-----------|----------------|----------------|-----------------|
| ADMIN | ✅ | ✅ | ✅ | ✅ | ✅ |
| DOCENTE | ❌ 403 | ✅ | ✅ | ✅ | ✅ |
| APODERADO | ❌ 403 | ❌ 403 | ✅ | ✅ | ❌ 403 |
| ESTUDIANTE | ❌ 403 | ❌ 403 | ✅ (solo propio) | ✅ | ❌ 403 |
| Sin token | ❌ 401 | ❌ 401 | ❌ 401 | ❌ 401 | ❌ 401 |
