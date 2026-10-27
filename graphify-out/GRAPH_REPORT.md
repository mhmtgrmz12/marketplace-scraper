# Graph Report - marketplace-connection-tests-df4fae  (2026-10-27)

## Corpus Check
- 10 files · ~9,757 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 2, .service 1)

## Summary
- 188 nodes · 320 edges · 18 communities (11 shown, 7 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 7 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7c7d1e22`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- car_sniper.py
- SeenStore
- log
- card
- evaluate_listing
- marketplace-scraper
- scrape_search
- marketplace-scraper: Car Sniper
- .claude/CLAUDE.md
- test_e2e_mock.py
- apply_vehicle_info
- VehicleInfoTests
- SeenStoreTests
- run_cycle
- setup.sh
- check.sh
- MockMarketplaceTest
- log_search_location

## God Nodes (most connected - your core abstractions)
1. `log()` - 15 edges
2. `VehicleInfoTests` - 14 edges
3. `main()` - 13 edges
4. `SeenStore` - 12 edges
5. `scrape_search()` - 12 edges
6. `card()` - 12 edges
7. `evaluate_listing()` - 11 edges
8. `marketplace-scraper: Car Sniper` - 11 edges
9. `run_cycle()` - 10 edges
10. `ParseCardTests` - 10 edges

## Surprising Connections (you probably didn't know these)
- `2. Kurulum` --references--> `main()`  [INFERRED]
  deploy/README.md → car_sniper.py
- `Durum (27.10.2026, dal `claude/marketplace-connection-tests-df4fae`, `main`'e alınmadı)` --references--> `main()`  [INFERRED]
  CLAUDE.md → car_sniper.py
- `Git` --references--> `main()`  [INFERRED]
  CLAUDE.md → car_sniper.py
- `Tasarım kararları ve tuzaklar` --references--> `log()`  [INFERRED]
  CLAUDE.md → car_sniper.py
- `Tasarım kararları ve tuzaklar` --references--> `truncate()`  [INFERRED]
  CLAUDE.md → car_sniper.py

## Import Cycles
- None detected.

## Communities (18 total, 7 thin omitted)

### Community 0 - "car_sniper.py"
Cohesion: 0.17
Nodes (7): format_km(), format_message(), Listing, parse_card(), parse_price_value(), _price_tokens(), truncate()

### Community 2 - "log"
Cohesion: 0.35
Nodes (7): log(), main(), notify(), process_listings(), send_test_message(), telegram_call(), telegram_configured()

### Community 3 - "card"
Cohesion: 0.23
Nodes (3): card(), ParseCardTests, PriceFilterTests

### Community 4 - "evaluate_listing"
Cohesion: 0.20
Nodes (5): category_rejection(), evaluate_listing(), item_rejection(), price_rejection(), vehicle_rejection()

### Community 5 - "marketplace-scraper"
Cohesion: 0.12
Nodes (15): 1. Sunucu, 2. Kurulum, 3. Telegram bilgileri, 4. Kontrol ve başlatma, Car Sniper'ı sunucuda 7/24 çalıştırmak, Günlük kullanım, Sorunlar, 1. Kurulum (+7 more)

### Community 6 - "scrape_search"
Cohesion: 0.24
Nodes (6): dismiss_login_popup(), handle_cookie_banner(), human_pause(), is_login_wall(), read_listing_page(), scrape_search()

### Community 7 - "marketplace-scraper: Car Sniper"
Cohesion: 0.17
Nodes (11): Akış, Açık konular, Dosyalar, Durum (27.10.2026, dal `claude/marketplace-connection-tests-df4fae`, `main`'e alınmadı), Git, Gizli bilgiler, graphify, Kullanıcının iş kuralları (+3 more)

### Community 9 - "test_e2e_mock.py"
Cohesion: 0.13
Nodes (5): card_html(), listing_html(), search_html(), ItemFilterTests, MessageTests

### Community 10 - "apply_vehicle_info"
Cohesion: 0.22
Nodes (5): apply_vehicle_info(), extract_km(), extract_years(), listing_category(), odometer_km()

### Community 13 - "run_cycle"
Cohesion: 0.25
Nodes (6): build_user_agent(), describe_error(), launch_browser(), new_stealth_context(), run_cycle(), Tasarım kararları ve tuzaklar

### Community 14 - "setup.sh"
Cohesion: 0.60
Nodes (4): as_app(), DEBIAN_FRONTEND, log(), setup.sh script

## Knowledge Gaps
- **21 isolated node(s):** `DEBIAN_FRONTEND`, `graphify`, `Çalıştırma`, `Dosyalar`, `Akış` (+16 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 72 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `log` to `car_sniper.py`, `SeenStore`, `marketplace-scraper`, `scrape_search`, `marketplace-scraper: Car Sniper`, `run_cycle`?**
  _High betweenness centrality (0.208) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `main()` (e.g. with `Durum (27.10.2026, dal `claude/marketplace-connection-tests-df4fae`, `main`'e alınmadı)` and `Git`) actually correct?**
  _`main()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `DEBIAN_FRONTEND`, `graphify`, `Çalıştırma` to the rest of the system?**
  _21 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `marketplace-scraper` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._
- **Why does `2. Kurulum` connect `marketplace-scraper` to `log`?**
  _High betweenness centrality (0.148) - this node is a cross-community bridge._
- **Should `test_e2e_mock.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12554112554112554 - nodes in this community are weakly interconnected._