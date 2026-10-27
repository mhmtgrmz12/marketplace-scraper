# Graph Report - marketplace-connection-tests-df4fae  (2026-10-27)

## Corpus Check
- 7 files · ~7,626 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 2)

## Summary
- 160 nodes · 289 edges · 15 communities (9 shown, 6 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `35924462`
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
- apply_vehicle_info
- VehicleInfoTests
- SeenStoreTests
- evaluate_listing
- log_search_location

## God Nodes (most connected - your core abstractions)
1. `log()` - 15 edges
2. `VehicleInfoTests` - 14 edges
3. `scrape_search()` - 13 edges
4. `SeenStore` - 12 edges
5. `main()` - 12 edges
6. `card()` - 12 edges
7. `marketplace-scraper: Car Sniper` - 11 edges
8. `run_cycle()` - 10 edges
9. `ParseCardTests` - 10 edges
10. `evaluate_listing()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `Git` --references--> `main()`  [INFERRED]
  CLAUDE.md → car_sniper.py
- `Tasarım kararları ve tuzaklar` --references--> `log()`  [INFERRED]
  CLAUDE.md → car_sniper.py
- `Tasarım kararları ve tuzaklar` --references--> `describe_error()`  [INFERRED]
  CLAUDE.md → car_sniper.py
- `Kaldığım yer (27.10.2026, worktree `claude/marketplace-connection-tests-df4fae`, commit edilmedi)` --references--> `log_search_location()`  [INFERRED]
  CLAUDE.md → car_sniper.py
- `Kaldığım yer (27.10.2026, worktree `claude/marketplace-connection-tests-df4fae`, commit edilmedi)` --references--> `scrape_search()`  [INFERRED]
  CLAUDE.md → car_sniper.py

## Import Cycles
- None detected.

## Communities (15 total, 6 thin omitted)

### Community 2 - "log"
Cohesion: 0.35
Nodes (7): log(), main(), notify(), process_listings(), send_test_message(), telegram_call(), telegram_configured()

### Community 3 - "card"
Cohesion: 0.23
Nodes (3): card(), ParseCardTests, PriceFilterTests

### Community 4 - "scrape_search"
Cohesion: 0.38
Nodes (4): handle_cookie_banner(), human_pause(), is_login_wall(), scrape_search()

### Community 5 - "marketplace-scraper"
Cohesion: 0.25
Nodes (7): 1. Kurulum, 2. Telegram Bot Token ve Chat ID, 3. Doğru Marketplace arama linkini almak, 4. Filtreler, 5. Çalıştırma, 6. Test, marketplace-scraper

### Community 6 - "run_cycle"
Cohesion: 0.50
Nodes (3): describe_error(), launch_browser(), run_cycle()

### Community 7 - "marketplace-scraper: Car Sniper"
Cohesion: 0.17
Nodes (11): Akış, Açık konular, Dosyalar, Git, Gizli bilgiler, graphify, Kaldığım yer (27.10.2026, worktree `claude/marketplace-connection-tests-df4fae`, commit edilmedi), Kullanıcının iş kuralları (+3 more)

### Community 9 - "test_e2e_mock.py"
Cohesion: 0.10
Nodes (6): card_html(), listing_html(), MockMarketplaceTest, do_GET(), search_html(), MessageTests

### Community 10 - "apply_vehicle_info"
Cohesion: 0.11
Nodes (13): apply_vehicle_info(), extract_km(), extract_years(), format_km(), format_message(), Listing, odometer_km(), parse_card() (+5 more)

### Community 13 - "evaluate_listing"
Cohesion: 0.25
Nodes (4): dismiss_login_popup(), evaluate_listing(), price_rejection(), read_listing_page()

## Knowledge Gaps
- **14 isolated node(s):** `graphify`, `Çalıştırma`, `Dosyalar`, `Akış`, `Kullanıcının iş kuralları` (+9 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 60 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `VehicleInfoTests` connect `VehicleInfoTests` to `test_e2e_mock.py`?**
  _High betweenness centrality (0.144) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `main()` (e.g. with `Git` and `Kaldığım yer (27.10.2026, worktree `claude/marketplace-connection-tests-df4fae`, commit edilmedi)`) actually correct?**
  _`main()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `graphify`, `Çalıştırma`, `Dosyalar` to the rest of the system?**
  _14 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_e2e_mock.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09852216748768473 - nodes in this community are weakly interconnected._
- **Why does `SeenStore` connect `SeenStore` to `car_sniper.py`, `log`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Should `apply_vehicle_info` be split into smaller, more focused modules?**
  _Cohesion score 0.1111111111111111 - nodes in this community are weakly interconnected._