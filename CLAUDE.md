# marketplace-scraper: Car Sniper

Facebook Marketplace'e düşen ucuz araba ilanlarını yakalayıp Telegram'a bildiren, Swoopa benzeri
tek dosyalık bir bot (`car_sniper.py`). Facebook'a **giriş yapmadan (misafir olarak)** Playwright ile tarar.

- Kullanıcı **Belçika'da** (Beringen, Limburg), botu **kendi Mac'inde** çalıştırıyor. Facebook arayüzü İngilizce,
  ilan açıklamaları çoğunlukla Flamanca/Fransızca, fiyatlar `€1,500` biçiminde.
- Kullanıcıyla **Türkçe** konuş. Koddaki yorumlar, loglar ve Telegram mesajları da Türkçe.
- Amaç "car flipping": yeni düşen, ucuz, çok eski/çok km'li olmayan arabayı herkesten önce görmek.

## Çalıştırma

```bash
pip3 install -r requirements.txt
python3 -m playwright install chromium

export TELEGRAM_BOT_TOKEN="..."      # ~/.zshrc içinde tanımlı; koda YAZMA (bkz. Gizli bilgiler)
export TELEGRAM_CHAT_ID="..."

python3 car_sniper.py --test         # Telegram'a deneme mesajı
python3 car_sniper.py                # botu başlatır (Ctrl+C ile durur)
```

Tarayıcıyı görmek ya da Facebook'un ne gösterdiğini incelemek için `HEADLESS = False` yap.

## Dosyalar

| Dosya | Ne |
|---|---|
| `car_sniper.py` | Botun tamamı. En üstteki "AYARLAR" bölümü kullanıcının değiştirdiği yer |
| `tests/test_parsing.py` | Tarayıcısız birim testleri (kart ayrıştırma, fiyat/yıl/km filtreleri, hafıza) |
| `tests/test_e2e_mock.py` | Sahte Marketplace sunucusu + gerçek Chromium ile uçtan uca test |
| `seen_cars.json` | Çalışma anında oluşan hafıza (gitignore'da). `{"seeded_urls": [...], "seen_ids": [...]}` |
| `requirements.txt` | `playwright`, `requests` |

## Akış

```
main()  → her tur: run_cycle()  → bekle (180 sn + 15-45 sn rastgele)
run_cycle(store)                   her turda yeni Chromium (crash'e dayanıklı, temiz misafir oturumu)
  └ her SEARCH_URL için scrape_search(page, url)
      goto → handle_cookie_banner → dismiss_login_popup → kaydır (SCROLL_STEPS)
      → EXTRACT_CARDS_JS (tüm kartlar tek seferde) → parse_card() → Listing
  └ process_listings(store, page, url, listings, first_run)
      link ilk kez taranıyorsa: sessizce hafızaya al (mesaj yok)
      değilse her yeni ID için evaluate_listing():
        price_rejection()                        fiyat filtresi (sayfa açmadan)
        apply_vehicle_info(listing)              karttaki yıl/km → vehicle_rejection()
        read_listing_page(context, url)          ilan sayfası AYRI SEKMEDE açılır
        apply_vehicle_info(listing, page_data)   → vehicle_rejection()
      elenmediyse notify(): sendPhoto, olmazsa sendMessage
```

## Kullanıcının iş kuralları

Bunlar kullanıcının açıkça istediği davranışlar. **Değiştirmeden önce kullanıcıya sor.**

- **İlk çalıştırma spam yapmaz.** `seen_cars.json` yoksa ya da boşsa mevcut ilanlar sessizce kaydedilir ve
  "İlk tarama tamamlandı, X adet mevcut ilan hafızaya alındı..." yazılır. `SEARCH_URLS`'e sonradan eklenen
  link de ilk taramasında sessizce hafızaya alınır (`seeded_urls`).
- **Fiyat:** Free/0 € atlanır. `MIN_PRICE` (100) altı ve `FAKE_PRICES` (123, 1234, 12345) sahte sayılır.
  `MAX_PRICE` (2000) üstü atlanır, 2000 dahil gönderilir. Fiyatı okunamayan ilan elenmez.
- **Yıl/km:** Yıl ≤ `SKIP_YEAR_AT_OR_BELOW` (2008) ya da km > `SKIP_KM_ABOVE` (200.000) ise gönderilmez.
- **Şüphede gönder (fail-open):** Eksik bilgi tek başına asla eleme sebebi değildir. Yıl/km bulunamazsa ya da
  ilan sayfası açılamazsa ilan gönderilir ("bilinmiyor"). Kaçan fırsat, fazladan mesajdan daha kötü.
- Elenen ilanlar sebebiyle loglanır (`⏭️ Atlandı (2006 model)`) ve seen sayılır. Telegram'a **gönderilemeyen**
  ilan seen sayılmaz, sonraki turda tekrar denenir.
- Arama linki: `https://www.facebook.com/marketplace/category/vehicles?sortBy=creation_time_descend&exact=false`
  (kullanıcının seçimi; "vehicles" motosiklet/römork da içerir). `sortBy=creation_time_descend` şart.

## Tasarım kararları ve tuzaklar

- **Facebook'un CSS sınıf adları anlamsız ve sürekli değişir.** Seçicilerde sadece `a[href*='/marketplace/item/']`,
  `role`, `aria-label`, `meta` etiketleri ve görünen metin kullan.
- **Kart metni düzeni** (`innerText` satırları): `[etiket ("Just listed")] fiyat [+ eski fiyat aynı satırda] başlık konum km`.
  Fiyattan önceki satırlar etikettir. Belçika'da başlıksız kart çok yaygın (sadece fiyat + konum); ilk satır
  `LOCATION_RE`'ye uyuyorsa ve sonrasında sadece km varsa başlık yok sayılır.
- Facebook eşleşme az olunca "Results from outside your search" başlığı altına filtre dışı ilanlar ekler; bu başlıktan
  sonraki kartlar alınmaz (`OUTSIDE_RESULTS_MARKERS`).
- **İlan sayfasında önerilen başka ilanlar var ("Today's picks").** Sayfanın genel metnini ya da genel "Description"
  başlığını okuma; başka ilanın yılı/km'si karışır. `DESCRIPTION_HEADINGS` sadece ilana özgü başlıklar ve her
  başlığın yalnızca **ilk** geçişi alınır. Testte bunun için tuzak var.
- **Yıl:** önce başlıklar (kart + `og:title`), yoksa açıklama; birden fazlaysa **en küçüğü** (sonrakiler genelde
  muayene/bakım yılı). Arkasından km/cc/€ gelen 4 haneli sayılar yıl sayılmaz.
- **Km:** öncelik `Driven X km` alanı > karttaki km > açıklamadaki **en büyük** km. `150k`, `230dkm`, `185.000`,
  `98 000` biçimleri tanınır; 1000'den küçük değerler mesafe sayılıp alınmaz.
- İlan sayfaları **ayrı sekmede** açılıp kapatılır: aynı sekmede başarısız bir yükleme sonraki `goto`'ları
  "interrupted by another navigation" hatasıyla zincirleme bozuyordu.
- Tarayıcı: `--disable-blink-features=AutomationControlled`, 1280x800, `channel="chromium"` (yeni headless; olmazsa
  normal). User-Agent gerçek Chromium sürümünden ve işletim sisteminden **üretilir**, sabit UA yazma.
  `BROWSER_LOCALE = "en-US"`: kod İngilizce metinleri tanır ("Allow all cookies", "See more", "Driven",
  "About this vehicle"). Dili değiştirirsen bu metinlerin karşılıklarını da ekle. Saat dilimi `Europe/Brussels`.
- Login pop-up: önce `aria-label="Close"` butonu, olmazsa diyalog en dıştaki sabit konumlu kapsayıcısıyla DOM'dan
  silinir ve sayfa kaydırması geri açılır.
- **Telegram:** HTML parse mode, kullanıcı metinleri `html.escape`'li. Fotoğraf açıklaması en fazla 1024 görünür
  karakter; `truncate` sınırları (başlık 150, fiyat 80, detay 150, açıklama 350) buna göre. 429'da `retry_after`
  kadar beklenir. Hata loglarında token `***` ile maskelenir.
- **Çökmeme:** her arama linki ve her tur `try/except` içinde; hatalar `describe_error()` ile tek satır loglanır.
  Hafıza dosyası atomik yazılır (`.tmp` + `os.replace`), bozuksa `.bak` alınıp boş başlanır.
- **Python 3.9 uyumlu kal** (macOS'un sistem Python'u): `X | None` yerine `Optional`, `match` yok.
- Loglar `log()` ile `[HH:MM:SS]` damgalı ve emojili; yeni loglar da bu biçimde ve Türkçe olsun.

## Gizli bilgiler

Repo **herkese açık (public)**. Telegram bot token'ını asla koda, commit'e, README'ye ya da test dosyasına yazma.
Token ve chat ID ortam değişkeninden okunur (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`); koddaki
`BURAYA_...` değerleri yer tutucudur. `seen_cars.json` gitignore'da kalmalı.

## Test

```bash
python3 -m unittest discover -s tests -v
```

- `test_parsing.py` saniyeler içinde biter. `test_e2e_mock.py` ~40 sn sürer, Chromium yoksa kendini atlar.
- Uçtan uca test gerçek Facebook'a **gitmez**: arama sayfası yerel HTTP sunucusundan, ilan sayfaları Playwright
  `route` ile sahte HTML'den gelir. Sahte sayfalarda cookie penceresi, kapanmayan login pop-up'ı, kaydırınca
  yüklenen ilan, filtre dışı sonuçlar, "See more" ve "Today's picks" tuzağı var.
- Ayrıştırma ya da filtre mantığını değiştirince önce ilgili testi güncelle/ekle, sonra tüm testleri çalıştır.
- Facebook'un gerçek sayfa yapısıyla ilgili bir şüphede: `HEADLESS = False` ile çalıştırıp bak; gerekirse
  `page.content()` çıktısını kaydedip incele. Gerçek DOM'a göre değişiklik yapınca sahte test sayfalarını da
  aynı yapıya yaklaştır.

## Açık konular

- **İlan sayfası okuma gerçek Facebook'ta henüz doğrulanmadı** (geliştirildiği ortamdan facebook.com'a erişim
  yoktu). Telegram mesajlarında yıl/km hep "bilinmiyor" geliyorsa `LISTING_DETAILS_JS` ve `DESCRIPTION_HEADINGS`
  gerçek ilan sayfasına göre güncellenmeli. Kart ayrıştırması kullanıcının ekran görüntüsüne göre doğrulandı.
- "vehicles" kategorisi motosiklet/römork da getiriyorsa "Cars" alt kategorisine geçmek gerekebilir.

## Git

- Kullanıcı `main` dalında çalışıyor. Commit mesajları İngilizce, kısa başlık + ne/neden açıklaması.
- Push etmeden önce testleri çalıştır.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.
