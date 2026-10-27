# Graph Report - marketplace-scraper  (2026-10-27)

## Corpus Check
- 7 files · ~6,155 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 145 nodes · 278 edges · 14 communities (10 shown, 4 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 10 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7e5bf85a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- car_sniper.py
- SeenStore
- log
- card
- scrape_search
- marketplace-scraper
- run_cycle
- marketplace-scraper: Car Sniper
- .claude/CLAUDE.md
- test_e2e_mock.py
- parse_card
- apply_vehicle_info
- MockMarketplaceTest
- dismiss_login_popup

## God Nodes (most connected - your core abstractions)
1. `SeenStore` - 17 edges
2. `log()` - 14 edges
3. `run_cycle()` - 11 edges
4. `main()` - 11 edges
5. `card()` - 11 edges
6. `marketplace-scraper: Car Sniper` - 11 edges
7. `scrape_search()` - 10 edges
8. `apply_vehicle_info()` - 9 edges
9. `evaluate_listing()` - 9 edges
10. `ParseCardTests` - 9 edges

## Surprising Connections (you probably didn't know these)
- `Git` --references--> `main()`  [INFERRED]
  CLAUDE.md → car_sniper.py
- `Tasarım kararları ve tuzaklar` --references--> `log()`  [INFERRED]
  CLAUDE.md → car_sniper.py
- `Tasarım kararları ve tuzaklar` --references--> `describe_error()`  [INFERRED]
  CLAUDE.md → car_sniper.py
- `Tasarım kararları ve tuzaklar` --references--> `truncate()`  [INFERRED]
  CLAUDE.md → car_sniper.py
- `card()` --calls--> `parse_card()`  [EXTRACTED]
  tests/test_parsing.py → car_sniper.py

## Import Cycles
- None detected.

## Communities (14 total, 4 thin omitted)

### Community 2 - "log"
Cohesion: 0.42
Nodes (6): log(), main(), notify(), send_test_message(), telegram_call(), telegram_configured()

### Community 3 - "card"
Cohesion: 0.23
Nodes (4): price_rejection(), card(), ParseCardTests, PriceFilterTests

### Community 4 - "scrape_search"
Cohesion: 0.47
Nodes (4): handle_cookie_banner(), human_pause(), is_login_wall(), scrape_search()

### Community 5 - "marketplace-scraper"
Cohesion: 0.25
Nodes (7): 1. Kurulum, 2. Telegram Bot Token ve Chat ID, 3. Doğru Marketplace arama linkini almak, 4. Filtreler, 5. Çalıştırma, 6. Test, marketplace-scraper

### Community 6 - "run_cycle"
Cohesion: 0.32
Nodes (5): describe_error(), evaluate_listing(), process_listings(), run_cycle(), short_url()

### Community 7 - "marketplace-scraper: Car Sniper"
Cohesion: 0.18
Nodes (10): Akış, Açık konular, Dosyalar, Git, Gizli bilgiler, graphify, Kullanıcının iş kuralları, marketplace-scraper: Car Sniper (+2 more)

### Community 9 - "test_e2e_mock.py"
Cohesion: 0.22
Nodes (3): card_html(), listing_html(), search_html()

### Community 10 - "parse_card"
Cohesion: 0.15
Nodes (10): format_km(), format_message(), Listing, parse_card(), parse_price_value(), _price_tokens(), truncate(), vehicle_rejection() (+2 more)

### Community 11 - "apply_vehicle_info"
Cohesion: 0.28
Nodes (4): apply_vehicle_info(), extract_km(), extract_years(), VehicleInfoTests

### Community 12 - "MockMarketplaceTest"
Cohesion: 0.20
Nodes (3): launch_browser(), MockMarketplaceTest, do_GET()

## Knowledge Gaps
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SeenStore` connect `SeenStore` to `car_sniper.py`, `log`, `MockMarketplaceTest`?**
  _High betweenness centrality (0.155) - this node is a cross-community bridge._
- **Why does `marketplace-scraper: Car Sniper` connect `marketplace-scraper: Car Sniper` to `parse_card`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Why does `Tasarım kararları ve tuzaklar` connect `parse_card` to `log`, `run_cycle`, `marketplace-scraper: Car Sniper`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._