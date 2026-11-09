# AI agent market map

A one-page sketch of the AI agent market as a whole, laid out as a stack from
what people buy and use down to the compute it runs on:

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

## Edit it

All the content is in the `LAYERS` list in `generate.py` — a list of layers,
each with a title, subtitle and a few named segments, each segment a short
list of example players. Edit that list, then regenerate.

```bash
python3 generate.py market-map.html
```

## Render to PNG

Any headless Chromium works. For example, with Chrome on macOS:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless \
  --hide-scrollbars --force-device-scale-factor=2 --window-size=1500,1555 \
  --screenshot=market-map.png file://$PWD/market-map.html
```

Adjust `--window-size` height if you add or remove segments or layers — it
should roughly match the page's content height so the screenshot isn't
padded with blank space.

## Limits

- Not exhaustive, and not meant to be. It's a navigation aid for thinking
  about where a given company, product or feature sits, not a competitor
  database.
- No funding, revenue or market-share data — this is a taxonomy, not a
  research report.
- Company placement is a snapshot judgement call, not sourced the way the
  protocol capability map's ratings are (spec-read vs. secondary). Treat it
  as a starting sketch to argue with and correct, not a finished reference.
