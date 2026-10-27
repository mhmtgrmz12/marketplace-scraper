# Graph Report - marketplace-scraper  (2026-10-27)

## Corpus Check
- 5 files · ~2,629 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 64 nodes · 113 edges · 9 communities (5 shown, 4 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b2f14fca`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- car_sniper.py
- SeenStore
- log
- run_cycle
- scrape_search
- marketplace-scraper
- describe_error
- CLAUDE.md
- .claude/CLAUDE.md

## God Nodes (most connected - your core abstractions)
1. `log()` - 12 edges
2. `SeenStore` - 12 edges
3. `scrape_search()` - 10 edges
4. `run_cycle()` - 10 edges
5. `main()` - 10 edges
6. `notify()` - 8 edges
7. `process_listings()` - 7 edges
8. `send_test_message()` - 7 edges
9. `human_pause()` - 6 edges
10. `describe_error()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `dismiss_login_popup()` --calls--> `log()`  [EXTRACTED]
  car_sniper.py → car_sniper.py  _Bridges community 2 → community 6_
- `handle_cookie_banner()` --calls--> `log()`  [EXTRACTED]
  car_sniper.py → car_sniper.py  _Bridges community 2 → community 4_
- `process_listings()` --calls--> `log()`  [EXTRACTED]
  car_sniper.py → car_sniper.py  _Bridges community 2 → community 3_
- `run_cycle()` --calls--> `human_pause()`  [EXTRACTED]
  car_sniper.py → car_sniper.py  _Bridges community 4 → community 3_
- `run_cycle()` --calls--> `describe_error()`  [EXTRACTED]
  car_sniper.py → car_sniper.py  _Bridges community 6 → community 3_

## Import Cycles
- None detected.

## Communities (9 total, 4 thin omitted)

### Community 0 - "car_sniper.py"
Cohesion: 0.16
Nodes (5): format_message(), Listing, parse_card(), _price_tokens(), truncate()

### Community 2 - "log"
Cohesion: 0.42
Nodes (6): log(), main(), notify(), send_test_message(), telegram_call(), telegram_configured()

### Community 3 - "run_cycle"
Cohesion: 0.29
Nodes (6): build_user_agent(), launch_browser(), new_stealth_context(), process_listings(), run_cycle(), short_url()

### Community 4 - "scrape_search"
Cohesion: 0.47
Nodes (4): handle_cookie_banner(), human_pause(), is_login_wall(), scrape_search()

### Community 5 - "marketplace-scraper"
Cohesion: 0.33
Nodes (5): 1. Kurulum, 2. Telegram Bot Token ve Chat ID, 3. Doğru Marketplace arama linkini almak, 4. Çalıştırma, marketplace-scraper

## Knowledge Gaps
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SeenStore` connect `SeenStore` to `car_sniper.py`, `log`?**
  _High betweenness centrality (0.208) - this node is a cross-community bridge._
- **Why does `log()` connect `log` to `car_sniper.py`, `SeenStore`, `run_cycle`, `scrape_search`, `describe_error`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `scrape_search()` connect `scrape_search` to `car_sniper.py`, `log`, `run_cycle`, `describe_error`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._