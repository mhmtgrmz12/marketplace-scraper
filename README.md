# marketplace-scraper

`car_sniper.py`: Facebook Marketplace'e düşen yeni araba ilanlarını yakalayıp Telegram'a
fotoğraflı bildirim olarak gönderen, Swoopa benzeri bir "sniper" botu. Facebook'a giriş
yapmadan (misafir olarak) çalışır.

## 1. Kurulum

```bash
pip install -r requirements.txt        # veya: pip install playwright requests
python -m playwright install chromium
# Linux sunucuda sistem kütüphaneleri eksikse:
# python -m playwright install --with-deps chromium
```

## 2. Telegram Bot Token ve Chat ID

1. Telegram'da **@BotFather**'a `/newbot` yaz, bota bir isim ver. Verdiği
   `123456789:AA...` şeklindeki metin **Bot Token**'ın.
2. Yeni botuna Telegram'dan herhangi bir mesaj at (örneğin `/start`).
3. Tarayıcıda `https://api.telegram.org/bot<TOKEN>/getUpdates` adresini aç.
   `"chat":{"id":123456789,...}` içindeki sayı **Chat ID**'n. Grup için botu gruba ekleyip
   grupta mesaj yaz; grup ID'si `-100...` ile başlar.
4. Bu iki değeri `car_sniper.py` içindeki `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID`
   alanlarına yaz ya da aynı isimli ortam değişkenleri olarak ver.
5. Doğrulamak için: `python car_sniper.py --test`

## 3. Doğru Marketplace arama linkini almak

Bot Facebook'a giriş yapmadığı için linkte **konum olmak zorunda**. Konumsuz linkte
(`/marketplace/category/vehicles`) Facebook misafire San Francisco ilanlarını gösterir.

1. **Gizli pencerede (giriş yapmadan)** `facebook.com/marketplace` → **Vehicles**'a gir.
   "Cars" alt kategorisini kullanma: misafire sıralamayı yok sayıp saatler önceki ilanları gösteriyor.
   Vehicles'taki jant, lastik, parça, bisiklet, scooter ve römork ilanlarını bot Facebook'un ilan kategorisine
   bakarak eler (sadece "Cars & Trucks" gönderilir, `CAR_CATEGORIES`).
2. **Konum**: Soldaki filtrelerde konuma ("Location: ...") tıkla, şehrini yazıp seç, **Apply**.
   Konum linke yazılmaz, oturumda kalır. Linkte gerekli olan **sayısal konum ID'sini** bulmak için
   konumu seçtikten sonra sayfadaki kategori linklerine bak: `/marketplace/<ID>/vehicles/` biçimindedir.
   Şehir adıyla (`/marketplace/beringen/`) ya da `latitude`/`longitude` ile çalışmaz.
   Beringen için Facebook'un en yakın konumu Lummen: `110843235610039`.
3. **Çap**: Varsayılan 65 km. Değiştirmek için linkin sonuna `&radius=40` gibi ekle.
4. **Sırala**: Linkte `sortBy=creation_time_descend` (Date listed: Newest first) olmalı.
   Bu ayar **çok önemli**: en yeni ilanlar en üstte olmazsa bot yeni ilanları geç görür.
   Linki gizli pencerede açınca solda "Sort by: Date listed: Newest first" yazmalı.
5. Linki `SEARCH_URLS` listesine ekle. Bot her taramada taradığı konumu loglar
   (`📍 Taranan konum: Lummen, Belgium, Within 65 km`); yanlış şehir görürsen linki kontrol et.

Kullanılan link (Lummen, 65 km, en yeniler önce):

```
https://www.facebook.com/marketplace/110843235610039/vehicles?sortBy=creation_time_descend&exact=false
```

## 4. Filtreler

`car_sniper.py` başındaki "Filtreler" bölümünden değiştirilebilir:

| Ayar | Varsayılan | Ne yapar |
|---|---|---|
| `MAX_PRICE` | 2000 | Bunun üstündeki ilanlar gönderilmez (2000 dahil gönderilir) |
| `MIN_PRICE` | 100 | Bunun altındaki fiyatlar (1 €, 50 €) sahte sayılıp atlanır |
| `FAKE_PRICES` | 123, 1234, 12345 | Sahte fiyat olarak atlanır |
| `SKIP_YEAR_AT_OR_BELOW` | 2008 | Başlıkta/açıklamada yıl bu ve daha eskiyse gönderilmez |
| `SKIP_KM_ABOVE` | 200000 | Km bunun üstündeyse gönderilmez |
| `CHECK_DESCRIPTION` | True | Yeni ilanın sayfasını açıp açıklamayı okur |
| `CAR_CATEGORIES` | Cars & Trucks | Sadece Facebook'un bu kategoriye koyduğu ilanlar gönderilir (jant, lastik, parça, bisiklet, scooter, römork gönderilmez) |
| `NOT_A_CAR_WORDS` | jante, pneus, banden, remorque, moteur, vélo... | Başlığı bu kelimelerden biriyle başlayan ilan sayfası açılmadan atlanır |

- Ücretsiz (Free / 0 €) ilanlar her zaman atlanır.
- Yıl ya da km bulunamazsa ilan bu yüzden elenmez, gönderilir. Mesajda "bilinmiyor" yazar.
- Elenen ilanlar konsolda `⏭️ Atlandı (sebep)` satırıyla görünür ve bir daha kontrol edilmez.

## 5. Çalıştırma

```bash
python car_sniper.py
```

- **İlk çalıştırmada** mevcut ilanlar bildirim atılmadan `seen_cars.json` dosyasına kaydedilir.
  Sonraki turlardan itibaren sadece yeni düşen ilanlar Telegram'a gönderilir.
- `SEARCH_URLS`'e sonradan eklediğin linkler de ilk taramada sessizce hafızaya alınır,
  böylece mesaj yağmuru olmaz.
- Varsayılan tarama aralığı 180 sn + 15-45 sn rastgele beklemedir. Aralığı çok düşürürsen
  Facebook IP'ni geçici olarak engelleyebilir.
- Tarayıcıyı görmek ya da engelleme sorunlarını incelemek için `HEADLESS = False` yap.

## 6. Test

```bash
python -m unittest discover -s tests -v
```

Testler gerçek Facebook'a ve Telegram'a bağlanmaz: ayrıştırma/filtre testleri tarayıcısız çalışır, uçtan uca
test gerçek Marketplace'in yapısına göre yazılmış yerel bir sahte sayfa kullanır (Chromium kurulu değilse atlanır).
Telegram bağlantısını denemek için: `python car_sniper.py --test`

## 7. Sunucuda 7/24 çalıştırmak

Mac kapalıyken de çalışması için bot bir Linux sunucuya (VPS) `systemd` servisi olarak kurulabilir.
Tek komutla kurulum, Telegram/Facebook kontrolü ve günlük kullanım: [deploy/README.md](deploy/README.md)
