"""Uçtan uca test: yerel sahte Marketplace sunucusu + gerçek Chromium.

Gerçek Facebook'a gidilmez. Arama sayfası yerel bir HTTP sunucusundan, ilan sayfaları
(https://www.facebook.com/marketplace/item/...) Playwright route ile sahte HTML'den gelir.
Chromium kurulu değilse (python -m playwright install chromium) test atlanır.
"""

import html
import json
import os
import re
import sys
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import car_sniper as cs  # noqa: E402

REAL_SLEEP = time.sleep

# id: (kart metni, ilan sayfası başlığı, "Driven" satırı, açıklama)
NEW_LISTINGS = {
    1:  ("€1,500\nGenk, VLG",                 "Opel Astra", "", "Bouwjaar 2012, 150.000 km, gekeurd voor verkoop."),
    2:  ("€1\nGenk, VLG",                     "", "", ""),
    3:  ("€1,234\nGenk, VLG",                 "", "", ""),
    4:  ("Free\nGenk, VLG",                   "", "", ""),
    5:  ("€2,500\n2015 Golf\nGenk, VLG",      "", "", ""),
    6:  ("Just listed\n€1,800\nHasselt, VLG", "2006 Opel Corsa", "", "Rijdt perfect, nieuwe banden."),
    7:  ("€900\nGenk, VLG",                   "Peugeot 206", "Driven 245,000 km", "Distributie vervangen bij 150.000 km."),
    8:  ("€1,200\nLeopoldsburg, VLG",         "", "", ""),
    9:  ("€1,700\nMechelen, VLG",             "BROKEN", "", ""),   # ilan sayfası açılamaz
    10: ("€1,950\n2007 VW Golf\nGenk, VLG",   "", "", "Netjes"),
    11: ("€1,600\nZoersel, VLG",              "Toyota Yaris", "",
         "Veel info " * 20 + "kilometerstand: 99.000, bj 2011."),   # bilgi "See more" arkasında
}
EXPECTED_SENT = [1, 8, 9, 11]


def card_html(item_id, text):
    spans = "".join(f"<div><span>{html.escape(line)}</span></div>" for line in text.split("\n"))
    return (f'<div style="height:300px"><a href="/marketplace/item/{item_id}/?ref=search">'
            f'<img src="https://scontent.example/{item_id}.jpg" alt="">{spans}</a></div>')


def search_html(extra_ids):
    cards = [card_html(i, NEW_LISTINGS[i][0]) for i in extra_ids]
    cards += [card_html(1000 + i, f"€{1000 + i}\n2012 Model {i}\nGenk, VLG") for i in range(8)]
    outside = "".join(card_html(9000 + i, "€500\nOutside\nAnkara, TR") for i in range(3))
    lazy = card_html(7777, "€999\nLazy Car\nGenk, VLG")
    return f"""<!doctype html><html><head><meta charset="utf-8">
<style>#lw{{position:fixed;inset:0;background:rgba(0,0,0,.7)}}</style></head><body>
<div role="dialog" id="cookie"><div role="button" onclick="this.parentElement.remove()">Allow all cookies</div></div>
<div role="main">{''.join(cards)}<div id="lazy"></div>
<h2>Results from outside your search</h2>{outside}</div>
<script>
let shown = false, loaded = false;
window.addEventListener('scroll', () => {{
  if (!loaded && scrollY > 500) {{ loaded = true; document.getElementById('lazy').innerHTML = {json.dumps(lazy)}; }}
  if (!shown && scrollY > 200) {{
    shown = true;
    const w = document.createElement('div'); w.id = 'lw';   // kapat butonu çalışmayan login pop-up'ı
    w.innerHTML = '<div role="dialog"><div role="button" aria-label="Close">X</div>'
                + '<form action="/login/"><input name="email"><input name="pass"></form></div>';
    document.body.appendChild(w); document.body.style.overflow = 'hidden';
  }}
}});
</script></body></html>"""


def listing_html(item_id):
    _, title, driven, description = NEW_LISTINGS[item_id]
    short = description[:120]
    about = (f"<div><div><span>About this vehicle</span></div><div><span>{driven}</span>"
             f"<span>Manual transmission</span></div></div>") if driven else ""
    see_more = (f'<div role="button" data-full="{html.escape(description)}" '
                f'onclick="document.getElementById(\'d\').textContent=this.dataset.full; this.remove()">See more</div>'
                if len(description) > 120 else "")
    seller = (f"<div><div><span>Seller's description</span></div>"
              f"<div><span id='d'>{html.escape(short)}</span>{see_more}</div></div>") if description else ""
    # Sayfanın altındaki önerilen ilanlar: buradaki yıl/km asla ilana karışmamalı.
    picks = ("<div><h2>Today's picks</h2><a href='/marketplace/item/5555/'><span>2001 Fiat Punto</span>"
             "<span>250.000 km</span></a><div><span>Description</span></div><div>Oldtimer 1985, 300.000 km</div></div>")
    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(short)}">
</head><body><div role="main"><h1>{html.escape(title)}</h1>{about}{seller}</div>{picks}</body></html>"""


class MockMarketplaceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as playwright:
                cs.launch_browser(playwright).close()
        except Exception as exc:
            raise unittest.SkipTest(f"Chromium başlatılamadı: {exc}")

        cls.extra_ids = []
        test = cls

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                body = search_html(test.extra_ids).encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.seen_file = os.path.join(self.tmp.name, "seen_cars.json")
        self.sent = []
        original_context = cs.new_stealth_context

        def context_with_routes(browser):
            context = original_context(browser)
            context.route("https://www.facebook.com/**", self.fake_facebook)
            return context

        patches = [
            mock.patch.object(cs, "new_stealth_context", context_with_routes),
            mock.patch.object(cs, "human_pause", lambda a, b: REAL_SLEEP(0.3)),
            mock.patch.object(cs, "telegram_call", lambda method, payload: self.sent.append(payload) or True),
            mock.patch.object(cs, "TELEGRAM_BOT_TOKEN", "123:TEST"),
            mock.patch.object(cs, "TELEGRAM_CHAT_ID", "42"),
            mock.patch.object(cs, "SEARCH_URLS", [self.base + "/marketplace/category/vehicles?sortBy=creation_time_descend"]),
        ]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)
        self.addCleanup(self.tmp.cleanup)

    @staticmethod
    def fake_facebook(route):
        item_id = int(re.search(r"/item/(\d+)", route.request.url).group(1))
        if NEW_LISTINGS.get(item_id, ("", ""))[1] == "BROKEN":
            return route.abort()
        route.fulfill(status=200, content_type="text/html; charset=utf-8", body=listing_html(item_id))

    def run_cycle(self):
        cs.run_cycle(cs.SeenStore(self.seen_file))
        with open(self.seen_file, encoding="utf-8") as f:
            return json.load(f)

    def sent_ids(self):
        return sorted(int(re.search(r"/item/(\d+)/", p["caption"]).group(1)) for p in self.sent)

    def test_full_flow(self):
        # 1. tur: ilk çalıştırma -> hiçbir şey gönderilmez, filtre dışı ilanlar hafızaya alınmaz
        type(self).extra_ids = []
        data = self.run_cycle()
        self.assertEqual(self.sent, [])
        self.assertIn("7777", data["seen_ids"], "kaydırınca yüklenen ilan yakalanmalı")
        self.assertFalse(any(i.startswith("900") for i in data["seen_ids"]), "filtre dışı ilanlar alınmamalı")

        # 2. tur: yeni ilanlar fiyat ve yıl/km filtresinden geçer
        type(self).extra_ids = list(NEW_LISTINGS)
        data = self.run_cycle()
        self.assertEqual(self.sent_ids(), EXPECTED_SENT)
        by_id = {int(re.search(r"/item/(\d+)/", p["caption"]).group(1)): p["caption"] for p in self.sent}
        self.assertIn("Yıl:</b> 2012   🛣 <b>KM:</b> 150.000", by_id[1])
        self.assertIn("Yıl:</b> 2011   🛣 <b>KM:</b> 99.000", by_id[11])
        self.assertIn("Yıl:</b> bilinmiyor", by_id[8])
        self.assertTrue(all("1985" not in c and "Fiat" not in c for c in by_id.values()))
        self.assertEqual(self.sent[0]["photo"], "https://scontent.example/1.jpg")
        self.assertTrue(all(str(i) in data["seen_ids"] for i in NEW_LISTINGS), "elenenler de hafızaya alınmalı")

        # 3. tur: yeni bir şey yok
        self.sent.clear()
        self.run_cycle()
        self.assertEqual(self.sent, [])

        # 4. tur: SEARCH_URLS'e yeni link eklenince sessizce hafızaya alınır
        cs.SEARCH_URLS.append(self.base + "/marketplace/category/cars?sortBy=creation_time_descend")
        data = self.run_cycle()
        self.assertEqual(self.sent, [])
        self.assertEqual(len(data["seeded_urls"]), 2)


if __name__ == "__main__":
    unittest.main()
