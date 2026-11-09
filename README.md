# AI agent market map

Live at **[fraseragain.github.io/authrty-agent-market-map](https://fraseragain.github.io/authrty-agent-market-map/)**, built by [Authrty](https://authrty.ai).

A small static site sketching the AI agent market as a whole: one overview
page (`index.html`) laid out as a stack from what people buy and use down to
the compute it runs on, and a drill-down page under `pages/` for every
segment that has one — click a segment's title (the ones with an arrow) to
see that sub-market broken into its own categories.

The stack, top to bottom:

1. **Vertical & horizontal agent applications** — the products people and businesses use.
2. **Agent platforms, orchestration & harnesses** — what builders use to assemble and run agents.
3. **Protocols & interoperability** — how agents talk to tools, each other and businesses.
4. **Identity, governance & security** — who an agent is, what it may do, what stops it going wrong.
5. **Foundation models & infrastructure** — what everything above is built on.

This is a sketch, not a census. Each segment lists a handful of illustrative
players, not every company in it, and a company often spans more than one
box (a frontier lab shipping its own harness and consumer agent, a payments
protocol vendor also doing identity). Inclusion is a judgement call made
2026-11-09, not a ranking.

It deliberately stays shallow on protocols — that detail (A2A, AP2, MCP, x402
and the rest, with adoption evidence and capability-level ratings) already
lives in [`cheqd/agent-toolkit`](https://github.com/cheqd/agent-toolkit)'s
[capability map](https://github.com/cheqd/agent-toolkit/tree/main/docs/research/tools/capability-map).
This repo is the wide, shallow view; that one is the narrow, deep view of a
single layer.

## Reading this as an agent

`market-map.json` is the whole map as plain data — every layer, segment,
example player and drill-down breakdown, with a `schema_notes` field
explaining its own shape so an agent doesn't need this README to parse it.
`index.html` and every `pages/*.html` file link to it via
`<link rel="alternate" type="application/json" href="...">` in `<head>`, and
`llms.txt` at the repo root points to both for anything that checks there
first. It's written by the same `generate.py` run that writes the HTML, so it
never drifts from what the pages show — edit `LAYERS`, rerun, both update
together.

## Branding

Authrty isn't a market-map entry — it's credited as the map's author in a
small "Map by Authrty" mark in the top-right of every page, using
`assets/logos/authrty.png` (copied in by hand, not fetched). If the map ever
needs a different credit, or none, edit `brand_html()` in `generate.py`.

## Logos

`fetch_logos.py` downloads a small icon per item, no key needed. It tries
DuckDuckGo's favicon service first (`icons.duckduckgo.com/ip3/<domain>.ico`);
DuckDuckGo returns one of a few fixed placeholder glyphs rather than a 404
when it has no real favicon for a domain, so the script checks the result
against `GENERIC_HASHES` and, if it matches (or nothing came back), retries
through Google's favicon service instead. Items with no obvious company
behind them, or where both services came back empty, fall back to a plain
grey swatch in the chart. To add or change an item's logo: edit the
`DOMAINS` map in `fetch_logos.py` (or drop a PNG straight into
`assets/logos/<slug>.png`, where `<slug>` is the item's label lower-cased
with everything but letters/digits turned into `-`), then rerun:

```bash
python3 fetch_logos.py           # only fetches what's missing
python3 fetch_logos.py --recheck # also re-validates files already on disk
```

## Edit it

All the content is in the `LAYERS` list in `generate.py` — a list of layers,
each with a title, subtitle and a few named segments. A segment is a short
top-level list of example players plus an optional `breakdown`: a list of
named sub-categories, each with its own short item list, rendered as that
segment's drill-down page. A segment with no `breakdown` just has no arrow
on the overview page — add one any time by passing `breakdown=[sub(...), ...]`
to `seg(...)`. Edit `LAYERS`, then regenerate:

```bash
python3 generate.py .        # writes ./index.html, ./market-map.json, ./llms.txt, ./pages/<segment>.html
```

Open `index.html` in a browser — the drill-down links are relative, so it
works straight off disk, no server needed.

## Render to PNG

Any headless Chromium works. For example, with Chrome on macOS:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless \
  --hide-scrollbars --force-device-scale-factor=2 --window-size=1500,1565 \
  --screenshot=market-map.png file://$PWD/index.html
```

The same works on any `pages/<segment>.html` file for a one-off image of a
single drill-down page. Adjust `--window-size` to roughly match the page's
content height so the screenshot isn't padded with blank space.

## Limits

- Not exhaustive, and not meant to be. It's a navigation aid for thinking
  about where a given company, product or feature sits, not a competitor
  database.
- No funding, revenue or market-share data — this is a taxonomy, not a
  research report.
- Company placement is a snapshot judgement call, not sourced the way the
  protocol capability map's ratings are (spec-read vs. secondary). Treat it
  as a starting sketch to argue with and correct, not a finished reference.
