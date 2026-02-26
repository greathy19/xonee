#!/bin/bash
# =============================================================================
#  XUI.one - Instalación de dependencias del sistema
#  Soporta: Ubuntu 20.04/22.04/24.04 | Debian 11/12/13 (x86_64)
# =============================================================================

export DEBIAN_FRONTEND=noninteractive

# Detectar OS
OS_ID="$(grep -w ID /etc/os-release 2>/dev/null | sed 's/^.*=//' | tr -d '"')"
OS_VER="$(grep -w VERSION_ID /etc/os-release 2>/dev/null | sed 's/^.*=//' | tr -d '"')"
echo "[dep] OS detectado: $OS_ID $OS_VER"

# --------------------------------------------------------------------------
# Función de instalación segura (no aborta si el paquete no existe)
# --------------------------------------------------------------------------
pkg_install() {
    apt-get install -y -qq "$1" >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "[dep] OK: $1"
    else
        echo "[dep] SKIP (no disponible): $1"
    fi
}

echo "[dep] Actualizando repositorios..."
apt-get update -y -qq

echo "[dep] Eliminando mysql-server (si existe)..."
apt-get remove -y -qq mysql-server >/dev/null 2>&1 || true

# --------------------------------------------------------------------------
# Paquetes base — disponibles en Ubuntu y Debian 11/12/13
# --------------------------------------------------------------------------
BASE_PKGS=(
    iproute2
    net-tools
    dirmngr
    gpg-agent
    wget
    curl
    gnupg
    ca-certificates
    lsb-release
    unzip
    xz-utils
    zip
    e2fsprogs
    sysstat
    alsa-utils
    v4l-utils
    certbot
    iptables-persistent
    libjpeg-dev
    libpng-dev
    libcurl4
    libgeoip-dev
    libxslt1-dev
    libonig-dev
    libmaxminddb-dev
    libssl-dev
    mariadb-server
    python3
    python3-dev
    python3-pip
    python3-setuptools
)

for pkg in "${BASE_PKGS[@]}"; do
    pkg_install "$pkg"
done

# --------------------------------------------------------------------------
# Paquetes opcionales (existen en Ubuntu pero no siempre en Debian)
# --------------------------------------------------------------------------
OPTIONAL_PKGS=(
    cpufrequtils          # solo disponible si el kernel tiene cpufreq
    php-ssh2              # puede no estar en repos base de Debian 13
    mcrypt                # eliminado desde Debian Buster; disponible en Ubuntu
    software-properties-common   # solo Ubuntu
)

for pkg in "${OPTIONAL_PKGS[@]}"; do
    pkg_install "$pkg"
done

# --------------------------------------------------------------------------
# libmaxminddb: en Debian 13 puede llamarse libmaxminddb0t64
# --------------------------------------------------------------------------
if dpkg -l libmaxminddb0 >/dev/null 2>&1; then
    echo "[dep] OK: libmaxminddb0 (ya instalado)"
else
    # Intentar primero el nombre viejo, luego el nuevo
    apt-get install -y -qq libmaxminddb0 >/dev/null 2>&1 || \
    apt-get install -y -qq libmaxminddb0t64 >/dev/null 2>&1 && \
    echo "[dep] OK: libmaxminddb0/libmaxminddb0t64" || \
    echo "[dep] SKIP: libmaxminddb0"
fi

# mmdb-bin también fue renombrado en Debian 13
apt-get install -y -qq mmdb-bin >/dev/null 2>&1 || \
apt-get install -y -qq libmaxminddb-bin >/dev/null 2>&1 || true

echo "[dep] Dependencias completadas."
