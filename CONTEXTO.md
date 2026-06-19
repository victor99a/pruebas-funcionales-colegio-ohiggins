# Contexto Sesión 2 — Pruebas Funcionales

> Fecha: 2026-06-19 | 135 tests | E2E ciclo completo con 4 roles

## Repositorios

| Repo | URL | Rama |
|------|-----|------|
| Principal | https://github.com/yaquelin2305/colegio-bernardo-ohiggins-platform | `feat/backend-integration-complete` |
| Pruebas | https://github.com/victor99a/pruebas-funcionales-colegio-ohiggins | `main` |

## PRs pendientes

- #75 → develop: https://github.com/yaquelin2305/colegio-bernardo-ohiggins-platform/pull/75
- #76 → main: https://github.com/yaquelin2305/colegio-bernardo-ohiggins-platform/pull/76

## Cambios clave en proyecto principal

- ms-comunicaciones + ms-asistencia en `docker-compose.test.yml` (puertos 8081/8085)
- API Gateway: perfil `docker` con 16 rutas estáticas a contenedores
- SecurityConfigProd: activado para `{prod, docker}` (CSRF disabled, JWT + RBAC)
- ms-comunicaciones + ms-asistencia SecurityConfig: `permitAll()` (trust-the-gateway)
- axiosClient: solo borra token en 401 (no en 403)
- ProtectedRoute activo con verificación de roles
- LoginForm: redirige según rol post-login
- GestionUsuariosPage: catch separado save vs refresh, muestra error real del API
- FormularioUsuarioAdmin: handleSubmit async con await onGuardar()
- UsuarioMsDTO (BFF): agregado campo pupiloUuid

## Estructura de tests (135)

```
specs/
├── test_admin_docente.py (40)
├── test_admin_only.py (22)
├── test_asistencia_rbac.py (24)
├── test_boletin.py (6)
├── test_comunicaciones_rbac.py (15)
├── test_public_endpoints.py (8)
├── test_token_edge_cases.py (8)
├── test_ui_funcionalidad.py (2) — login validacion + E2E ciclo completo
└── test_ui_seguridad.py (4) — bloqueos y acceso denegado
```

## Tags pytest

```bash
pytest -m seguridad -v      # 4 tests
pytest -m funcionalidad -v  # 2 tests (login + E2E)
```

## Flujo E2E

```
FASE 1: ADMIN crea curso+asignatura+DOCENTE+ESTUDIANTE+APODERADO+asignación
FASE 2: DOCENTE registra notas/asistencia + envía mensaje "alumno estrella"
FASE 3: ESTUDIANTE revisa /mis-calificaciones, historial, comunicaciones
FASE 4: APODERADO revisa calificaciones pupilo, historial, justificar, mensaje
VERIFICACION BD: calificaciones guardadas
```

## Bugs conocidos

| # | Bug | Estado |
|---|-----|--------|
| 1 | GET /api/v1/asignacion-docente → 500 | Pendiente |
| 2 | POST /api/bff/comunicaciones/enviar → 500 | Pendiente |
| 3 | pupiloUuid faltaba en BD (ALTER TABLE aplicado) | Resuelto |

## Ejecución

```bash
cd /Users/vitoco/colegio-bernardo-ohiggins-platform
docker compose -f docker-compose.test.yml up --build -d

cd /Users/vitoco/pruebas-funcionales-colegio-ohiggins
source venv/bin/activate
HEADED=1 SLOW_MO=100 FRONTEND_URL=http://localhost:3000 pytest specs/ -v
```

## Credenciales

| Rol | RUT | Password |
|-----|-----|----------|
| ADMIN | 12345678-9 | Admin1234! |
| DOCENTE | 20000001-5 | Test1234! |
| APODERADO | 20000002-3 | Test1234! |
| ESTUDIANTE | 20000003-1 | Test1234! |

## Pendientes próxima sesión

- [ ] Arreglar GET /api/v1/asignacion-docente → 500
- [ ] Arreglar POST /api/bff/comunicaciones/enviar → 500
- [ ] Merge PRs #75 y #76
- [ ] Ejecución paralela pytest -n 4
