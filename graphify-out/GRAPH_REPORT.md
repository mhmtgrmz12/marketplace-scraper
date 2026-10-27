# Graph Report - marketplace-scraper  (2026-10-27)

## Corpus Check
- 5 files · ~3,728 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 81 nodes · 147 edges · 12 communities (7 shown, 5 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c667c3da`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- SeenStore
- log
- build_user_agent
- scrape_search
- marketplace-scraper
- evaluate_listing
- CLAUDE.md
- .claude/CLAUDE.md
- format_message
- parse_card
- apply_vehicle_info

## God Nodes (most connected - your core abstractions)
1. `log()` - 13 edges
2. `SeenStore` - 12 edges
3. `scrape_search()` - 10 edges
4. `run_cycle()` - 10 edges
5. `main()` - 10 edges
6. `evaluate_listing()` - 9 edges
7. `notify()` - 8 edges
8. `process_listings()` - 8 edges
9. `human_pause()` - 7 edges
10. `send_test_message()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `dismiss_login_popup()` --calls--> `log()`  [EXTRACTED]
  car_sniper.py → car_sniper.py  _Bridges community 2 → community 4_
- `evaluate_listing()` --calls--> `log()`  [EXTRACTED]
  car_sniper.py → car_sniper.py  _Bridges community 2 → community 6_
- `parse_card()` --calls--> `truncate()`  [EXTRACTED]
  car_sniper.py → car_sniper.py  _Bridges community 9 → community 10_
- `dismiss_login_popup()` --calls--> `describe_error()`  [EXTRACTED]
  car_sniper.py → car_sniper.py  _Bridges community 6 → community 4_
- `send_test_message()` --calls--> `Listing`  [EXTRACTED]
  car_sniper.py → car_sniper.py  _Bridges community 10 → community 2_

## Import Cycles
- None detected.

## Communities (12 total, 5 thin omitted)

### Community 2 - "log"
Cohesion: 0.27
Nodes (10): launch_browser(), log(), main(), notify(), process_listings(), run_cycle(), send_test_message(), short_url() (+2 more)

### Community 4 - "scrape_search"
Cohesion: 0.27
Nodes (6): dismiss_login_popup(), handle_cookie_banner(), human_pause(), is_login_wall(), read_listing_page(), scrape_search()

### Community 5 - "marketplace-scraper"
Cohesion: 0.29
Nodes (6): 1. Kurulum, 2. Telegram Bot Token ve Chat ID, 3. Doğru Marketplace arama linkini almak, 4. Filtreler, 5. Çalıştırma, marketplace-scraper

### Community 6 - "evaluate_listing"
Cohesion: 0.33
Nodes (3): describe_error(), evaluate_listing(), price_rejection()

### Community 9 - "format_message"
Cohesion: 0.33
Nodes (4): format_km(), format_message(), truncate(), vehicle_rejection()

### Community 10 - "parse_card"
Cohesion: 0.33
Nodes (4): Listing, parse_card(), parse_price_value(), _price_tokens()

### Community 11 - "apply_vehicle_info"
Cohesion: 0.40
Nodes (3): apply_vehicle_info(), extract_km(), extract_years()

## Knowledge Gaps
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SeenStore` connect `SeenStore` to `car_sniper.py`, `log`?**
  _High betweenness centrality (0.172) - this node is a cross-community bridge._
- **Why does `log()` connect `log` to `car_sniper.py`, `SeenStore`, `scrape_search`, `evaluate_listing`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `evaluate_listing()` connect `evaluate_listing` to `car_sniper.py`, `log`, `scrape_search`, `format_message`, `apply_vehicle_info`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._