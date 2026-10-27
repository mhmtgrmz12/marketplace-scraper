# Car Sniper'ı sunucuda 7/24 çalıştırmak

Bot bir Linux sunucuda `systemd` servisi olarak çalışır: sunucu açılınca kendiliğinden başlar, çökerse
60 sn sonra yeniden başlar, Mac'in kapalı olması fark etmez.

| Dosya | Ne yapar |
|---|---|
| `setup.sh` | Kurar ya da günceller: paketler, `carsniper` kullanıcısı, kod `/opt/car-sniper`'a, Python ortamı, Chromium, gerekirse swap, servis |
| `car-sniper.service` | systemd servisi (`/etc/systemd/system/` altına kopyalanır) |
| `check.sh` | Kurulumdan sonra: Telegram deneme mesajı + Facebook'a tek tarama turu |

## 1. Sunucu

- **Ubuntu 24.04** (Debian 12 de olur), **Avrupa'da** (Almanya/Hollanda/Belçika), en az **2 GB RAM**
  (Chromium ~1 GB kullanır; 2 GB'den azsa `setup.sh` 2 GB swap açar).
- Öneri: Hetzner Cloud CX22 (~€4-5/ay). DigitalOcean, Vultr ya da Oracle Cloud (ücretsiz katman) da olur.
- Sunucuyu oluştururken SSH anahtarını ekle, sonra bağlan: `ssh root@SUNUCU_IP`

## 2. Kurulum

```bash
curl -fsSL https://raw.githubusercontent.com/mhmtgrmz12/marketplace-scraper/main/deploy/setup.sh | sudo bash
```

Kurulum ~3-5 dakika sürer. `deploy/` klasörü GitHub'daki `main` dalında olmalı (push edilmiş olmalı).

## 3. Telegram bilgileri

```bash
sudo nano /etc/car-sniper.env
```

`BURAYA_...` yazan yerlere token ve chat ID'yi yaz (tırnak ve `export` yok). Dosya sadece root tarafından
okunabilir (izin 600); token repoya hiç girmez.

## 4. Kontrol ve başlatma

```bash
sudo bash /opt/car-sniper/deploy/check.sh
```

- Telefona "2012 Volkswagen Polo 1.2 (TEST)" mesajı gelmeli.
- Çıktıda `📍 Taranan konum: Lummen, Belgium` ve `✅ İlk tarama tamamlandı, X adet mevcut ilan...` görünmeli.
  Bu ilk tur ilanları sessizce hafızaya alır, Telegram'a ilan göndermez.

Sorun yoksa botu başlat:

```bash
sudo systemctl start car-sniper
```

## Günlük kullanım

| Ne | Komut |
|---|---|
| Canlı log | `journalctl -u car-sniper -f` |
| Son 200 satır | `journalctl -u car-sniper -n 200 --no-pager` |
| Durum | `systemctl status car-sniper` |
| Durdur / başlat | `sudo systemctl stop car-sniper` / `sudo systemctl start car-sniper` |
| Kodu güncelle (GitHub'dan çek, yeniden başlat) | `sudo bash /opt/car-sniper/deploy/setup.sh` |
| Hafızayı sıfırla (sonraki tur yine sessiz) | `sudo systemctl stop car-sniper && sudo rm /opt/car-sniper/seen_cars.json && sudo systemctl start car-sniper` |

Ayarları (fiyat, yıl, km, kelime listesi) `car_sniper.py`'de değiştirip GitHub'a push et, sonra sunucuda
`setup.sh`'ı tekrar çalıştır. Sunucuda dosyayı elle değiştirirsen sonraki güncelleme (`git pull`) hata verir.

## Sorunlar

- **`🚫 Facebook giriş duvarı` ya da `ilan kartı bulunamadı`:** Facebook bu sunucunun IP'sine misafir
  Marketplace'i göstermiyor. Bot ev IP'sinden test edildi; veri merkezi IP'leri daha sık engellenir.
  Önce birkaç saat bekleyip tekrar dene, sonra başka bir sağlayıcı/bölge dene. Son çare konut (residential) proxy.
- **Telegram mesajı gelmiyor:** `journalctl -u car-sniper | grep Telegram` ile hata mesajına bak. Token/chat ID
  yanlışsa `/etc/car-sniper.env`'i düzeltip `sudo systemctl restart car-sniper`.
- **`net::ERR_NAME_NOT_RESOLVED` sürekli:** sunucunun DNS'i çalışmıyor; `getent hosts www.facebook.com` ile dene.
- **Bot sürekli yeniden başlıyor:** `journalctl -u car-sniper -n 100` ile son hatayı oku. Bellek yetmiyorsa
  (`Killed`, `Target crashed`) daha fazla RAM'li sunucuya geç.
