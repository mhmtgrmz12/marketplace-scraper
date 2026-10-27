# Graph Report - marketplace-connection-tests-df4fae  (2026-10-27)

## Corpus Check
- 7 files · ~8,017 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 2)

## Summary
- 164 nodes · 292 edges · 11 communities (6 shown, 5 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `59a4d3f5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- MockMarketplaceTest
- SeenStore
- log
- card
- marketplace-scraper
- marketplace-scraper: Car Sniper
- .claude/CLAUDE.md
- test_e2e_mock.py
- car_sniper.py
- VehicleInfoTests
- SeenStoreTests

## God Nodes (most connected - your core abstractions)
1. `log()` - 15 edges
2. `VehicleInfoTests` - 14 edges
3. `SeenStore` - 12 edges
4. `scrape_search()` - 12 edges
5. `main()` - 12 edges
6. `card()` - 12 edges
7. `marketplace-scraper: Car Sniper` - 11 edges
8. `evaluate_listing()` - 10 edges
9. `run_cycle()` - 10 edges
10. `ParseCardTests` - 10 edges

## Surprising Connections (you probably didn't know these)
- `Durum (27.10.2026, dal `claude/marketplace-connection-tests-df4fae`, `main`'e alınmadı)` --references--> `main()`  [INFERRED]
  CLAUDE.md → car_sniper.py
- `Git` --references--> `main()`  [INFERRED]
  CLAUDE.md → car_sniper.py
- `Tasarım kararları ve tuzaklar` --references--> `truncate()`  [INFERRED]
  CLAUDE.md → car_sniper.py
- `Tasarım kararları ve tuzaklar` --references--> `log()`  [INFERRED]
  CLAUDE.md → car_sniper.py
- `Tasarım kararları ve tuzaklar` --references--> `describe_error()`  [INFERRED]
  CLAUDE.md → car_sniper.py

## Import Cycles
- None detected.

## Communities (11 total, 5 thin omitted)

### Community 2 - "log"
Cohesion: 0.13
Nodes (19): describe_error(), dismiss_login_popup(), handle_cookie_banner(), human_pause(), is_login_wall(), launch_browser(), log(), log_search_location() (+11 more)

### Community 3 - "card"
Cohesion: 0.23
Nodes (3): card(), ParseCardTests, PriceFilterTests

### Community 5 - "marketplace-scraper"
Cohesion: 0.25
Nodes (7): 1. Kurulum, 2. Telegram Bot Token ve Chat ID, 3. Doğru Marketplace arama linkini almak, 4. Filtreler, 5. Çalıştırma, 6. Test, marketplace-scraper

### Community 7 - "marketplace-scraper: Car Sniper"
Cohesion: 0.17
Nodes (11): Akış, Açık konular, Dosyalar, Durum (27.10.2026, dal `claude/marketplace-connection-tests-df4fae`, `main`'e alınmadı), Git, Gizli bilgiler, graphify, Kullanıcının iş kuralları (+3 more)

### Community 9 - "test_e2e_mock.py"
Cohesion: 0.15
Nodes (5): card_html(), listing_html(), search_html(), ItemFilterTests, MessageTests

### Community 10 - "car_sniper.py"
Cohesion: 0.09
Nodes (17): apply_vehicle_info(), build_user_agent(), evaluate_listing(), extract_km(), extract_years(), format_km(), format_message(), item_rejection() (+9 more)

## Knowledge Gaps
- **14 isolated node(s):** `graphify`, `Çalıştırma`, `Dosyalar`, `Akış`, `Kullanıcının iş kuralları` (+9 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 62 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `VehicleInfoTests` connect `VehicleInfoTests` to `test_e2e_mock.py`?**
  _High betweenness centrality (0.141) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `main()` (e.g. with `Durum (27.10.2026, dal `claude/marketplace-connection-tests-df4fae`, `main`'e alınmadı)` and `Git`) actually correct?**
  _`main()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `graphify`, `Çalıştırma`, `Dosyalar` to the rest of the system?**
  _14 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `log` be split into smaller, more focused modules?**
  _Cohesion score 0.12873563218390804 - nodes in this community are weakly interconnected._
- **Why does `MockMarketplaceTest` connect `MockMarketplaceTest` to `test_e2e_mock.py`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Should `car_sniper.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08907563025210084 - nodes in this community are weakly interconnected._
- **Why does `SeenStore` connect `SeenStore` to `car_sniper.py`, `log`?**
  _High betweenness centrality (0.097) - this node is a cross-community bridge._