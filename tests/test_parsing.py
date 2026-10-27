"""Tarayıcı ve ağ gerektirmeyen testler: kart ayrıştırma, fiyat ve yıl/km filtreleri, hafıza dosyası."""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import car_sniper as cs  # noqa: E402


def card(text, alt=""):
    return cs.parse_card({"href": "/marketplace/item/42/?ref=search", "text": text, "img": "", "alt": alt})


class ParseCardTests(unittest.TestCase):
    def test_full_card(self):
        listing = card("€1,500\n2012 VW Polo 1.2\nGenk, VLG\n185K km")
        self.assertEqual(listing.id, "42")
        self.assertEqual(listing.title, "2012 VW Polo 1.2")
        self.assertEqual(listing.price, "€1,500")
        self.assertEqual(listing.price_value, 1500.0)
        self.assertEqual(listing.details, "Genk, VLG • 185K km")
        self.assertEqual(listing.url, "https://www.facebook.com/marketplace/item/42/")

    def test_badge_before_price_is_ignored(self):
        listing = card("Just listed\n€1,500\nHerstal, WAL")
        self.assertEqual(listing.price, "€1,500")
        self.assertEqual(listing.details, "Herstal, WAL")
        self.assertTrue(listing.title.startswith("Başlık yok"))

    def test_location_only_card_has_no_title(self):
        listing = card("€3,100\nLeopoldsburg, VLG")
        self.assertTrue(listing.title.startswith("Başlık yok"))
        self.assertEqual(listing.details, "Leopoldsburg, VLG")

    def test_title_with_comma_is_still_title(self):
        listing = card("€8,900\n2017 Opel Corsa, zeer proper\nGenk, VLG")
        self.assertEqual(listing.title, "2017 Opel Corsa, zeer proper")

    def test_price_drop_shows_old_price(self):
        listing = card("€1,800€2,100\n2012 Polo\nGenk, VLG")
        self.assertEqual(listing.price, "€1,800 (eski fiyat: €2,100 📉)")
        self.assertEqual(listing.price_value, 1800.0)

    def test_alt_text_is_title_fallback(self):
        self.assertEqual(card("", alt="2009 Toyota Corolla").title, "2009 Toyota Corolla")

    def test_non_item_link_is_ignored(self):
        self.assertIsNone(cs.parse_card({"href": "/marketplace/category/cars", "text": "x"}))

    def test_price_formats(self):
        cases = {
            "€1,500": 1500.0, "€1.500": 1500.0, "1 500 €": 1500.0, "TRY850.000": 850000.0,
            "450.000 TL": 450000.0, "CA$12,000": 12000.0, "Free": 0.0, "€0": 0.0,
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(card(f"{text}\nGenk, VLG").price_value, expected)


class PriceFilterTests(unittest.TestCase):
    def test_price_rules(self):
        cases = {
            "€1": "sahte", "€50": "sahte", "€123": "sahte", "€1,234": "sahte", "€1.234": "sahte",
            "Free": "ücretsiz", "€0": "ücretsiz", "€2,001": "2000 üstü", "€12,345": "sahte",
            "€150": None, "€1,500": None, "€2,000": None,
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                reason = cs.price_rejection(card(f"{text}\nGenk, VLG"))
                if expected is None:
                    self.assertIsNone(reason)
                else:
                    self.assertIn(expected, reason)

    def test_unreadable_price_is_not_rejected(self):
        self.assertIsNone(cs.price_rejection(card("Opel Corsa\nGenk, VLG")))


class VehicleInfoTests(unittest.TestCase):
    CASES = [
        # (metin, beklenen yıl, beklenen km)
        ("Opel Corsa bouwjaar 2006, 145.000 km, gekeurd voor verkoop 2024", 2006, 145000),
        ("VW Polo 2011 benzine 185000km nieuwe distributie bij 150.000 km", 2011, 185000),
        ("Te koop: Peugeot 207, 230dkm, rijdt perfect. Prijs 1500 euro", None, 230000),
        ("Renault Clio km-stand: 210.000, eerste inschrijving 2010", 2010, 210000),
        ("Ford Fiesta, 1400cc, 2000 € vaste prijs, op 5 km van Genk", None, None),
        ("Citroën C3 2012 kilométrage 98 000 km", 2012, 98000),
        ("Auto rijdt goed, enkel export. Bel 0470 12 34 56", None, None),
        ("Driven 165,000 km", None, 165000),
        ("BMW 318d 2007 150k km", 2007, 150000),
        ("Skoda Fabia 2010. 178.000km. Gekeurd.", 2010, 178000),
    ]

    def test_extract_year_and_km(self):
        for text, year, km in self.CASES:
            with self.subTest(text=text):
                years, kms = cs.extract_years(text), cs.extract_km(text)
                self.assertEqual(min(years) if years else None, year)
                self.assertEqual(max(kms) if kms else None, km)

    def listing(self, title="", details="Genk, VLG"):
        return cs.Listing("1", title, "€1,500", 1500.0, details, "", "https://x/")

    def test_vehicle_rules(self):
        cases = [((2008, None), "2008 model"), ((2009, None), None), ((None, 200_001), "200.000"),
                 ((None, 200_000), None), ((None, None), None), ((2006, 100_000), "2006 model")]
        for (year, km), expected in cases:
            with self.subTest(year=year, km=km):
                listing = self.listing()
                listing.year, listing.km = year, km
                reason = cs.vehicle_rejection(listing)
                self.assertEqual(reason is None, expected is None)
                if expected:
                    self.assertIn(expected.split(".")[0], reason)

    def test_title_year_wins_over_description(self):
        listing = self.listing(title="2012 Polo")
        cs.apply_vehicle_info(listing, {"title": "", "description": "Distributie 2005 vervangen",
                                        "sections": [], "driven": ""})
        self.assertEqual(listing.year, 2012)

    def test_driven_field_wins_over_description(self):
        listing = self.listing()
        cs.apply_vehicle_info(listing, {"title": "", "description": "riem bij 240.000 km",
                                        "sections": [], "driven": "Driven 180,000 km"})
        self.assertEqual(listing.km, 180000)

    def test_card_mileage_is_used(self):
        listing = self.listing(details="Genk, VLG • 245K km")
        cs.apply_vehicle_info(listing)
        self.assertEqual(listing.km, 245000)

    def test_section_headings_are_stripped_from_description(self):
        listing = self.listing()
        cs.apply_vehicle_info(listing, {"title": "", "description": "", "driven": "",
                                        "sections": ["Seller's description\nNette wagen, 2013"]})
        self.assertEqual(listing.description, "Nette wagen, 2013")
        self.assertEqual(listing.year, 2013)


class SeenStoreTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "seen_cars.json")

    def tearDown(self):
        self.dir.cleanup()

    def write(self, text):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(text)

    def test_missing_and_empty_file_mean_first_run(self):
        self.assertTrue(cs.SeenStore(self.path).is_empty)
        self.write("")
        self.assertTrue(cs.SeenStore(self.path).is_empty)

    def test_corrupt_file_is_backed_up(self):
        self.write("{bozuk")
        self.assertTrue(cs.SeenStore(self.path).is_empty)
        self.assertTrue(os.path.exists(self.path + ".bak"))

    def test_legacy_id_list_is_loaded(self):
        self.write('["1", "2"]')
        store = cs.SeenStore(self.path)
        self.assertEqual(len(store), 2)
        self.assertFalse(store.is_seeded("https://x/"))

    def test_save_and_reload(self):
        store = cs.SeenStore(self.path)
        store.add("7")
        store.mark_seeded("https://x/")
        store.save()
        with open(self.path, encoding="utf-8") as f:
            self.assertEqual(json.load(f), {"seeded_urls": ["https://x/"], "seen_ids": ["7"]})
        reloaded = cs.SeenStore(self.path)
        self.assertIn("7", reloaded)
        self.assertTrue(reloaded.is_seeded("https://x/"))


class MessageTests(unittest.TestCase):
    def test_html_is_escaped_and_within_caption_limit(self):
        listing = cs.Listing("1", cs.truncate("<b>" * 100, 150), "€1", 1.0, cs.truncate("&" * 500, 150),
                             "", "https://www.facebook.com/marketplace/item/1/", 2012, 185000, "A" * 2000)
        message = cs.format_message(listing)
        self.assertNotIn("<b><b>", message)
        self.assertIn("185.000", message)
        visible = cs.html.unescape(cs.re.sub(r"<[^>]+>", "", message))   # Telegram'ın saydığı uzunluk
        self.assertLessEqual(len(visible), 1024)


if __name__ == "__main__":
    unittest.main()
