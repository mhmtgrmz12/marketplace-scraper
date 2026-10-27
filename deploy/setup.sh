#!/usr/bin/env bash
# Car Sniper'ı bir Ubuntu/Debian sunucuya kurar ya da günceller (tekrar çalıştırmak güvenli).
#
#   curl -fsSL https://raw.githubusercontent.com/mhmtgrmz12/marketplace-scraper/main/deploy/setup.sh | sudo bash
#
# Yaptıkları: sistem paketleri, "carsniper" kullanıcısı, kod /opt/car-sniper'a (git), Python sanal ortamı,
# Chromium ve kütüphaneleri, RAM 2 GB'den azsa swap, /etc/car-sniper.env şablonu, systemd servisi.
# Telegram bilgileri girilmişse servis başlatılır/yeniden başlatılır.
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/mhmtgrmz12/marketplace-scraper.git}"
APP_DIR=/opt/car-sniper
APP_USER=carsniper
ENV_FILE=/etc/car-sniper.env
SERVICE=car-sniper

log() { printf '\n==> %s\n' "$*"; }
as_app() { runuser -u "$APP_USER" -- "$@"; }

[ "$(id -u)" -eq 0 ] || { echo "root olarak çalıştır: sudo bash $0" >&2; exit 1; }

log "Sistem paketleri"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq git python3 python3-venv ca-certificates >/dev/null

log "Kullanıcı ve kod ($APP_DIR)"
id "$APP_USER" >/dev/null 2>&1 || useradd --system --home-dir "$APP_DIR" --shell /usr/sbin/nologin "$APP_USER"
if [ -d "$APP_DIR/.git" ]; then
    as_app git -C "$APP_DIR" pull --ff-only
else
    install -d -o "$APP_USER" -g "$APP_USER" "$APP_DIR"
    as_app git clone -q "$REPO_URL" "$APP_DIR"
fi

log "Python ortamı ve Chromium"
[ -x "$APP_DIR/.venv/bin/python" ] || as_app python3 -m venv "$APP_DIR/.venv"
as_app "$APP_DIR/.venv/bin/pip" install -q --upgrade pip
as_app "$APP_DIR/.venv/bin/pip" install -q -r "$APP_DIR/requirements.txt"
"$APP_DIR/.venv/bin/python" -m playwright install-deps chromium >/dev/null   # sistem kütüphaneleri (root)
as_app env PLAYWRIGHT_BROWSERS_PATH="$APP_DIR/.browsers" "$APP_DIR/.venv/bin/python" -m playwright install chromium

# Chromium ~1 GB kullanıyor; küçük sunucuda bellek yetmezse tarayıcı çöker.
mem_kb=$(awk '/MemTotal/ {print $2}' /proc/meminfo)
if [ "$mem_kb" -lt 2000000 ] && ! swapon --show | grep -q .; then
    log "RAM 2 GB'den az, 2 GB swap açılıyor"
    if fallocate -l 2G /swapfile 2>/dev/null && chmod 600 /swapfile && mkswap /swapfile >/dev/null && swapon /swapfile; then
        grep -q '^/swapfile ' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
    else
        rm -f /swapfile
        echo "UYARI: swap açılamadı (konteyner olabilir), devam ediliyor."
    fi
fi

if [ ! -f "$ENV_FILE" ]; then
    log "Telegram bilgileri için $ENV_FILE oluşturuldu"
    install -m 600 -o root -g root /dev/null "$ENV_FILE"
    cat > "$ENV_FILE" <<'EOF'
# Car Sniper Telegram bilgileri. systemd biçimi: "export" ve tırnak yok.
TELEGRAM_BOT_TOKEN=BURAYA_BOT_TOKEN_YAZ
TELEGRAM_CHAT_ID=BURAYA_CHAT_ID_YAZ
EOF
fi

if [ ! -d /run/systemd/system ]; then
    echo "UYARI: systemd çalışmıyor (konteyner?), servis kurulmadı."
    exit 0
fi

log "systemd servisi"
install -m 644 "$APP_DIR/deploy/car-sniper.service" "/etc/systemd/system/$SERVICE.service"
systemctl daemon-reload
systemctl enable -q "$SERVICE"

if grep -q 'BURAYA' "$ENV_FILE"; then
    cat <<EOF

Kurulum tamam, ama Telegram bilgileri henüz girilmedi. Sıradaki adımlar:
  1. Token ve chat ID'yi yaz:                  sudo nano $ENV_FILE
  2. Telegram + Facebook kontrolü:             sudo bash $APP_DIR/deploy/check.sh
  3. Botu başlat:                              sudo systemctl start $SERVICE
  4. Canlı log:                                journalctl -u $SERVICE -f
EOF
else
    systemctl restart "$SERVICE"
    echo
    echo "Servis (yeniden) başlatıldı. Canlı log: journalctl -u $SERVICE -f"
fi
