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

1. `facebook.com/marketplace` → sol menüden **Araçlar (Vehicles)** kategorisine gir.
2. **Konum**: Şehrini seç. Misafir modunda konumu linkteki şehir kısmı belirler
   (`/marketplace/istanbul/vehicles`).
3. **Filtreler**: Minimum/maksimum fiyat, yıl, marka, kilometre gibi filtreleri ayarla.
4. **Sırala (Sort by)** → **Tarih: Önce en yeni (Date listed: Newest first)** seç.
   Linkte `sortBy=creation_time_descend` görünmeli. Bu ayar **çok önemli**: en yeni ilanlar
   en üstte olmazsa bot yeni ilanları geç görür.
5. Adres çubuğundaki linkin tamamını kopyalayıp `SEARCH_URLS` listesine ekle.
6. Linki **gizli pencerede (giriş yapmadan)** açıp ilanların göründüğünü kontrol et.
   Bot da sayfayı bu şekilde görür.

Örnek link:

```
https://www.facebook.com/marketplace/category/vehicles?sortBy=creation_time_descend&exact=false
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

Testler gerçek Facebook'a bağlanmaz: ayrıştırma/filtre testleri tarayıcısız çalışır, uçtan uca test
yerel bir sahte Marketplace sayfası kullanır (Chromium kurulu değilse atlanır).
