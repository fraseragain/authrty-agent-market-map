#!/usr/bin/env python3
"""Generate the AI agent market map as a self-contained HTML page.

Edit LAYERS below to change what sits where, then run:

    python3 generate.py [output.html] [--title TEXT]

The map is a stack, top to bottom: what a user or business buys, down to the
compute underneath it. Each layer holds a few segments; each segment holds a
short, illustrative (not exhaustive) list of example players. Inclusion is a
judgement call, not a ranking, and a company in one segment often competes in
others too (e.g. a frontier lab shipping its own harness and consumer agent).

See README.md for scope, sourcing and rendering to PNG.
"""
import os
import re
import sys
import html

LOGO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logos")


def slug(label):
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")


def logo_path(label):
    """Relative path to this item's logo file, if fetch_logos.py produced one."""
    p = os.path.join(LOGO_DIR, f"{slug(label)}.png")
    return f"assets/logos/{slug(label)}.png" if os.path.exists(p) else None


# layer key -> accent colour
COLOUR = {
    "apps": "#2f7fd1",
    "platforms": "#2e9e6b",
    "protocols": "#8a56c2",
    "trust": "#b3261e",
    "foundation": "#6b7a8f",
}


def seg(name, items, note=None):
    return dict(name=name, items=items, note=note)


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
            ]),
            seg("Browser & computer-use agents", [
                "Operator (OpenAI)", "Comet (Perplexity)", "Claude computer use",
                "Browserbase / Browser-use", "Genspark",
            ]),
            seg("Coding agents", [
                "Claude Code", "Cursor", "GitHub Copilot", "Devin (Cognition)",
                "Windsurf", "Replit Agent",
            ]),
            seg("Customer support & sales", [
                "Sierra", "Decagon", "Intercom Fin", "Salesforce Agentforce",
                "Clay", "11x",
            ]),
            seg("Enterprise knowledge / research", [
                "Glean", "Hebbia", "Elicit", "You.com", "Harvey (legal)",
            ]),
            seg("Other verticals", [
                "Abridge (health)", "Rogo (finance)", "EvenUp (legal)",
                "Sierra (travel/CX)", "Cradle (hardware eng.)",
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
            ]),
            seg("No/low-code agent builders", [
                "Dust", "Lindy", "Relevance AI", "n8n", "Zapier Agents",
                "Vellum",
            ]),
            seg("Multi-agent & enterprise runtime", [
                "AWS Bedrock AgentCore", "Azure AI Foundry Agent Service",
                "Vertex AI Agent Builder", "UiPath Agentic Automation",
            ]),
            seg("Evaluation & observability", [
                "LangSmith", "Braintrust", "Arize", "Weights & Biases Weave",
                "Langfuse", "Humanloop",
            ]),
            seg("Memory, retrieval & data", [
                "Pinecone", "Weaviate", "LlamaIndex", "Mem0", "Letta",
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
            ]),
            seg("Agent-to-agent & discovery", [
                "A2A (Linux Foundation)", "AGNTCY (Cisco)", "ANS",
            ]),
            seg("Commerce & payments", [
                "AP2 (Google)", "ACP (OpenAI)", "UCP (Google)", "x402",
                "TAP (Visa)", "MPP (Stripe/Tempo)",
            ]),
        ],
    ),
    layer(
        "trust",
        "Identity, governance & security",
        "Who an agent is, what it may do, and what stops it going wrong",
        [
            seg("Agent identity & delegation", [
                "Authrty", "KYA-OS (DIF)", "ERC-8004", "Baselayer", "Skyfire",
            ]),
            seg("Guardrails & red-teaming", [
                "Lakera", "CalypsoAI", "HiddenLayer", "Robust Intelligence (Cisco)",
                "Prompt Security",
            ]),
            seg("AI governance & risk", [
                "Credo AI", "Holistic AI", "OneTrust AI Governance",
                "IBM watsonx.governance",
            ]),
            seg("Identity & access infra reused for agents", [
                "Okta (Cross App Access)", "Auth0", "WorkOS", "cheqd (DID infra)",
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
            ]),
            seg("Open-weight models", [
                "Llama (Meta)", "Qwen (Alibaba)", "DeepSeek", "Mistral",
            ]),
            seg("Model hosting & inference", [
                "Together AI", "Fireworks AI", "Groq", "Amazon Bedrock",
                "Azure AI Foundry", "Vertex AI",
            ]),
            seg("Compute & training infra", [
                "Nvidia", "AWS", "Microsoft Azure", "Google Cloud", "CoreWeave",
            ]),
        ],
    ),
]


def _arg(flag):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else None


TITLE = _arg("--title") or "AI agent market map"
OUT = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "market-map.html"

CSS = """
:root{
  --ink:#1b1f24; --sub:#5f6b7a; --bg:#ffffff; --panel:#f7f8fa; --border:#d8dde3;
}
@media (prefers-color-scheme: dark){
  :root{ --ink:#e8ecf1; --sub:#9aa7b4; --bg:#14171b; --panel:#1b1f24; --border:#2c3238; }
}
*{box-sizing:border-box;}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;padding:28px 32px 40px;}
h1{font-size:22px;margin:0 0 2px;}
.meta{color:var(--sub);font-size:12.5px;margin:0 0 22px;max-width:900px;}
.layer{border:1px solid var(--border);border-radius:10px;margin-bottom:16px;overflow:hidden;}
.layer-head{display:flex;align-items:baseline;gap:10px;padding:10px 16px;border-bottom:1px solid var(--border);}
.layer-head .chip{width:9px;height:9px;border-radius:50%;flex:none;}
.layer-head h2{font-size:14.5px;margin:0;}
.layer-head .sub{color:var(--sub);font-size:12px;}
.segments{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:0;}
.segment{padding:12px 14px;border-right:1px solid var(--border);background:var(--panel);}
.segment:last-child{border-right:none;}
.segment h3{font-size:12px;margin:0 0 8px;color:var(--sub);font-weight:600;text-transform:uppercase;letter-spacing:.02em;}
.items{display:flex;flex-direction:column;gap:5px;}
.item{font-size:12.5px;padding:4px 0;border-bottom:1px dashed var(--border);display:flex;align-items:center;gap:7px;}
.item:last-child{border-bottom:none;}
.item img{width:16px;height:16px;border-radius:3px;flex:none;object-fit:contain;background:#fff;}
.item .swatch{width:16px;height:16px;border-radius:3px;flex:none;background:var(--border);}
footer{color:var(--sub);font-size:11.5px;margin-top:18px;max-width:900px;}
"""


def render():
    out = [f"<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(TITLE)}</title><style>{CSS}</style></head><body>"]
    out.append(f"<h1>{html.escape(TITLE)}</h1>")
    out.append(
        "<p class='meta'>A sketch of the AI agent market by layer, not a census: each segment lists a handful of "
        "illustrative players, not every company in it, and a company often spans more than one box. "
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
            out.append(f"<div class='segment'><h3>{html.escape(s['name'])}</h3><div class='items'>")
            for it in s["items"]:
                src = logo_path(it)
                mark = f"<img src='{html.escape(src)}' alt=''>" if src else "<span class='swatch'></span>"
                out.append(f"<div class='item'>{mark}<span>{html.escape(it)}</span></div>")
            out.append("</div></div>")
        out.append("</div></div>")
    out.append(
        "<footer>Sketch, not exhaustive. Protocol detail (A2A, AP2, MCP and the rest) is tracked at "
        "cheqd/agent-toolkit's capability map; this map's protocols row is a summary pointer to it, not a "
        "replacement. Last assembled 2026-11-09.</footer>"
    )
    out.append("</body></html>")
    return "\n".join(out)


if __name__ == "__main__":
    html_out = render()
    with open(OUT, "w") as f:
        f.write(html_out)
    total = sum(len(s["items"]) for l in LAYERS for s in l["segments"])
    print(f"Wrote {OUT}: {len(LAYERS)} layers, {sum(len(l['segments']) for l in LAYERS)} segments, {total} example players.")
