#!/usr/bin/env python3
"""Generate the AI agent market map as a small static site: one overview page
and one drill-down page per segment that has a breakdown.

Edit LAYERS below to change what sits where, then run:

    python3 generate.py [out_dir] [--title TEXT]

out_dir defaults to the current directory. The script writes `index.html`
there and one file per segment with a `breakdown` under `pages/`.

The map is a stack, top to bottom: what a user or business buys, down to the
compute underneath it. Each layer holds a few segments; each segment holds a
short, illustrative (not exhaustive) list of example players, and segments
with a `breakdown` link through to a page that splits that segment into its
own sub-categories. Inclusion is a judgement call, not a ranking, and a
company in one box often competes in others too (e.g. a frontier lab shipping
its own harness and consumer agent).

See README.md for scope, sourcing and rendering to PNG.
"""
import json
import os
import re
import sys
import html

ROOT = os.path.dirname(os.path.abspath(__file__))
LOGO_DIR = os.path.join(ROOT, "assets", "logos")


def slug(label):
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")


def logo_path(label, depth=0):
    """Relative path (from the file being written) to this item's logo, if any."""
    p = os.path.join(LOGO_DIR, f"{slug(label)}.png")
    if not os.path.exists(p):
        return None
    prefix = "../" * depth
    return f"{prefix}assets/logos/{slug(label)}.png"


# layer key -> accent colour
COLOUR = {
    "apps": "#2f7fd1",
    "platforms": "#2e9e6b",
    "protocols": "#8a56c2",
    "trust": "#b3261e",
    "foundation": "#6b7a8f",
}


def seg(name, items, breakdown=None):
    return dict(name=name, items=items, breakdown=breakdown)


def sub(name, items):
    return dict(name=name, items=items)


def layer(key, title, subtitle, segments):
    return dict(key=key, title=title, subtitle=subtitle, segments=segments)


LAYERS = [
    layer(
        "apps",
        "Vertical & horizontal agent applications",
        "What end users and buyers actually use",
        [
            seg("Horizontal / general-purpose", [
                "ChatGPT (OpenAI)", "Claude (Anthropic)", "Gemini (Google)",
                "Copilot (Microsoft)", "Perplexity",
            ], breakdown=[
                sub("Consumer chat assistants", ["ChatGPT (OpenAI)", "Claude (Anthropic)", "Gemini (Google)", "Meta AI", "Grok"]),
                sub("Enterprise / work assistants", ["Microsoft Copilot", "Glean Assistant", "Gemini for Workspace"]),
                sub("Search-native assistants", ["Perplexity", "You.com", "Arc Search (The Browser Company)"]),
                sub("Model access, bring your own UI", ["Anthropic API", "OpenAI API", "Google AI Studio"]),
            ]),
            seg("Browser & computer-use agents", [
                "Operator (OpenAI)", "Comet (Perplexity)", "Claude computer use",
                "Browserbase / Browser-use", "Genspark",
            ], breakdown=[
                sub("Browser-native agents", ["Operator (OpenAI)", "Comet (Perplexity)", "Gemini in Chrome (Google)"]),
                sub("Desktop / OS computer-use", ["Claude computer use", "Adept (Amazon)"]),
                sub("Browser automation infra for builders", ["Browserbase", "Browser Use", "Skyvern", "Multion"]),
                sub("New agentic browsers", ["Genspark", "Dia (The Browser Company)", "Arc"]),
            ]),
            seg("Coding agents", [
                "Claude Code", "Cursor", "GitHub Copilot", "Devin (Cognition)",
                "Windsurf", "Replit Agent",
            ], breakdown=[
                sub("IDE-embedded", ["Cursor", "Windsurf", "GitHub Copilot", "Cody (Sourcegraph)"]),
                sub("CLI / terminal agents", ["Claude Code", "OpenAI Codex CLI", "Aider", "Amazon Q Developer CLI"]),
                sub("Autonomous SWE agents", ["Devin (Cognition)", "Replit Agent", "Factory AI"]),
                sub("Code review & QA agents", ["Greptile", "CodeRabbit", "Graphite Diamond"]),
            ]),
            seg("Customer support & sales", [
                "Sierra", "Decagon", "Intercom Fin", "Salesforce Agentforce",
                "Clay", "11x",
            ], breakdown=[
                sub("Support / CX agents", ["Sierra", "Decagon", "Intercom Fin", "Ada"]),
                sub("Sales SDR & outbound agents", ["11x", "Artisan", "Clay"]),
                sub("Revenue / CRM-native agents", ["Salesforce Agentforce", "HubSpot Breeze"]),
                sub("Voice agents", ["Bland AI", "Vapi", "Retell AI"]),
            ]),
            seg("Enterprise knowledge / research", [
                "Glean", "Hebbia", "Elicit", "You.com", "Harvey (legal)",
            ], breakdown=[
                sub("Enterprise search & RAG", ["Glean", "Hebbia", "You.com for Business"]),
                sub("Research assistants", ["Elicit", "Consensus", "Perplexity Enterprise"]),
                sub("Analyst / BI copilots", ["Rogo", "AlphaSense"]),
                sub("Legal research", ["Harvey (legal)", "CoCounsel (Thomson Reuters)", "Robin AI"]),
            ]),
            seg("Marketing & content agents", [
                "Jasper", "Copy.ai", "Writer", "Surfer SEO",
            ], breakdown=[
                sub("Content generation", ["Jasper", "Copy.ai", "Writer"]),
                sub("SEO & content ops", ["Surfer SEO", "Clearscope"]),
                sub("Social & ad creative agents", ["AdCreative.ai", "Omneky"]),
            ]),
            seg("Education & tutoring agents", [
                "Khanmigo", "Speak", "Duolingo Max",
            ], breakdown=[
                sub("Tutoring assistants", ["Khanmigo"]),
                sub("Language learning agents", ["Speak", "Duolingo Max"]),
                sub("Corporate learning agents", ["Sana Labs"]),
            ]),
            seg("Embodied / physical-world agents", [
                "Figure", "Physical Intelligence", "Skild AI",
            ], breakdown=[
                sub("Humanoid robots", ["Figure", "1X Technologies", "Apptronik"]),
                sub("Robot foundation models", ["Physical Intelligence", "Skild AI"]),
            ]),
            seg("Other verticals", [
                "Abridge (health)", "Rogo (finance)", "EvenUp (legal)",
                "Sierra (travel/CX)", "Cradle (hardware eng.)",
            ], breakdown=[
                sub("Healthcare", ["Abridge (health)", "Ambience Healthcare", "Nabla"]),
                sub("Finance & accounting", ["Rogo (finance)", "Fintool", "Basis"]),
                sub("Legal", ["EvenUp (legal)", "Harvey (legal)", "Eve (litigation)"]),
                sub("Life sciences / biotech", ["Cradle (hardware eng.)", "Latch Bio"]),
                sub("Recruiting & HR", ["Mercor", "Fetcher", "Eightfold"]),
            ]),
        ],
    ),
    layer(
        "platforms",
        "Agent platforms, orchestration & harnesses",
        "What builders use to assemble and run agents",
        [
            seg("Agent SDKs & frameworks", [
                "Claude Agent SDK", "OpenAI Agents SDK", "LangGraph",
                "CrewAI", "Google ADK", "AutoGen / AG2", "Pydantic AI",
            ], breakdown=[
                sub("First-party lab SDKs", ["Claude Agent SDK", "OpenAI Agents SDK", "Google ADK"]),
                sub("Open-source multi-agent frameworks", ["LangGraph", "CrewAI", "AutoGen / AG2", "Microsoft Semantic Kernel"]),
                sub("Typed / validation-first", ["Pydantic AI", "Instructor"]),
                sub("Retrieval-origin frameworks", ["LlamaIndex Workflows", "Haystack (deepset)"]),
            ]),
            seg("No/low-code agent builders", [
                "Dust", "Lindy", "Relevance AI", "n8n", "Zapier Agents",
                "Vellum",
            ], breakdown=[
                sub("General agent builders", ["Dust", "Lindy", "Relevance AI"]),
                sub("Workflow automation with agent steps", ["n8n", "Zapier Agents", "Make"]),
                sub("Enterprise low-code", ["Microsoft Copilot Studio", "Vellum"]),
            ]),
            seg("Multi-agent & enterprise runtime", [
                "AWS Bedrock AgentCore", "Azure AI Foundry Agent Service",
                "Vertex AI Agent Builder", "UiPath Agentic Automation",
            ], breakdown=[
                sub("Hyperscaler agent runtimes", ["AWS Bedrock AgentCore", "Azure AI Foundry Agent Service", "Vertex AI Agent Builder"]),
                sub("Enterprise automation platforms", ["UiPath Agentic Automation", "Automation Anywhere", "Workday Illuminate"]),
                sub("Agent orchestration infra", ["Temporal", "Restate"]),
            ]),
            seg("Evaluation & observability", [
                "LangSmith", "Braintrust", "Arize", "Weights & Biases Weave",
                "Langfuse", "Humanloop",
            ], breakdown=[
                sub("Agent / LLM observability", ["LangSmith", "Langfuse", "Arize", "Helicone"]),
                sub("Eval platforms", ["Braintrust", "Humanloop", "Weights & Biases Weave"]),
            ]),
            seg("Memory, retrieval & data", [
                "Pinecone", "Weaviate", "LlamaIndex", "Mem0", "Letta",
            ], breakdown=[
                sub("Vector databases", ["Pinecone", "Weaviate", "Qdrant", "Chroma"]),
                sub("Agent memory layers", ["Mem0", "Letta", "Zep"]),
                sub("Retrieval frameworks", ["LlamaIndex", "LangChain retrieval"]),
            ]),
            seg("Model gateways & routers", [
                "OpenRouter", "Portkey", "LiteLLM", "Martian",
            ], breakdown=[
                sub("Unified API gateways", ["OpenRouter", "Portkey"]),
                sub("Open-source routing libraries", ["LiteLLM"]),
                sub("Cost / performance routers", ["Martian", "Not Diamond"]),
            ]),
            seg("Agent sandboxes & code execution infra", [
                "E2B", "Modal", "Daytona",
            ], breakdown=[
                sub("Code execution sandboxes", ["E2B", "Modal"]),
                sub("Cloud dev environments for agents", ["Daytona", "CodeSandbox"]),
            ]),
            seg("Usage metering & billing for agents", [
                "Orb", "Metronome",
            ], breakdown=[
                sub("Usage-based billing infra", ["Orb", "Metronome"]),
            ]),
        ],
    ),
    layer(
        "protocols",
        "Protocols & interoperability",
        "How agents talk to tools, each other and businesses — see cheqd/agent-toolkit's capability map for the detailed breakdown",
        [
            seg("Tool & data access", [
                "MCP (Anthropic)", "OpenAPI tool calling",
            ], breakdown=[
                sub("MCP ecosystem", ["MCP (Anthropic)", "Smithery (MCP registry)", "Glama (MCP registry)"]),
                sub("Tool-calling infra for builders", ["OpenAPI tool calling", "Composio", "Arcade AI"]),
            ]),
            seg("Agent-to-agent & discovery", [
                "A2A (Linux Foundation)", "AGNTCY (Cisco)", "ANS",
            ], breakdown=[
                sub("Agent-to-agent messaging", ["A2A (Linux Foundation)", "AGNTCY (Cisco)"]),
                sub("Naming & discovery", ["ANS", "ERC-8004"]),
                sub("Agent registries & marketplaces", ["Agent.ai"]),
            ]),
            seg("Commerce & payments", [
                "AP2 (Google)", "ACP (OpenAI)", "UCP (Google)", "x402",
                "TAP (Visa)", "MPP (Stripe/Tempo)",
            ], breakdown=[
                sub("Mandate & intent protocols", ["AP2 (Google)", "Verifiable Intent (Mastercard)"]),
                sub("Checkout protocols", ["ACP (OpenAI)", "UCP (Google)", "TAP (Visa)"]),
                sub("HTTP-native & stablecoin payments", ["x402", "MPP (Stripe/Tempo)", "L402"]),
                sub("Payment credential infra", ["Stripe Shared Payment Tokens", "Skyfire"]),
            ]),
        ],
    ),
    layer(
        "trust",
        "Identity, governance & security",
        "Who an agent is, what it may do, and what stops it going wrong",
        [
            seg("Agent identity & delegation", [
                "KYA-OS (DIF)", "ERC-8004", "Baselayer", "Skyfire",
            ], breakdown=[
                sub("Identity & KYA standards", ["KYA-OS (DIF)", "Baselayer", "Skyfire"]),
                sub("On-chain agent identity", ["ERC-8004"]),
            ]),
            seg("Guardrails & red-teaming", [
                "Lakera", "CalypsoAI", "HiddenLayer", "Robust Intelligence (Cisco)",
                "Prompt Security",
            ], breakdown=[
                sub("Runtime guardrails", ["Lakera", "CalypsoAI", "Prompt Security"]),
                sub("Model & red-team testing", ["HiddenLayer", "Robust Intelligence (Cisco)", "Mindgard"]),
                sub("Open-source guardrail frameworks", ["NeMo Guardrails (Nvidia)", "Guardrails AI", "LLM Guard"]),
            ]),
            seg("AI governance & risk", [
                "Credo AI", "Holistic AI", "OneTrust AI Governance",
                "IBM watsonx.governance",
            ], breakdown=[
                sub("AI governance platforms", ["Credo AI", "Holistic AI", "OneTrust AI Governance"]),
                sub("Model risk management", ["IBM watsonx.governance", "ValidMind"]),
            ]),
            seg("Identity & access infra reused for agents", [
                "Okta (Cross App Access)", "Auth0", "WorkOS",
            ], breakdown=[
                sub("Enterprise IAM extending to agents", ["Okta (Cross App Access)", "Auth0", "Microsoft Entra Agent ID"]),
                sub("Developer-first auth", ["WorkOS", "Clerk", "Ory"]),
            ]),
            seg("Liability & insurance", [
                "Armilla AI", "Munich Re (aiSure)", "Chubb",
            ], breakdown=[
                sub("AI performance warranty & cover", ["Armilla AI", "Munich Re (aiSure)"]),
                sub("Insurers underwriting AI risk", ["Chubb"]),
            ]),
        ],
    ),
    layer(
        "foundation",
        "Foundation models & infrastructure",
        "What everything above is built on",
        [
            seg("Frontier labs", [
                "Anthropic", "OpenAI", "Google DeepMind", "Meta", "xAI", "Mistral",
            ], breakdown=[
                sub("US labs", ["Anthropic", "OpenAI", "xAI"]),
                sub("Big tech labs", ["Google DeepMind", "Meta"]),
                sub("European labs", ["Mistral"]),
            ]),
            seg("Open-weight models", [
                "Llama (Meta)", "Qwen (Alibaba)", "DeepSeek", "Mistral",
            ], breakdown=[
                sub("US open-weight", ["Llama (Meta)", "OLMo (AI2)"]),
                sub("Chinese open-weight", ["Qwen (Alibaba)", "DeepSeek", "Kimi (Moonshot)"]),
                sub("European open-weight", ["Mistral"]),
            ]),
            seg("Model hosting & inference", [
                "Together AI", "Fireworks AI", "Groq", "Amazon Bedrock",
                "Azure AI Foundry", "Vertex AI",
            ], breakdown=[
                sub("Hyperscaler-native", ["Amazon Bedrock", "Azure AI Foundry", "Vertex AI"]),
                sub("Inference specialists", ["Together AI", "Fireworks AI", "Groq", "Cerebras"]),
            ]),
            seg("Compute & training infra", [
                "Nvidia", "AWS", "Microsoft Azure", "Google Cloud", "CoreWeave",
            ], breakdown=[
                sub("Chips", ["Nvidia", "AMD", "Google TPU"]),
                sub("Cloud / GPU infra", ["AWS", "Microsoft Azure", "Google Cloud", "CoreWeave", "Lambda"]),
            ]),
            seg("Data, labeling & RLHF", [
                "Scale AI", "Surge AI", "Labelbox", "Invisible Technologies",
            ], breakdown=[
                sub("Data labeling & annotation", ["Scale AI", "Labelbox"]),
                sub("RLHF & expert data", ["Surge AI", "Invisible Technologies"]),
            ]),
            seg("Voice & multimodal model infra", [
                "ElevenLabs", "Deepgram", "Cartesia", "AssemblyAI",
            ], breakdown=[
                sub("Text-to-speech", ["ElevenLabs", "Cartesia"]),
                sub("Speech-to-text", ["Deepgram", "AssemblyAI"]),
            ]),
        ],
    ),
]


def _arg(flag):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else None


TITLE = _arg("--title") or "AI agent market map"
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "."
PAGES_DIR = os.path.join(OUT_DIR, "pages")

CSS = """
:root{
  --ink:#1b1f24; --sub:#5f6b7a; --bg:#ffffff; --panel:#f7f8fa; --border:#d8dde3; --link:#2f7fd1;
}
@media (prefers-color-scheme: dark){
  :root{ --ink:#e8ecf1; --sub:#9aa7b4; --bg:#14171b; --panel:#1b1f24; --border:#2c3238; --link:#6fa8e8; }
}
*{box-sizing:border-box;}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;padding:28px 32px 40px;}
.topbar{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;}
.brand{display:flex;align-items:center;gap:7px;color:var(--sub);font-size:12px;white-space:nowrap;flex:none;padding-top:3px;}
.brand img{width:18px;height:18px;border-radius:4px;object-fit:contain;background:#fff;}
h1{font-size:22px;margin:0 0 2px;}
.meta{color:var(--sub);font-size:12.5px;margin:0 0 22px;max-width:900px;}
.crumb{font-size:12.5px;color:var(--sub);margin:0 0 10px;}
.crumb a{color:var(--link);text-decoration:none;}
.crumb a:hover{text-decoration:underline;}
.layer{border:1px solid var(--border);border-radius:10px;margin-bottom:16px;overflow:hidden;}
.layer-head{display:flex;align-items:baseline;gap:10px;padding:10px 16px;border-bottom:1px solid var(--border);}
.layer-head .chip{width:9px;height:9px;border-radius:50%;flex:none;}
.layer-head h2{font-size:14.5px;margin:0;}
.layer-head .sub{color:var(--sub);font-size:12px;}
.segments{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:0;}
.segment{padding:12px 14px;border-right:1px solid var(--border);background:var(--panel);}
.segment:last-child{border-right:none;}
.segment h3{font-size:12px;margin:0 0 8px;color:var(--sub);font-weight:600;text-transform:uppercase;letter-spacing:.02em;}
.segment h3 a{color:inherit;text-decoration:none;}
.segment h3 a:hover{color:var(--link);text-decoration:underline;}
.segment h3 .arrow{color:var(--link);margin-left:3px;}
.items{display:flex;flex-direction:column;gap:5px;}
.item{font-size:12.5px;padding:4px 0;border-bottom:1px dashed var(--border);display:flex;align-items:center;gap:7px;}
.item:last-child{border-bottom:none;}
.item img{width:16px;height:16px;border-radius:3px;flex:none;object-fit:contain;background:#fff;}
.item .swatch{width:16px;height:16px;border-radius:3px;flex:none;background:var(--border);}
footer{color:var(--sub);font-size:11.5px;margin-top:18px;max-width:900px;}
"""


def item_row(it, depth):
    src = logo_path(it, depth)
    mark = f"<img src='{html.escape(src)}' alt=''>" if src else "<span class='swatch'></span>"
    return f"<div class='item'>{mark}<span>{html.escape(it)}</span></div>"


def brand_html(depth):
    """Authrty credit shown as page branding only — not a market-map entry."""
    src = logo_path("Authrty", depth) or f"{'../' * depth}assets/logos/authrty.png"
    return f"<div class='brand'><img src='{html.escape(src)}' alt=''><span>Map by Authrty</span></div>"


def render_index():
    out = [
        f"<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(TITLE)}</title>"
        "<link rel='alternate' type='application/json' href='market-map.json' "
        "title='Structured data for this map, for agents and scripts'>"
        f"<style>{CSS}</style></head><body>"
    ]
    out.append(f"<div class='topbar'><h1>{html.escape(TITLE)}</h1>{brand_html(0)}</div>")
    out.append(
        "<p class='meta'>A sketch of the AI agent market by layer, not a census: each segment lists a handful of "
        "illustrative players, not every company in it, and a company often spans more than one box. "
        "Segment titles with an arrow link through to a breakdown of that sub-market. "
        "See README.md for scope and how to edit it.</p>"
    )
    for l in LAYERS:
        colour = COLOUR[l["key"]]
        out.append("<div class='layer'>")
        out.append(
            f"<div class='layer-head'><span class='chip' style='background:{colour}'></span>"
            f"<h2>{html.escape(l['title'])}</h2><span class='sub'>{html.escape(l['subtitle'])}</span></div>"
        )
        out.append("<div class='segments'>")
        for s in l["segments"]:
            if s["breakdown"]:
                head = f"<a href='pages/{slug(s['name'])}.html'>{html.escape(s['name'])}<span class='arrow'>&nbsp;&rarr;</span></a>"
            else:
                head = html.escape(s["name"])
            out.append(f"<div class='segment'><h3>{head}</h3><div class='items'>")
            for it in s["items"]:
                out.append(item_row(it, depth=0))
            out.append("</div></div>")
        out.append("</div></div>")
    out.append(
        "<footer>Sketch, not exhaustive. Protocol detail (A2A, AP2, MCP and the rest) is tracked at "
        "cheqd/agent-toolkit's capability map; this map's protocols row is a summary pointer to it, not a "
        "replacement. Last assembled 2026-11-09.</footer>"
    )
    out.append("</body></html>")
    return "\n".join(out)


def render_breakdown(l, s):
    page_title = f"{s['name']} — {TITLE}"
    colour = COLOUR[l["key"]]
    out = [
        f"<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(page_title)}</title>"
        "<link rel='alternate' type='application/json' href='../market-map.json' "
        "title='Structured data for the whole map, for agents and scripts'>"
        f"<style>{CSS}</style></head><body>"
    ]
    out.append(f"<p class='crumb'><a href='../index.html'>&larr; {html.escape(TITLE)}</a> / {html.escape(l['title'])}</p>")
    out.append(f"<div class='topbar'><h1>{html.escape(s['name'])}</h1>{brand_html(1)}</div>")
    out.append(
        f"<p class='meta'>Part of <strong>{html.escape(l['title'])}</strong> — {html.escape(l['subtitle'])}. "
        "A sketch of this sub-market's own segments, same rules as the top-level map: illustrative, not exhaustive.</p>"
    )
    out.append("<div class='layer'>")
    out.append(
        f"<div class='layer-head'><span class='chip' style='background:{colour}'></span>"
        f"<h2>{html.escape(s['name'])}</h2></div>"
    )
    out.append("<div class='segments'>")
    for sub_s in s["breakdown"]:
        out.append(f"<div class='segment'><h3>{html.escape(sub_s['name'])}</h3><div class='items'>")
        for it in sub_s["items"]:
            out.append(item_row(it, depth=1))
        out.append("</div></div>")
    out.append("</div></div>")
    out.append("</body></html>")
    return "\n".join(out)


def item_obj(it, depth):
    return {"name": it, "logo": logo_path(it, depth)}


def build_data():
    """The whole map as plain data: what generate.py renders to HTML, and what
    market-map.json hands to anything that wants to read the map without
    scraping it — an agent, a script, a future version of this site."""
    layers_out = []
    for l in LAYERS:
        segments_out = []
        for s in l["segments"]:
            page = f"pages/{slug(s['name'])}.html" if s["breakdown"] else None
            breakdown_out = (
                [{"name": ss["name"], "items": [item_obj(it, 0) for it in ss["items"]]} for ss in s["breakdown"]]
                if s["breakdown"] else None
            )
            segments_out.append({
                "name": s["name"],
                "page": page,
                "items": [item_obj(it, 0) for it in s["items"]],
                "breakdown": breakdown_out,
            })
        layers_out.append({
            "key": l["key"], "title": l["title"], "subtitle": l["subtitle"], "segments": segments_out,
        })
    return {
        "title": TITLE,
        "description": (
            "A sketch of the AI agent market by layer, top (what people buy and use) to bottom "
            "(the compute underneath it). Each segment lists a handful of illustrative players, not "
            "every company in it -- this is a navigation aid, not a competitor database or a ranking. "
            "A company often appears in, or belongs in, more than one box."
        ),
        "schema_notes": (
            "layers[].segments[].items are the top-level examples shown on index.html. "
            "layers[].segments[].breakdown, where present, is the same segment split into its own "
            "named sub-categories (its drill-down page, linked by `page`); breakdown[].items follow "
            "the same {name, logo} shape as the top-level items. `logo` is a relative path from this "
            "file's own directory to a PNG, or null if no logo was found."
        ),
        "source": "https://github.com/cheqd/agent-toolkit (protocol-layer detail) + this repo (everything else)",
        "layers": layers_out,
    }


LLMS_TXT = """# AI agent market map

> A sketch of the AI agent market by layer, top (what people buy and use) \
down to the compute underneath it: applications, agent platforms and \
harnesses, protocols, identity/governance/security, and foundation models \
and infrastructure. Illustrative, not exhaustive -- a navigation aid, not a \
competitor database or a ranking.

Read [market-map.json](market-map.json) for the whole map as structured \
data: every layer, segment and example player, plus each segment's \
drill-down breakdown where one exists. That file is the source of truth for \
agents; the HTML pages are a rendering of the same data for people.

- [index.html](index.html) -- the overview page (human-readable rendering of market-map.json)
- [market-map.json](market-map.json) -- the same content as structured data
- [README.md](README.md) -- how this map is built, scope and limits, how to edit it
- `pages/<segment>.html` -- one drill-down page per segment that has a breakdown

Protocol-level detail (A2A, AP2, MCP, x402 and the rest) is out of scope \
here by design and tracked instead at \
https://github.com/cheqd/agent-toolkit/tree/main/docs/research/tools/capability-map.
"""


if __name__ == "__main__":
    os.makedirs(PAGES_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "index.html"), "w") as f:
        f.write(render_index())

    pages = 0
    for l in LAYERS:
        for s in l["segments"]:
            if not s["breakdown"]:
                continue
            with open(os.path.join(PAGES_DIR, f"{slug(s['name'])}.html"), "w") as f:
                f.write(render_breakdown(l, s))
            pages += 1

    with open(os.path.join(OUT_DIR, "market-map.json"), "w") as f:
        json.dump(build_data(), f, indent=2)
        f.write("\n")

    with open(os.path.join(OUT_DIR, "llms.txt"), "w") as f:
        f.write(LLMS_TXT)

    total = sum(len(s["items"]) for l in LAYERS for s in l["segments"])
    sub_total = sum(len(ss["items"]) for l in LAYERS for s in l["segments"] for ss in (s["breakdown"] or []))
    print(
        f"Wrote {OUT_DIR}/index.html, {OUT_DIR}/market-map.json, {OUT_DIR}/llms.txt and {pages} breakdown "
        f"pages under {PAGES_DIR}/: {len(LAYERS)} layers, {sum(len(l['segments']) for l in LAYERS)} segments, "
        f"{total} top-level players, {sub_total} sub-market players."
    )
