# XUI.one — Instalador unificado

Fork y mejora de [amidevous/xui.one](https://github.com/amidevous/xui.one) con soporte para **Ubuntu y Debian**.

## OS soportados (x86_64)

| OS | Versiones |
|---|---|
| Ubuntu | 20.04 / 22.04 / 24.04 |
| Debian | 11 (Bullseye) / 12 (Bookworm) / 13 (Trixie) |

## Instalación

```bash
sudo wget https://raw.githubusercontent.com/greathy19/xonee/main/install.sh \
     -O /root/install.sh && sudo bash /root/install.sh
```

## Archivos del repositorio

| Archivo | Descripción |
|---|---|
| `install.sh` | Entrada principal — detecta OS y orquesta todo |
| `install-dep.sh` | Instala dependencias del sistema (Ubuntu + Debian) |
| `install.python3` | Instalador principal: MariaDB, PHP, Redis, servicio |
| `install-crack.sh` | Aplica licencia |
| `build-php.sh` | Compila PHP para XUI |

## Créditos

- [amidevous/xui.one](https://github.com/amidevous/xui.one) — base original
- [PabloServers/xui.one](https://github.com/PabloServers/xui.one) — referencia
