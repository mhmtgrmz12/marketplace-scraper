#!/usr/bin/env bash
# Kurulumdan sonra çalıştır: sudo bash /opt/car-sniper/deploy/check.sh
#   1. Telegram'a deneme mesajı gönderir.
#   2. Facebook'a tek tarama turu yapar. Sunucu IP'sine misafir Marketplace gösteriliyor mu bu turda anlaşılır.
#      İlk tur ilanları sessizce hafızaya alır, Telegram'a ilan gönderilmez.
# Servisle aynı kullanıcı, ortam ve klasörle (systemd-run) çalışır.
set -euo pipefail

APP_DIR=/opt/car-sniper
SERVICE=car-sniper

[ "$(id -u)" -eq 0 ] || { echo "root olarak çalıştır: sudo bash $0" >&2; exit 1; }
if grep -q 'BURAYA' /etc/car-sniper.env; then
    echo "Önce Telegram bilgilerini gir: sudo nano /etc/car-sniper.env" >&2
    exit 1
fi

was_active=false
if systemctl is-active -q "$SERVICE"; then   # aynı hafıza dosyasına iki bot yazmasın
    was_active=true
    echo "Servis kontrol süresince durduruluyor..."
    systemctl stop "$SERVICE"
fi

run() {
    systemd-run --quiet --wait --pipe --collect \
        --uid=carsniper --working-directory="$APP_DIR" \
        -p EnvironmentFile=/etc/car-sniper.env \
        -E PLAYWRIGHT_BROWSERS_PATH="$APP_DIR/.browsers" -E TZ=Europe/Brussels -E PYTHONUNBUFFERED=1 \
        "$APP_DIR/.venv/bin/python" "$@"
}

status=0
echo "== 1/2 Telegram deneme mesajı"
run car_sniper.py --test || status=1
echo
echo "== 2/2 Facebook tarama turu"
run -c 'import car_sniper as cs; cs.run_cycle(cs.SeenStore(cs.SEEN_FILE))' || status=1

cat <<'EOF'

Kontrol et:
  - Telefona "2012 Volkswagen Polo 1.2 (TEST)" mesajı geldi mi?
  - Yukarıda "📍 Taranan konum: Lummen, Belgium" ve "🔍 ... ilan tarandı" ya da "İlk tarama tamamlandı" var mı?
  - "🚫 Facebook giriş duvarı" ya da "ilan kartı bulunamadı" görürsen Facebook bu sunucu IP'sini misafir
    olarak kabul etmiyor demektir (deploy/README.md → Sorunlar).
EOF

if $was_active; then
    systemctl start "$SERVICE"
    echo "Servis tekrar başlatıldı."
fi
exit $status
