#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
car_sniper.py - Facebook Marketplace araba "sniper" botu (Swoopa benzeri).

Facebook Marketplace aramalarını giriş yapmadan (misafir olarak) belirli
aralıklarla tarar, daha önce görülmemiş YENİ ilanları anında Telegram'a
fotoğraflı bildirim olarak gönderir.

Kurulum:
    pip install playwright requests
    python -m playwright install chromium

Çalıştırma:
    python car_sniper.py          # botu başlatır (durdurmak için Ctrl+C)
    python car_sniper.py --test   # sadece Telegram'a deneme mesajı gönderir
"""

import html
import json
import os
import random
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta

try:
    import requests
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from playwright.sync_api import sync_playwright
except ImportError as exc:
    sys.exit(
        f"Eksik kütüphane: {exc.name}\n"
        "Kurulum: pip install playwright requests && python -m playwright install chromium"
    )


# =============================================================================
# AYARLAR - genelde sadece bu bölümü düzenlemen yeterli
# =============================================================================

# Takip edilecek Marketplace arama linkleri (filtreleri ayarlayıp adres
# çubuğundan kopyaladığın linkler). İstediğin kadar ekleyebilirsin.
SEARCH_URLS = [
    "https://www.facebook.com/marketplace/istanbul/vehicles"
    "?minPrice=150000&maxPrice=600000&sortBy=creation_time_descend&exact=false",
    # "https://www.facebook.com/marketplace/ankara/vehicles?maxPrice=400000&sortBy=creation_time_descend&exact=false",
]

# Telegram bilgileri. Dosyaya yazabilir ya da aynı isimli ortam
# değişkenleriyle (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID) verebilirsin.
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "BURAYA_BOT_TOKEN_YAZ")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "BURAYA_CHAT_ID_YAZ")

BASE_INTERVAL_SECONDS = 180     # iki tarama turu arasındaki sabit bekleme
JITTER_SECONDS = (15, 45)       # sabit beklemeye eklenecek rastgele süre (min, max)
DELAY_BETWEEN_URLS = (5, 12)    # aynı tur içinde iki arama linki arası bekleme

SCROLL_STEPS = 3                # ilanların yüklenmesi için kaç kez aşağı kaydırılsın
HEADLESS = True                 # tarayıcı penceresini görmek istersen False yap
BROWSER_LOCALE = "tr-TR"        # IP'nin bulunduğu ülkeyle uyumlu olması iyi olur
BROWSER_TIMEZONE = "Europe/Istanbul"

# Hafıza dosyası script ile aynı klasörde tutulur.
SEEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seen_cars.json")
MAX_SEEN_IDS = 20000            # dosya sonsuza kadar büyümesin diye tutulacak en fazla ID

# Eşleşen ilan azsa Facebook listenin altına filtre dışı ilanlar ekler
# ("Results from outside your search"). Bu başlıktan sonraki ilanlar yok sayılır.
# Facebook'u başka bir dilde görüyorsan o dildeki başlığın bir parçasını ekle.
OUTSIDE_RESULTS_MARKERS = ["outside your search", "dışındaki sonuçlar"]


# =============================================================================
# SABİTLER
# =============================================================================

CARD_SELECTOR = "a[href*='/marketplace/item/']"
ITEM_ID_RE = re.compile(r"/marketplace/item/(\d+)")

_NUM = r"\d{1,3}(?:[.,\s]\d{3})+(?:[.,]\d{1,2})?|\d+(?:[.,]\d{1,2})?"
_SYMBOLS = "$€£₺¥₹₼"
_CODES = "TRY|TL|USD|EUR|GBP|CAD|AUD|AZN"
PRICE_TOKEN_RE = re.compile(
    rf"(?:[A-Z]{{1,3}})?[{_SYMBOLS}]\s?(?:{_NUM})"                   # $5,500  CA$5,500  ₺450.000
    rf"|(?<![A-Za-z])(?:{_CODES})\s?(?:{_NUM})"                     # TRY450.000
    rf"|(?:{_NUM})\s?(?:(?:{_CODES})(?![A-Za-z])|[{_SYMBOLS}])"     # 450.000 TL
)
FREE_WORDS = {"free", "ücretsiz", "bedava", "gratis"}

LOGIN_HINT_SELECTOR = 'input[name="email"], input[name="pass"], form[action*="login"], a[href*="/login"]'
CLOSE_BUTTON_SELECTOR = (
    '[aria-label="Close"], [aria-label="Kapat"], [aria-label="Schließen"], '
    '[aria-label="Fermer"], [aria-label="Cerrar"]'
)
COOKIE_BUTTON_RE = re.compile(
    r"Decline optional cookies|Only allow essential cookies|Allow all cookies"
    r"|İsteğe bağlı çerezleri reddet|Yalnızca gerekli çerezlere izin ver|Tüm çerezlere izin ver",
    re.IGNORECASE,
)

# Headless tarayıcının ele verdiği küçük izleri düzeltir.
STEALTH_JS = """
if (navigator.webdriver) {
  Object.defineProperty(Navigator.prototype, 'webdriver', { get: () => false });
}
if (!window.chrome) { window.chrome = { runtime: {} }; }
"""

# Login pop-up'ı "Kapat" ile kapanmazsa DOM'dan söker ve kaydırmayı geri açar.
REMOVE_LOGIN_DIALOG_JS = """
(loginHint) => {
  let removed = 0;
  document.querySelectorAll('div[role="dialog"]').forEach((dialog) => {
    if (!dialog.isConnected || !dialog.querySelector(loginHint)) return;
    // Arka plandaki karartma katmanıyla birlikte silmek için en dıştaki
    // sabit konumlu (ilan içermeyen) kapsayıcıya kadar çık.
    let target = dialog;
    for (let el = dialog.parentElement; el && el !== document.body; el = el.parentElement) {
      if (getComputedStyle(el).position === 'fixed' && !el.querySelector('a[href*="/marketplace/item/"]')) {
        target = el;
      }
    }
    target.remove();
    removed++;
  });
  if (removed) {
    document.documentElement.style.setProperty('overflow', 'auto', 'important');
    document.body.style.setProperty('overflow', 'auto', 'important');
  }
  return removed;
}
"""

# Tüm ilan kartlarını tek seferde okur (her kart için ayrı istek atmaktan çok daha hızlı).
EXTRACT_CARDS_JS = """
(anchors, markers) => {
  let boundary = null;
  if (markers.length) {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) {
      const text = walker.currentNode.nodeValue.trim().toLowerCase();
      if (text && markers.some((m) => text.includes(m))) {
        boundary = walker.currentNode.parentElement;
        break;
      }
    }
  }
  return anchors
    .filter((a) => !boundary || (boundary.compareDocumentPosition(a) & Node.DOCUMENT_POSITION_PRECEDING))
    .map((a) => {
      const img = a.querySelector('img');
      return {
        href: a.getAttribute('href') || '',
        text: a.innerText || '',
        img: img ? (img.currentSrc || img.getAttribute('src') || '') : '',
        alt: img ? (img.getAttribute('alt') || '') : '',
      };
    });
}
"""


# =============================================================================
# YARDIMCILAR
# =============================================================================

def log(message):
    print(f"[{datetime.now():%H:%M:%S}] {message}", flush=True)


def human_pause(min_seconds, max_seconds):
    time.sleep(random.uniform(min_seconds, max_seconds))


def short_url(url, limit=70):
    tail = url.split("facebook.com", 1)[-1]
    return tail if len(tail) <= limit else tail[: limit - 1] + "…"


def truncate(text, limit):
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def describe_error(exc):
    """Playwright hatalarının uzun 'Call log' kısmını atıp tek satırlık özet döner."""
    lines = str(exc).strip().splitlines()
    return f"{type(exc).__name__}: {lines[0] if lines else ''}"


@dataclass
class Listing:
    id: str
    title: str
    price: str
    details: str
    image_url: str
    url: str


# =============================================================================
# HAFIZA (seen_cars.json)
# =============================================================================

class SeenStore:
    """Görülen ilan ID'lerini ve sessizce hafızaya alınmış arama linklerini tutar.

    Bir arama linki ilk kez başarıyla tarandığında ilanları bildirim atılmadan
    kaydedilir. Böylece hem ilk çalıştırmada hem de SEARCH_URLS'e sonradan link
    eklendiğinde mesaj yağmuru olmaz.
    """

    def __init__(self, path):
        self.path = path
        self.ids = {}             # dict = sıralı küme (en eskiler başta)
        self.seeded_urls = set()
        self._load()

    def _load(self):
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path, encoding="utf-8") as f:
                raw = f.read().strip()
            data = json.loads(raw) if raw else {}
        except (OSError, ValueError) as exc:
            backup = self.path + ".bak"
            log(f"⚠️ {os.path.basename(self.path)} okunamadı ({exc}). "
                f"Yedeği {os.path.basename(backup)} olarak alındı, boş hafızayla başlanıyor.")
            try:
                os.replace(self.path, backup)
            except OSError:
                pass
            return
        if isinstance(data, list):        # sadece ID listesi içeren eski/elle yazılmış format
            data = {"seen_ids": data}
        self.ids = dict.fromkeys(str(i) for i in data.get("seen_ids", []))
        if self.ids:                      # ID yoksa her şey "ilk çalıştırma" sayılır
            self.seeded_urls = set(data.get("seeded_urls", []))

    @property
    def is_empty(self):
        return not self.ids

    def __len__(self):
        return len(self.ids)

    def __contains__(self, item_id):
        return item_id in self.ids

    def add(self, item_id):
        self.ids[item_id] = None

    def is_seeded(self, url):
        return url in self.seeded_urls

    def mark_seeded(self, url):
        self.seeded_urls.add(url)

    def save(self):
        if len(self.ids) > MAX_SEEN_IDS:
            self.ids = dict.fromkeys(list(self.ids)[-MAX_SEEN_IDS:])
        data = {"seeded_urls": sorted(self.seeded_urls), "seen_ids": list(self.ids)}
        tmp_path = self.path + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=1)
            os.replace(tmp_path, self.path)   # yarım yazılmış dosya kalmasın
        except OSError as exc:
            log(f"⚠️ Hafıza dosyası kaydedilemedi: {exc}")


# =============================================================================
# TELEGRAM
# =============================================================================

def telegram_configured():
    return ":" in TELEGRAM_BOT_TOKEN and bool(TELEGRAM_CHAT_ID) and not TELEGRAM_CHAT_ID.startswith("BURAYA")


def telegram_call(method, payload):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"
    for attempt in range(1, 4):
        try:
            data = requests.post(url, json=payload, timeout=20).json()
        except (requests.RequestException, ValueError) as exc:
            log(f"⚠️ Telegram'a ulaşılamadı ({method}, deneme {attempt}/3): "
                f"{str(exc).replace(TELEGRAM_BOT_TOKEN, '***')}")
            time.sleep(2 * attempt)
            continue
        if data.get("ok"):
            return True
        retry_after = (data.get("parameters") or {}).get("retry_after")
        if retry_after:                   # Telegram hız sınırı (429)
            log(f"⏳ Telegram hız sınırı, {retry_after} sn bekleniyor...")
            time.sleep(retry_after + 1)
            continue
        log(f"⚠️ Telegram hatası ({method}): {data.get('description')}")
        return False
    return False


def format_message(listing):
    esc = lambda s: html.escape(s, quote=False)
    return (
        "🚨 <b>YENİ FIRSAT ARABA DÜŞTÜ!</b>\n\n"
        f"🚗 <b>Başlık:</b> {esc(listing.title)}\n"
        f"💰 <b>Fiyat:</b> {esc(listing.price)}\n"
        f"📍 <b>Detay:</b> {esc(listing.details)}\n\n"
        f'🔗 <a href="{html.escape(listing.url)}">İlana Gitmek İçin Tıkla</a>'
    )


def notify(listing):
    """Bildirimi gönderir; başarılıysa True döner."""
    text = format_message(listing)
    if not telegram_configured():
        log("ℹ️ Telegram ayarlı değil, bildirim sadece konsola yazıldı.")
        return True
    if listing.image_url and telegram_call(
        "sendPhoto",
        {"chat_id": TELEGRAM_CHAT_ID, "photo": listing.image_url, "caption": text, "parse_mode": "HTML"},
    ):
        return True
    # Resim yoksa ya da Telegram resmi çekemediyse düz mesaj gönder.
    return telegram_call(
        "sendMessage",
        {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "link_preview_options": {"is_disabled": True},
        },
    )


# =============================================================================
# İLAN KARTI AYRIŞTIRMA
# =============================================================================

def _price_tokens(line):
    """Satır sadece fiyattan oluşuyorsa fiyatları döner (indirimde eski fiyat da gelir)."""
    if line.lower() in FREE_WORDS:
        return ["Ücretsiz"]
    tokens = [t.strip(" .,") for t in PRICE_TOKEN_RE.findall(line)]
    leftover = PRICE_TOKEN_RE.sub("", line).strip(" ·•|-")
    return tokens if tokens and not leftover else []


def parse_card(raw):
    match = ITEM_ID_RE.search(raw.get("href", ""))
    if not match:
        return None
    item_id = match.group(1)

    lines = []
    for line in raw.get("text", "").splitlines():
        line = " ".join(line.split())
        if line and line not in lines:
            lines.append(line)

    # Kart düzeni genelde: fiyat (+ üstü çizili eski fiyat), başlık, konum, kilometre.
    prices, title, details = [], "", []
    for line in lines:
        tokens = _price_tokens(line)
        if tokens and not title:
            prices.extend(tokens)
        elif not title:
            title = line
        else:
            details.append(line)

    if not prices:
        price = "Belirtilmemiş"
    elif len(prices) > 1 and prices[1] != prices[0]:
        price = f"{prices[0]} (eski fiyat: {prices[1]} 📉)"
    else:
        price = prices[0]

    image_url = raw.get("img", "")
    if image_url.startswith("data:"):
        image_url = ""

    return Listing(
        id=item_id,
        title=truncate(title or raw.get("alt", "").strip() or "Başlık bulunamadı", 150),
        price=truncate(price, 80),
        details=truncate(" • ".join(details) or "-", 300),
        image_url=image_url,
        url=f"https://www.facebook.com/marketplace/item/{item_id}/",
    )


# =============================================================================
# TARAYICI VE SAYFA İŞLEMLERİ
# =============================================================================

def build_user_agent(browser_version):
    """Gerçek Chromium sürümüyle ve işletim sistemiyle tutarlı bir User-Agent üretir."""
    major = (browser_version or "").split(".")[0] or "140"
    if sys.platform == "darwin":
        os_part = "Macintosh; Intel Mac OS X 10_15_7"
    elif sys.platform.startswith("win"):
        os_part = "Windows NT 10.0; Win64; x64"
    else:
        os_part = "X11; Linux x86_64"
    return (f"Mozilla/5.0 ({os_part}) AppleWebKit/537.36 (KHTML, like Gecko) "
            f"Chrome/{major}.0.0.0 Safari/537.36")


def launch_browser(playwright):
    options = {
        "headless": HEADLESS,
        "args": ["--disable-blink-features=AutomationControlled"],
        "ignore_default_args": ["--enable-automation"],
    }
    try:
        # "chromium" kanalı, tespit edilmesi daha zor olan yeni headless modunu kullanır.
        return playwright.chromium.launch(channel="chromium", **options)
    except Exception:
        return playwright.chromium.launch(**options)


def new_stealth_context(browser):
    context = browser.new_context(
        user_agent=build_user_agent(browser.version),
        viewport={"width": 1280, "height": 800},
        locale=BROWSER_LOCALE,
        timezone_id=BROWSER_TIMEZONE,
    )
    context.add_init_script(STEALTH_JS)
    context.set_default_timeout(30_000)
    return context


def handle_cookie_banner(page):
    try:
        button = page.get_by_role("button", name=COOKIE_BUTTON_RE).first
        if button.count() and button.is_visible():
            button.click(timeout=3_000)
            log("🍪 Çerez onay penceresi kapatıldı.")
            human_pause(0.8, 1.5)
    except Exception:
        pass   # çerez penceresi yoksa ya da kapanmadıysa tarama yine devam eder


def dismiss_login_popup(page):
    """Facebook'un 'Giriş Yap' pop-up'ını kapatır; kapanmazsa DOM'dan siler."""
    try:
        login_dialogs = page.locator('div[role="dialog"]').filter(has=page.locator(LOGIN_HINT_SELECTOR))
        if login_dialogs.count() == 0:
            return
        close_button = login_dialogs.first.locator(CLOSE_BUTTON_SELECTOR).first
        if close_button.count() and close_button.is_visible():
            close_button.click(timeout=3_000)
            page.wait_for_timeout(500)
        removed = page.evaluate(REMOVE_LOGIN_DIALOG_JS, LOGIN_HINT_SELECTOR)
        log("🔓 Giriş pop-up'ı " + ("DOM'dan silindi." if removed else "kapatıldı."))
    except Exception as exc:
        log(f"⚠️ Giriş pop-up'ı kapatılamadı: {describe_error(exc)}")


def is_login_wall(page):
    if "/login" in page.url or "/checkpoint" in page.url:
        return True
    try:
        return page.locator('form#login_form, input[name="pass"]').count() > 0
    except Exception:
        return False


def scrape_search(page, url):
    """Bir arama sayfasını açar ve üzerindeki ilanları döner."""
    page.goto(url, wait_until="domcontentloaded", timeout=60_000)
    human_pause(2, 4)
    handle_cookie_banner(page)
    dismiss_login_popup(page)

    try:
        page.wait_for_selector(CARD_SELECTOR, timeout=20_000)
    except PlaywrightTimeoutError:
        if is_login_wall(page):
            log("🚫 Facebook giriş duvarı gösterdi (misafir erişimi engellendi). Bu link bu turda atlanıyor.")
        else:
            log("⚠️ Sayfada ilan kartı bulunamadı (sonuç yok ya da sayfa yapısı değişmiş olabilir).")
        return []

    for _ in range(SCROLL_STEPS):
        page.evaluate("dy => window.scrollBy({top: dy, behavior: 'smooth'})", random.randint(700, 1200))
        human_pause(1.2, 2.5)
        dismiss_login_popup(page)

    raw_cards = page.eval_on_selector_all(
        CARD_SELECTOR, EXTRACT_CARDS_JS, [m.lower() for m in OUTSIDE_RESULTS_MARKERS]
    )
    listings, ids = [], set()
    for raw in raw_cards:
        try:
            listing = parse_card(raw)
        except Exception as exc:
            log(f"⚠️ Bir ilan kartı ayrıştırılamadı, atlanıyor: {exc}")
            continue
        if listing and listing.id not in ids:
            ids.add(listing.id)
            listings.append(listing)
    return listings


# =============================================================================
# ANA DÖNGÜ
# =============================================================================

def process_listings(store, url, listings, first_run):
    """Yeni ilanları bildirir; daha önce hiç taranmamış linkleri sessizce hafızaya alır."""
    if not store.is_seeded(url):
        for listing in listings:
            store.add(listing.id)
        store.mark_seeded(url)
        store.save()
        if not first_run:
            log(f"🆕 Yeni arama linki sessizce hafızaya alındı: {len(listings)} ilan ({short_url(url)})")
        return

    new_listings = [l for l in listings if l.id not in store]
    log(f"🔍 {short_url(url)} → {len(listings)} ilan tarandı, {len(new_listings)} yeni.")
    for listing in new_listings:
        log(f"🚨 YENİ İLAN: {listing.title} | {listing.price} | {listing.url}")
        if notify(listing):
            store.add(listing.id)
            store.save()
        else:
            log("⚠️ Bildirim gönderilemedi, ilan bir sonraki turda tekrar denenecek.")
        time.sleep(1)   # Telegram hız sınırına takılmamak için


def run_cycle(store):
    first_run = store.is_empty
    if first_run:
        log("🆕 İlk çalıştırma: mevcut ilanlar bildirim atılmadan hafızaya alınacak.")

    with sync_playwright() as playwright:
        browser = launch_browser(playwright)
        try:
            page = new_stealth_context(browser).new_page()
            for index, url in enumerate(SEARCH_URLS):
                if index:
                    human_pause(*DELAY_BETWEEN_URLS)
                try:
                    listings = scrape_search(page, url)
                except Exception as exc:
                    log(f"❌ Arama sayfası taranamadı ({short_url(url)}): {describe_error(exc)}")
                    continue
                if listings:
                    process_listings(store, url, listings, first_run)
        finally:
            try:
                browser.close()
            except Exception:
                pass

    if first_run:
        if store.is_empty:
            log("⚠️ İlk taramada hiç ilan bulunamadı, bir sonraki turda tekrar denenecek.")
        else:
            log(f"✅ İlk tarama tamamlandı, {len(store)} adet mevcut ilan hafızaya alındı. "
                "Şimdi yeni düşecek ilanlar bekleniyor...")


def send_test_message():
    if not telegram_configured():
        sys.exit("TELEGRAM_BOT_TOKEN ve TELEGRAM_CHAT_ID ayarlanmamış.")
    sample = Listing(
        id="0",
        title="2015 Volkswagen Golf 1.6 TDI (TEST)",
        price="₺450.000 (eski fiyat: ₺500.000 📉)",
        details="İstanbul • 120 bin km",
        image_url="",
        url="https://www.facebook.com/marketplace/",
    )
    ok = notify(sample)
    log("✅ Deneme mesajı gönderildi." if ok else "❌ Deneme mesajı gönderilemedi.")
    sys.exit(0 if ok else 1)


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")   # emoji desteklemeyen konsollarda çökmesin
        except Exception:
            pass

    if "--test" in sys.argv:
        send_test_message()
    if not SEARCH_URLS:
        sys.exit("SEARCH_URLS listesi boş. En az bir Marketplace arama linki ekle.")

    log(f"🚗 Car Sniper başladı. {len(SEARCH_URLS)} arama linki takip ediliyor.")
    if not telegram_configured():
        log("⚠️ Telegram ayarlı değil; yeni ilanlar sadece konsola yazılacak.")

    store = SeenStore(SEEN_FILE)
    cycle = 0
    try:
        while True:
            cycle += 1
            log(f"🔄 Tarama #{cycle} başlıyor...")
            try:
                run_cycle(store)
            except Exception as exc:
                log(f"❌ Tarama #{cycle} sırasında hata: {describe_error(exc)}")
            wait = BASE_INTERVAL_SECONDS + random.uniform(*JITTER_SECONDS)
            next_at = datetime.now() + timedelta(seconds=wait)
            log(f"⏳ Sonraki tarama {int(wait)} sn sonra ({next_at:%H:%M:%S}).")
            time.sleep(wait)
    except KeyboardInterrupt:
        log("👋 Bot durduruldu.")


if __name__ == "__main__":
    main()
