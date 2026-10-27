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
- Arama linki: `https://www.facebook.com/marketplace/110843235610039/vehicles?sortBy=creation_time_descend&exact=false`
  (kullanıcının seçimi, 27.10.2026: Lummen = Beringen'in yanı, Facebook'un varsayılan 65 km çapı). Konumsuz linkte
  misafire San Francisco ilanları gelir. `/cars/` sayfası `sortBy`'ı **yok sayıyor** (en üstte saatler/günler önceki
  ilanlar, "Sort by" etiketi yok), `topLevelVehicleType=car_truck` bir şey filtrelemiyor; bu yüzden vehicles +
  kelime filtresi. `sortBy=creation_time_descend` şart; sayfada "Sort by: Date listed: Newest first" görünmeli.
- **Araba olmayanlar:** başlığı `NOT_A_CAR_WORDS`'teki bir kelimeyle başlayan ilan (`Jantes BBS`, `4 pneus hiver`,
  `Remorque`, `Moteur vw polo`, `Mobylette`) `⏭️ Atlandı (araba değil: jantes)` olur. Sadece başlığın başına bakılır
  ("Opel Astra, nieuwe banden" elenmez); başlıksız kartta sayfadaki başlıkla kontrol edilir (kullanıcının seçimi).

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
- **Km:** öncelik `Driven X km` alanı > sayfadaki gizli `vehicle_odometer_data` > karttaki km > başlık + açıklamadaki
  **en büyük** km. Misafire "Driven" gösterilmez; gizli veri sadece ilanın tırnaklı ID'sinin geçtiği script'ten
  okunur, mil ise km'ye çevrilir. `150k`, `230dkm`, `185.000`, `98 000`, `240.xxx` biçimleri tanınır; 1000'den
  küçük değerler mesafe sayılıp alınmaz. `KM_BEFORE_RE`'de binlik ekinden sonra harf gelemez ("km"nin k'si).
- **Başlık:** Belçika'da kartların çoğu başlıksız; resim alt metni "<başlık> in <konum>" olduğu için sadece
  " in <konum>" kalan alt metin başlık sayılmaz. Kartta başlık yoksa ilan sayfasının `og:title`'ı kullanılır.
- Açıklamadan `Condition`/`Used - Good`, satır sonu `See less`, `... · Location is approximate` ve `￼` atılır.
- İlan sayfaları **ayrı sekmede** açılıp kapatılır: aynı sekmede başarısız bir yükleme sonraki `goto`'ları
  "interrupted by another navigation" hatasıyla zincirleme bozuyordu.
- Tarayıcı: `--disable-blink-features=AutomationControlled`, 1280x800, `channel="chromium"` (yeni headless; olmazsa
  normal). User-Agent gerçek Chromium sürümünden ve işletim sisteminden **üretilir**, sabit UA yazma.
  `BROWSER_LOCALE = "en-US"`: kod İngilizce metinleri tanır ("Allow all cookies", "See more", "Driven",
  "About this vehicle"). Dili değiştirirsen bu metinlerin karşılıklarını da ekle. Saat dilimi `Europe/Brussels`.
- **Çerez penceresi** sayfadan ~1 sn sonra gelir ve login pop-up'ının üstünde durur: önce o beklenir
  (`handle_cookie_banner(page, wait_ms=5_000)`) ve kaydırırken tekrar kontrol edilir. "Decline optional cookies"
  DOM'da önce geldiği için o seçilir; gerçek DOM'daki `aria-hidden` kopya butonları `get_by_role` atlar.
- Login pop-up: önce `aria-label="Close"` butonu (tıklama başarısız olsa da devam edilir), sonra diyalog en dıştaki
  sabit konumlu kapsayıcısıyla DOM'dan silinir ve sayfa kaydırması geri açılır.
- Yeni Chromium'un ilk isteği turlar arası beklemeden sonra ara sıra `net::ERR_NAME_NOT_RESOLVED` verir; arama
  sayfası `net::ERR_` hatasında bir kez tekrar denenir. Taranan konum `📍 Taranan konum: ...` diye loglanır.
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

- `test_parsing.py` saniyeler içinde biter. `test_e2e_mock.py` ~55 sn sürer, Chromium yoksa kendini atlar.
  pytest kurulu değil; testler `unittest` ile çalışır.
- Uçtan uca test gerçek Facebook'a ve Telegram'a **gitmez**: arama sayfası yerel HTTP sunucusundan, ilan sayfaları
  Playwright `route` ile sahte HTML'den gelir. Sahte sayfalar Ekim 2026'daki gerçek yapıya göre: geç gelen ve Close
  tıklamasını engelleyen çerez penceresi (gizli kopya butonlarla), açılışta ve kaydırınca gelen kapanmayan login
  pop-up'ı, ilk istekte DNS hatası, konum butonu, " in <konum>" alt metinleri, kaydırınca yüklenen ilan, filtre dışı
  sonuçlar, satır içi "See more", gizli km JSON'u ve "Today's picks" tuzakları.
- Telegram'ın gerçekten çalıştığını denemek için `python3 car_sniper.py --test` (telefona deneme mesajı gider).
- Ayrıştırma ya da filtre mantığını değiştirince önce ilgili testi güncelle/ekle, sonra tüm testleri çalıştır.
- Facebook'un gerçek sayfa yapısıyla ilgili bir şüphede: `HEADLESS = False` ile çalıştırıp bak; gerekirse
  `page.content()` çıktısını kaydedip incele. Gerçek DOM'a göre değişiklik yapınca sahte test sayfalarını da
  aynı yapıya yaklaştır.

## Açık konular

### Durum (27.10.2026, dal `claude/marketplace-connection-tests-df4fae`, `main`'e alınmadı)

Bot gerçek Facebook Marketplace'te (misafir, kullanıcının Mac'inden) ve gerçek Telegram'la uçtan uca doğrulandı:
arama sayfası, ilan sayfası okuma, yıl/km/fiyat/"araba değil" filtreleri ve Telegram mesajı (`--test` ve gerçek
ilan: "Alfa Romeo 159 €1,750" telefona gitti). Bulgular yukarıdaki iş kuralları ve tasarım kararlarına işlendi.
Gerçek ilanlarda doğru elenenler: Laguna 2011/230.000 km, Zafira 2013/200.500 km, 2005 Corsa, BMW 525d 2010/
240.000 km, jant/lastik/römork/motor/moped/scooter ilanları. Testler: 29 test, hepsi geçiyor.

**Kalan işler:**
1. Dalı `main`'e al: ana klasörde `git merge claude/marketplace-connection-tests-df4fae`.
2. `seen_cars.json` bu worktree'de deneme turlarından kaldı (gitignore'da). Botu ana klasörde çalıştırınca orada
   yeni hafıza oluşur, ilk tur yine sessizdir.
3. İzlenecek: misafir akışında ilanlar dakikalar içinde düşüyor mu (17:27'de en yeni ilan 11 dk önceydi). Telegram'a
   uzun süre hiç ilan gelmezse önce logda `🔍 ... X yeni` sayılarına, sonra sayfada "Sort by" etiketine bak.
   Araba olmayan ilan gelirse başlığın ilk kelimesini `NOT_A_CAR_WORDS`'e ekle (önce kullanıcıya sor).

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
