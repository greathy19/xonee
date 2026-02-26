#!/bin/bash
# =============================================================================
#  XUI.one - Instalador unificado
#  Repositorio: https://github.com/greathy19/xonee
#
#  OS soportados (x86_64):
#    Ubuntu  : 20.04 / 22.04 / 24.04
#    Debian  : 11 (Bullseye) / 12 (Bookworm) / 13 (Trixie)
#
#  Instalar con:
#    sudo wget https://raw.githubusercontent.com/greathy19/xonee/main/install.sh \
#         -O /root/install.sh && sudo bash /root/install.sh
# =============================================================================

REPO_RAW="https://raw.githubusercontent.com/greathy19/xonee/main"
XUI_ZIP_URL="https://github.com/amidevous/xui.one/releases/download/test/XUI_1.5.13.zip"

echo -e "\n============================================"
echo -e "  XUI.one  |  github.com/greathy19/xonee"
echo -e "============================================\n"

# --------------------------------------------------------------------------
# Detectar OS y versión
# --------------------------------------------------------------------------
if [ -f /etc/lsb-release ]; then
    OS="$(grep DISTRIB_ID /etc/lsb-release | sed 's/^.*=//')"
    VER="$(grep DISTRIB_RELEASE /etc/lsb-release | sed 's/^.*=//')"
elif [ -f /etc/os-release ]; then
    OS="$(grep -w ID /etc/os-release | sed 's/^.*=//' | tr -d '"')"
    VER="$(grep -w VERSION_ID /etc/os-release | sed 's/^.*=//' | tr -d '"')"
else
    OS="$(uname -s)"
    VER="$(uname -r)"
fi
ARCH="$(uname -m)"

echo "Detectado: $OS $VER $ARCH"

# --------------------------------------------------------------------------
# Validar OS soportado
# --------------------------------------------------------------------------
SUPPORTED=0
if [[ "$ARCH" == "x86_64" ]]; then
    if [[ "$OS" == "Ubuntu" && ( "$VER" == "20.04" || "$VER" == "22.04" || "$VER" == "24.04" ) ]]; then
        SUPPORTED=1
    fi
    if [[ "$OS" == "debian" && ( "$VER" == "11" || "$VER" == "12" || "$VER" == "13" ) ]]; then
        SUPPORTED=1
    fi
fi

if [[ "$SUPPORTED" -ne 1 ]]; then
    echo ""
    echo "ERROR: OS no soportado."
    echo "  Ubuntu : 20.04 / 22.04 / 24.04  (x86_64)"
    echo "  Debian : 11 / 12 / 13           (x86_64)"
    echo ""
    exit 1
fi

# --------------------------------------------------------------------------
# Verificar privilegios root
# --------------------------------------------------------------------------
if [[ "$EUID" -ne 0 ]]; then
    echo "Ejecuta este script como root (sudo bash install.sh)."
    exit 1
fi

echo -e "OS válido. Comenzando instalación...\n"

# --------------------------------------------------------------------------
# PASO 1 — Dependencias del sistema
# --------------------------------------------------------------------------
echo "[1/4] Instalando dependencias del sistema..."
wget "$REPO_RAW/install-dep.sh" -qO /tmp/xonee-dep.sh
bash /tmp/xonee-dep.sh
rm -f /tmp/xonee-dep.sh

# --------------------------------------------------------------------------
# PASO 2 — Descargar y descomprimir XUI
# --------------------------------------------------------------------------
echo "[2/4] Descargando XUI 1.5.13..."
cd /root
wget "$XUI_ZIP_URL" -O XUI_1.5.13.zip
unzip -o XUI_1.5.13.zip
rm -f XUI_1.5.13.zip

# --------------------------------------------------------------------------
# PASO 3 — Instalador principal (Python)
# --------------------------------------------------------------------------
echo "[3/4] Ejecutando instalador principal..."
wget "$REPO_RAW/install.python3" -qO /root/install.python3
python3 /root/install.python3

# --------------------------------------------------------------------------
# PASO 4 — Hecho
# --------------------------------------------------------------------------
echo -e "\n[4/4] Instalación finalizada."
