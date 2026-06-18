#!/bin/bash
# Ejecuta tests de navegador con navegador visible y graba video
# Uso: ./run-ui-tests.sh

export FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
export HEADED="${HEADED:-1}"
export SLOW_MO="${SLOW_MO:-500}"
export VIDEO_DIR="${VIDEO_DIR:-./videos}"

mkdir -p screenshots videos

source venv/bin/activate

echo "=================================================="
echo " Ejecutando tests UI con navegador visible"
echo " Frontend: $FRONTEND_URL"
echo " Video:    $VIDEO_DIR"
echo " SlowMo:   ${SLOW_MO}ms"
echo "=================================================="

python -m pytest specs/test_ui_login.py -v --tb=short

echo ""
echo "Videos guardados en: $VIDEO_DIR/"
echo "Screenshots en: screenshots/"
