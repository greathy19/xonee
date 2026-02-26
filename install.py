#!/usr/bin/python3
# install.python3 - Adaptado para Debian 13 (Trixie)
# Basado en: https://raw.githubusercontent.com/amidevous/xui.one/refs/heads/master/install.python3

import subprocess, os, random, string, sys, shutil, socket, time, io, platform

if sys.version_info.major != 3:
    print("Please run with python3.")
    sys.exit(1)

rPath = os.path.dirname(os.path.realpath(__file__))

# -------------------------------------------------------
# Paquetes adaptados para Debian 13 (Trixie)
# Eliminados:  python, python-dev, mcrypt (no existen),
#              software-properties-common (es de Ubuntu),
#              python2, python2-dev, python2.7, python2.7-dev
# Renombrados: libmaxminddb0 -> libmaxminddb0t64 en Debian 13
#              mmdb-bin -> libmaxminddb-bin
# Añadidos:    python3-pip, python3-setuptools, libssl-dev
# -------------------------------------------------------
rPackages = [
    "iproute2",
    "net-tools",
    "dirmngr",
    "gpg-agent",
    "libmaxminddb0",          # puede llamarse libmaxminddb0t64 en Debian 13
    "libmaxminddb-dev",
    "libmaxminddb-bin",       # reemplaza mmdb-bin
    "libcurl4",
    "libgeoip-dev",
    "libxslt1-dev",
    "libonig-dev",
    "e2fsprogs",
    "wget",
    "mariadb-server",
    "sysstat",
    "alsa-utils",
    "v4l-utils",
    "certbot",
    "iptables-persistent",
    "libjpeg-dev",
    "libpng-dev",
    "xz-utils",
    "zip",
    "unzip",
    "python3",
    "python3-dev",
    "python3-pip",
    "python3-setuptools",
    "libssl-dev",
    "curl",
    "gnupg",
    "lsb-release",
    "ca-certificates",
]

rRemove = ["mysql-server"]

rMySQLCnf = '''# XUI
[client]
port                            = 3306

[mysqld_safe]
nice                            = 0

[mysqld]
user                            = mysql
port                            = 3306
basedir                         = /usr
datadir                         = /var/lib/mysql
tmpdir                          = /tmp
lc-messages-dir                 = /usr/share/mysql
skip-external-locking
skip-name-resolve
bind-address                    = *

key_buffer_size                 = 128M
myisam_sort_buffer_size         = 4M
max_allowed_packet              = 64M
myisam-recover-options          = BACKUP
max_length_for_sort_data        = 8192
query_cache_limit               = 0
query_cache_size                = 0
query_cache_type                = 0
expire_logs_days                = 10
max_binlog_size                 = 100M
max_connections                 = 8192
back_log                        = 4096
open_files_limit                = 20240
innodb_open_files               = 20240
max_connect_errors              = 3072
table_open_cache                = 4096
table_definition_cache          = 4096
tmp_table_size                  = 1G
max_heap_table_size             = 1G

innodb_buffer_pool_size         = 10G
innodb_buffer_pool_instances    = 10
innodb_read_io_threads          = 64
innodb_write_io_threads         = 64
innodb_thread_concurrency       = 0
innodb_flush_log_at_trx_commit  = 0
innodb_flush_method             = O_DIRECT
performance_schema              = 0
innodb-file-per-table           = 1
innodb_io_capacity              = 20000
innodb_table_locks              = 0
innodb_lock_wait_timeout        = 0

sql_mode                        = "NO_ENGINE_SUBSTITUTION"

[mariadb]

thread_cache_size               = 8192
thread_handling                 = pool-of-threads
thread_pool_size                = 12
thread_pool_idle_timeout        = 20
thread_pool_max_threads         = 1024

[mysqldump]
quick
quote-names
max_allowed_packet              = 16M

[mysql]

[isamchk]
key_buffer_size                 = 16M'''

rConfig = '''; XUI Configuration
[XUI]
hostname    =   "127.0.0.1"
database    =   "xui"
port        =   3306
server_id   =   1
license     =   ""

[Encrypted]
username    =   "%s"
password    =   "%s"'''

rRedisConfig = """bind *
protected-mode yes
port 6379
tcp-backlog 511
timeout 0
tcp-keepalive 300
daemonize yes
supervised no
pidfile /home/xui/bin/redis/redis-server.pid
loglevel warning
logfile /home/xui/bin/redis/redis-server.log
databases 1
always-show-logo yes
stop-writes-on-bgsave-error no
rdbcompression no
rdbchecksum no
dbfilename dump.rdb
dir /home/xui/bin/redis/
slave-serve-stale-data yes
slave-read-only yes
repl-diskless-sync no
repl-diskless-sync-delay 5
repl-disable-tcp-nodelay no
slave-priority 100
requirepass #PASSWORD#
maxclients 655350
lazyfree-lazy-eviction no
lazyfree-lazy-expire no
lazyfree-lazy-server-del no
slave-lazy-flush no
appendonly no
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-load-truncated yes
aof-use-rdb-preamble no
lua-time-limit 5000
slowlog-log-slower-than 10000
slowlog-max-len 128
latency-monitor-threshold 0
notify-keyspace-events ""
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
list-compress-depth 0
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
hll-sparse-max-bytes 3000
activerehashing yes
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit slave 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60
hz 10
aof-rewrite-incremental-fsync yes
save 60 1000
server-threads 4
server-thread-affinity true"""

rSysCtl = '''# XUI.one

net.ipv4.tcp_congestion_control = bbr
net.core.default_qdisc = fq
net.ipv4.tcp_rmem = 8192 87380 134217728
net.ipv4.udp_rmem_min = 16384
net.core.rmem_default = 262144
net.core.rmem_max = 268435456
net.ipv4.tcp_wmem = 8192 65536 134217728
net.ipv4.udp_wmem_min = 16384
net.core.wmem_default = 262144
net.core.wmem_max = 268435456
net.core.somaxconn = 1000000
net.core.netdev_max_backlog = 250000
net.core.optmem_max = 65535
net.ipv4.tcp_max_tw_buckets = 1440000
net.ipv4.tcp_max_orphans = 16384
net.ipv4.ip_local_port_range = 2000 65000
net.ipv4.tcp_no_metrics_save = 1
net.ipv4.tcp_slow_start_after_idle = 0
net.ipv4.tcp_fin_timeout = 15
net.ipv4.tcp_keepalive_time = 300
net.ipv4.tcp_keepalive_probes = 5
net.ipv4.tcp_keepalive_intvl = 15
fs.file-max=20970800
fs.nr_open=20970800
fs.aio-max-nr=20970800
net.ipv4.tcp_timestamps = 1
net.ipv4.tcp_window_scaling = 1
net.ipv4.tcp_mtu_probing = 1
net.ipv4.route.flush = 1
net.ipv6.route.flush = 1'''

rSystemd = '''[Unit]
SourcePath=/home/xui/service
Description=XUI.one Service
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=root
Restart=always
RestartSec=1
ExecStart=/bin/bash /home/xui/service start
ExecRestart=/bin/bash /home/xui/service restart
ExecStop=/bin/bash /home/xui/service stop

[Install]
WantedBy=multi-user.target'''

rChoice = "23456789abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ"


class col:
    HEADER    = '\033[95m'
    OKBLUE    = '\033[94m'
    OKGREEN   = '\033[92m'
    WARNING   = '\033[93m'
    FAIL      = '\033[91m'
    ENDC      = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'


def generate(length=32):
    return ''.join(random.choice(rChoice) for i in range(length))


def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def printc(rText, rColour=col.OKBLUE, rPadding=0):
    rLeft  = int(30 - (len(rText) / 2))
    rRight = (60 - rLeft - len(rText))
    print("%s |--------------------------------------------------------------| %s" % (rColour, col.ENDC))
    for i in range(rPadding):
        print("%s |                                                              | %s" % (rColour, col.ENDC))
    print("%s | %s%s%s | %s" % (rColour, " " * rLeft, rText, " " * rRight, col.ENDC))
    for i in range(rPadding):
        print("%s |                                                              | %s" % (rColour, col.ENDC))
    print("%s |--------------------------------------------------------------| %s" % (rColour, col.ENDC))
    print(" ")


def detect_os():
    """Detecta si el OS es Debian 13 (Trixie) o compatible."""
    os_id = ""
    os_ver = ""
    try:
        with open("/etc/os-release") as f:
            for line in f:
                line = line.strip().strip('"')
                if line.startswith("ID="):
                    os_id = line.split("=", 1)[1].strip('"')
                elif line.startswith("VERSION_ID="):
                    os_ver = line.split("=", 1)[1].strip('"')
    except Exception:
        pass
    return os_id.lower(), os_ver


def install_package_safe(pkg):
    """Instala un paquete ignorando error si no existe."""
    ret = os.system(
        "sudo DEBIAN_FRONTEND=noninteractive apt-get -yq install %s >/dev/null 2>&1" % pkg
    )
    if ret != 0:
        print("%s[WARN] Package not found or failed: %s%s" % (col.WARNING, pkg, col.ENDC))


if __name__ == "__main__":

    # --------------------------------------------------
    # Verificar OS
    # --------------------------------------------------
    os_id, os_ver = detect_os()
    arch = os.uname().machine

    print("Detected OS: %s %s %s" % (os_id, os_ver, arch))

    supported = (
        (os_id == "debian" and os_ver in ["12", "13"]) or
        (os_id == "ubuntu" and os_ver in ["20.04", "22.04", "24.04"])
    )

    if not supported or arch != "x86_64":
        printc("OS no soportado. Usa Debian 12/13 o Ubuntu 20.04/22.04/24.04 (x86_64)", col.FAIL)
        sys.exit(1)

    if not os.path.exists("./xui.tar.gz") and not os.path.exists("./xui_trial.tar.gz"):
        print("Fatal Error: xui.tar.gz is missing. Please download it from XUI billing panel.")
        sys.exit(1)

    printc("XUI", col.OKGREEN, 2)
    rHost     = "127.0.0.1"
    rServerID = 1
    rUsername = generate()
    rPassword = generate()
    rDatabase = "xui"
    rPort     = 3306

    if os.path.exists("/home/xui/"):
        printc("XUI Directory Exists!")
        while True:
            rAnswer = input("Continue and overwrite? (Y / N) : ")
            if rAnswer.upper() in ["Y", "N"]: break
        if rAnswer.upper() == "N": sys.exit(1)

    # --------------------------------------------------
    # Preparar e instalar paquetes
    # --------------------------------------------------
    printc("Preparing Installation")

    for rFile in [
        "/var/lib/dpkg/lock-frontend",
        "/var/cache/apt/archives/lock",
        "/var/lib/dpkg/lock",
        "/var/lib/apt/lists/lock"
    ]:
        if os.path.exists(rFile):
            try: os.remove(rFile)
            except: pass

    printc("Updating system")
    os.system("sudo DEBIAN_FRONTEND=noninteractive apt-get update -y >/dev/null 2>&1")

    for rPackage in rRemove:
        printc("Removing %s" % rPackage)
        os.system(
            "sudo DEBIAN_FRONTEND=noninteractive apt-get remove %s -y >/dev/null 2>&1" % rPackage
        )

    for rPackage in rPackages:
        printc("Installing %s" % rPackage)
        install_package_safe(rPackage)

    # En Debian 13 el paquete puede haberse renombrado a libmaxminddb0t64
    ret = os.system("dpkg -l libmaxminddb0 >/dev/null 2>&1")
    if ret != 0:
        install_package_safe("libmaxminddb0t64")

    # --------------------------------------------------
    # Crear usuario xui
    # --------------------------------------------------
    try:
        subprocess.check_output("getent passwd xui".split())
    except:
        printc("Creating user")
        os.system(
            "sudo adduser --system --shell /bin/false --group --disabled-login xui >/dev/null 2>&1"
        )

    os.system("mkdir -p /home/xui >/dev/null 2>&1")

    # --------------------------------------------------
    # Instalar XUI
    # --------------------------------------------------
    printc("Installing XUI")
    tar_file = "./xui.tar.gz" if os.path.exists("./xui.tar.gz") else "./xui_trial.tar.gz"

    os.system('sudo tar -zxvf "%s" -C "/home/xui/" >/dev/null 2>&1' % tar_file)
    os.system(
        'sudo wget https://raw.githubusercontent.com/amidevous/xui.one/master/build-php.sh '
        '-O /root/build-php.sh >/dev/null 2>&1'
    )
    os.system('cd /root && sudo bash /root/build-php.sh >/dev/null 2>&1')
    os.system('sudo rm -rf /root/build-php.sh >/dev/null 2>&1')

    if not os.path.exists("/home/xui/status"):
        printc("Failed to extract! Exiting", col.FAIL)
        sys.exit(1)

    # --------------------------------------------------
    # Configurar MySQL / MariaDB
    # --------------------------------------------------
    printc("Configuring MySQL")
    rCreate = True
    if os.path.exists("/etc/mysql/my.cnf"):
        if open("/etc/mysql/my.cnf", "r").read(5) == "# XUI":
            rCreate = False
    if rCreate:
        with io.open("/etc/mysql/my.cnf", "w", encoding="utf-8") as f:
            f.write(rMySQLCnf)
        # Debian 13 usa 'mariadb' como nombre de servicio
        os.system("sudo systemctl restart mariadb >/dev/null 2>&1")
        os.system("sudo service mariadb restart >/dev/null 2>&1")

    rExtra = ""
    rRet = os.system("mysql -u root -e \"SELECT VERSION();\"")
    if rRet != 0:
        while True:
            rExtra = " -p%s" % input("Root MySQL Password: ")
            rRet = os.system("mysql -u root%s -e \"SELECT VERSION();\"" % rExtra)
            if rRet == 0: break
            else: printc("Invalid password! Please try again.")

    for sql in [
        "DROP DATABASE IF EXISTS xui; CREATE DATABASE IF NOT EXISTS xui;",
        "DROP DATABASE IF EXISTS xui_migrate; CREATE DATABASE IF NOT EXISTS xui_migrate;",
    ]:
        os.system('sudo mysql -u root%s -e "%s" >/dev/null 2>&1' % (rExtra, sql))

    os.system('sudo mysql -u root%s xui < "/home/xui/bin/install/database.sql" >/dev/null 2>&1' % rExtra)

    for host in ["localhost", "127.0.0.1"]:
        os.system('sudo mysql -u root%s -e "CREATE USER IF NOT EXISTS \'%s\'@\'%s\' IDENTIFIED BY \'%s\';" >/dev/null 2>&1' % (rExtra, rUsername, host, rPassword))
        for db in ["xui.*", "xui_migrate.*", "mysql.*"]:
            os.system('sudo mysql -u root%s -e "GRANT ALL PRIVILEGES ON %s TO \'%s\'@\'%s\';" >/dev/null 2>&1' % (rExtra, db, rUsername, host))
        os.system('sudo mysql -u root%s -e "GRANT GRANT OPTION ON xui.* TO \'%s\'@\'%s\';" >/dev/null 2>&1' % (rExtra, rUsername, host))

    os.system('sudo mysql -u root%s -e "FLUSH PRIVILEGES;" >/dev/null 2>&1' % rExtra)

    with io.open("/home/xui/config/config.ini", "w", encoding="utf-8") as f:
        f.write(rConfig % (rUsername, rPassword))

    # --------------------------------------------------
    # Configurar sistema
    # --------------------------------------------------
    printc("Configuring System")

    if not "/home/xui/" in open("/etc/fstab").read():
        with io.open("/etc/fstab", "a", encoding="utf-8") as f:
            f.write(
                "\ntmpfs /home/xui/content/streams tmpfs defaults,noatime,nosuid,nodev,noexec,mode=1777,size=90% 0 0"
                "\ntmpfs /home/xui/tmp tmpfs defaults,noatime,nosuid,nodev,noexec,mode=1777,size=6G 0 0"
            )

    for old in ["/etc/init.d/xuione", "/etc/systemd/system/xui.service"]:
        if os.path.exists(old): os.remove(old)

    if not os.path.exists("/etc/systemd/system/xuione.service"):
        with io.open("/etc/systemd/system/xuione.service", "w", encoding="utf-8") as f:
            f.write(rSystemd)
        os.system("sudo chmod +x /etc/systemd/system/xuione.service >/dev/null 2>&1")
        os.system("sudo systemctl daemon-reload >/dev/null 2>&1")
        os.system("sudo systemctl enable xuione >/dev/null 2>&1")
        os.system("sudo modprobe ip_conntrack >/dev/null 2>&1 || sudo modprobe nf_conntrack >/dev/null 2>&1")
        with io.open("/etc/sysctl.conf", "w", encoding="utf-8") as f:
            f.write(rSysCtl)
        os.system("sudo sysctl -p >/dev/null 2>&1")
        open("/home/xui/config/sysctl.on", "w").close()

    system_conf = open("/etc/systemd/system.conf").read()
    if "DefaultLimitNOFILE=655350" not in system_conf:
        os.system('echo "\nDefaultLimitNOFILE=655350" | sudo tee -a /etc/systemd/system.conf >/dev/null 2>&1')
        os.system('echo "\nDefaultLimitNOFILE=655350" | sudo tee -a /etc/systemd/user.conf >/dev/null 2>&1')

    if not os.path.exists("/home/xui/bin/redis/redis.conf"):
        with io.open("/home/xui/bin/redis/redis.conf", "w", encoding="utf-8") as f:
            f.write(rRedisConfig)

    # --------------------------------------------------
    # Access Code
    # --------------------------------------------------
    rCodeDir  = "/home/xui/bin/nginx/conf/codes/"
    rHasAdmin = None
    for rCode in os.listdir(rCodeDir):
        if rCode.endswith(".conf"):
            if rCode.split(".")[0] == "setup":
                os.remove(rCodeDir + "setup.conf")
            elif "/home/xui/admin" in open(rCodeDir + rCode, "r").read():
                rHasAdmin = rCode

    if not rHasAdmin:
        rCode = generate(8)
        os.system(
            'sudo mysql -u root%s -e "USE xui; INSERT INTO access_codes(code, type, enabled, groups) '
            'VALUES(\'%s\', 0, 1, \'[1]\');" >/dev/null 2>&1' % (rExtra, rCode)
        )
        rTemplate = open(rCodeDir + "template").read()
        rTemplate = rTemplate.replace("#WHITELIST#", "")
        rTemplate = rTemplate.replace("#TYPE#", "admin")
        rTemplate = rTemplate.replace("#CODE#", rCode)
        rTemplate = rTemplate.replace("#BURST#", "500")
        with io.open("%s%s.conf" % (rCodeDir, rCode), "w", encoding="utf-8") as f:
            f.write(rTemplate)
    else:
        rCode = rHasAdmin.split(".")[0]

    # --------------------------------------------------
    # Finalizar
    # --------------------------------------------------
    os.system("sudo mount -a >/dev/null 2>&1")
    os.system("sudo chown xui:xui -R /home/xui >/dev/null 2>&1")
    time.sleep(60)
    os.system("sudo systemctl daemon-reload >/dev/null 2>&1")
    time.sleep(60)
    os.system("sudo systemctl start xuione >/dev/null 2>&1")
    time.sleep(10)
    os.system("sudo /home/xui/status 1 >/dev/null 2>&1")
    time.sleep(60)
    os.system("sudo wget https://github.com/amidevous/xui.one/releases/download/test/xui_crack.tar.gz -qO /root/xui_crack.tar.gz >/dev/null 2>&1")
    os.system("sudo tar -xvf /root/xui_crack.tar.gz >/dev/null 2>&1")
    os.system("sudo systemctl stop xuione >/dev/null 2>&1")
    os.system("sudo cp -r license /home/xui/config/license >/dev/null 2>&1")
    os.system("sudo cp -r xui.so /home/xui/bin/php/lib/php/extensions/no-debug-non-zts-20190902/xui.so >/dev/null 2>&1")
    os.system('sudo sed -i "s/^license.*/license     =   \\"cracked\\"/g" /home/xui/config/config.ini >/dev/null 2>&1')
    os.system("sudo systemctl start xuione >/dev/null 2>&1")
    os.system("sudo /home/xui/bin/php/bin/php /home/xui/includes/cli/startup.php >/dev/null 2>&1")
    time.sleep(60)

    with io.open(rPath + "/credentials.txt", "w", encoding="utf-8") as f:
        f.write("MySQL Username: %s\nMySQL Password: %s" % (rUsername, rPassword))
        f.write("\nContinue Setup: http://%s/%s" % (getIP(), rCode))

    printc("Installation completed!", col.OKGREEN, 2)
    printc("Continue Setup: http://%s/%s" % (getIP(), rCode))
    print(" ")
    printc("Your mysql credentials have been saved to:")
    printc(rPath + "/credentials.txt")
    print(" ")
    printc("Please move this file somewhere safe!")
