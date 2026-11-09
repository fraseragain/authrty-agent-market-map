#!/usr/bin/env python3
"""Fetch a logo per market-map item, no key needed.

Reads the (item -> domain) map below. For each, tries
https://icons.duckduckgo.com/ip3/<domain>.ico first, converts it to PNG with
macOS `sips`, and writes assets/logos/<slug>.png. DuckDuckGo returns a generic
placeholder glyph (a few fixed images) rather than a 404 when it has no real
favicon for a domain -- GENERIC_HASHES lists their MD5s, so those are detected
and rejected rather than saved as if they were a real logo. When DDG has
nothing real, or the request fails outright, it falls back to Google's
favicon service (https://www.google.com/s2/favicons). Items with domain=None
are skipped (no company behind them, or the logo is fetched another way, e.g.
Authrty's own file in assets/logos/authrty.png).

Run with --recheck to also re-validate files already on disk (slower, but
catches cases where an earlier run saved one of DDG's generic placeholders
before GENERIC_HASHES knew about it).
"""
import hashlib
import os
import re
import subprocess
import sys
import urllib.request

OUT = os.path.join(os.path.dirname(__file__), "assets", "logos")

# MD5s of DuckDuckGo's own generic "no real favicon" placeholder images,
# observed by fetching known-nonexistent domains and domains that otherwise
# return the same bytes as an unrelated company (e.g. microsoft.com and
# fintool.com both came back with hash b49de891...). Grows as new ones turn up.
GENERIC_HASHES = {
    "b49de8917046a69241832c8b94139499",
    "911944405987195b41fc7c0e2c8ce826",
}
os.makedirs(OUT, exist_ok=True)

# item label (as it appears in generate.py) -> domain to fetch from Clearbit
DOMAINS = {
    "ChatGPT (OpenAI)": "openai.com",
    "Claude (Anthropic)": "anthropic.com",
    "Gemini (Google)": "google.com",
    "Copilot (Microsoft)": "microsoft.com",
    "Perplexity": "perplexity.ai",
    "Operator (OpenAI)": "openai.com",
    "Comet (Perplexity)": "perplexity.ai",
    "Claude computer use": "anthropic.com",
    "Browserbase / Browser-use": "browserbase.com",
    "Genspark": "genspark.ai",
    "Claude Code": "anthropic.com",
    "Cursor": "cursor.com",
    "GitHub Copilot": "github.com",
    "Devin (Cognition)": "cognition.ai",
    "Windsurf": "windsurf.com",
    "Replit Agent": "replit.com",
    "Sierra": "sierra.ai",
    "Decagon": "decagon.ai",
    "Intercom Fin": "intercom.com",
    "Salesforce Agentforce": "salesforce.com",
    "Clay": "clay.com",
    "11x": "11x.ai",
    "Glean": "glean.com",
    "Hebbia": "hebbia.ai",
    "Elicit": "elicit.com",
    "You.com": "you.com",
    "Harvey (legal)": "harvey.ai",
    "Abridge (health)": "abridge.com",
    "Rogo (finance)": "rogo.ai",
    "EvenUp (legal)": "evenuplaw.com",
    "Sierra (travel/CX)": "sierra.ai",
    "Cradle (hardware eng.)": "cradle.bio",
    "Claude Agent SDK": "anthropic.com",
    "OpenAI Agents SDK": "openai.com",
    "LangGraph": "langchain.com",
    "CrewAI": "crewai.com",
    "Google ADK": "google.com",
    "AutoGen / AG2": "microsoft.com",
    "Pydantic AI": "pydantic.dev",
    "Dust": "dust.tt",
    "Lindy": "lindy.ai",
    "Relevance AI": "relevanceai.com",
    "n8n": "n8n.io",
    "Zapier Agents": "zapier.com",
    "Vellum": "vellum.ai",
    "AWS Bedrock AgentCore": "aws.amazon.com",
    "Azure AI Foundry Agent Service": "azure.microsoft.com",
    "Vertex AI Agent Builder": "cloud.google.com",
    "UiPath Agentic Automation": "uipath.com",
    "LangSmith": "langchain.com",
    "Braintrust": "braintrust.dev",
    "Arize": "arize.com",
    "Weights & Biases Weave": "wandb.ai",
    "Langfuse": "langfuse.com",
    "Humanloop": "humanloop.com",
    "Pinecone": "pinecone.io",
    "Weaviate": "weaviate.io",
    "LlamaIndex": "llamaindex.ai",
    "Mem0": "mem0.ai",
    "Letta": "letta.com",
    "MCP (Anthropic)": "anthropic.com",
    "OpenAPI tool calling": None,
    "A2A (Linux Foundation)": "linuxfoundation.org",
    "AGNTCY (Cisco)": "cisco.com",
    "ANS": None,
    "AP2 (Google)": "google.com",
    "ACP (OpenAI)": "openai.com",
    "UCP (Google)": "google.com",
    "x402": "x402.org",
    "TAP (Visa)": "visa.com",
    "MPP (Stripe/Tempo)": "stripe.com",
    "Authrty": None,  # local file, see assets/logos/authrty.png
    "KYA-OS (DIF)": "identity.foundation",
    "ERC-8004": "ethereum.org",
    "Baselayer": "baselayer.com",
    "Skyfire": "skyfire.xyz",
    "Lakera": "lakera.ai",
    "CalypsoAI": "calypsoai.com",
    "HiddenLayer": "hiddenlayer.com",
    "Robust Intelligence (Cisco)": "cisco.com",
    "Prompt Security": "prompt.security",
    "Credo AI": "credo.ai",
    "Holistic AI": "holisticai.com",
    "OneTrust AI Governance": "onetrust.com",
    "IBM watsonx.governance": "ibm.com",
    "Okta (Cross App Access)": "okta.com",
    "Auth0": "auth0.com",
    "WorkOS": "workos.com",
    "cheqd (DID infra)": "cheqd.io",
    "Anthropic": "anthropic.com",
    "OpenAI": "openai.com",
    "Google DeepMind": "deepmind.google",
    "Meta": "meta.com",
    "xAI": "grok.com",
    "Mistral": "mistral.ai",
    "Llama (Meta)": "meta.com",
    "Qwen (Alibaba)": "alibaba.com",
    "DeepSeek": "deepseek.com",
    "Together AI": "together.ai",
    "Fireworks AI": "fireworks.ai",
    "Groq": "groq.com",
    "Amazon Bedrock": "aws.amazon.com",
    "Azure AI Foundry": "azure.microsoft.com",
    "Vertex AI": "cloud.google.com",
    "Nvidia": "nvidia.com",
    "AWS": "aws.amazon.com",
    "Microsoft Azure": "azure.microsoft.com",
    "Google Cloud": "cloud.google.com",
    "CoreWeave": "coreweave.com",

    # --- sub-market breakdown pages ---
    "Meta AI": "meta.com",
    "Grok": "grok.com",
    "Microsoft Copilot": "microsoft.com",
    "Gemini for Workspace": "google.com",
    "Arc Search (The Browser Company)": "arc.net",
    "Arc": "arc.net",
    "Dia (The Browser Company)": "diabrowser.com",
    "Anthropic API": "anthropic.com",
    "OpenAI API": "openai.com",
    "Google AI Studio": "google.com",
    "Adept (Amazon)": "amazon.com",
    "Browserbase": "browserbase.com",
    "Browser Use": "browser-use.com",
    "Skyvern": "skyvern.com",
    "Multion": "multion.ai",
    "Cody (Sourcegraph)": "sourcegraph.com",
    "OpenAI Codex CLI": "openai.com",
    "Aider": "aider.chat",
    "Amazon Q Developer CLI": "aws.amazon.com",
    "Factory AI": "factory.ai",
    "Greptile": "greptile.com",
    "CodeRabbit": "coderabbit.ai",
    "Graphite Diamond": "graphite.dev",
    "Ada": "ada.cx",
    "Artisan": "artisan.co",
    "HubSpot Breeze": "hubspot.com",
    "Bland AI": "bland.ai",
    "Vapi": "vapi.ai",
    "Retell AI": "retellai.com",
    "You.com for Business": "you.com",
    "Consensus": "consensus.app",
    "Perplexity Enterprise": "perplexity.ai",
    "AlphaSense": "alpha-sense.com",
    "Rogo": "rogo.ai",
    "CoCounsel (Thomson Reuters)": "thomsonreuters.com",
    "Robin AI": "robinai.com",
    "Ambience Healthcare": "ambiencehealthcare.com",
    "Nabla": "nabla.com",
    "Fintool": "fintool.com",
    "Basis": "basis.net",
    "Eve (litigation)": "eve.legal",
    "Latch Bio": "latch.bio",
    "Mercor": "mercor.com",
    "Fetcher": "fetcher.ai",
    "Eightfold": "eightfold.ai",
    "Microsoft Semantic Kernel": "microsoft.com",
    "Instructor": "python.useinstructor.com",
    "Haystack (deepset)": "haystack.deepset.ai",
    "LlamaIndex Workflows": "llamaindex.ai",
    "Make": "make.com",
    "Microsoft Copilot Studio": "microsoft.com",
    "Automation Anywhere": "automationanywhere.com",
    "Workday Illuminate": "workday.com",
    "Temporal": "temporal.io",
    "Restate": "restate.dev",
    "Helicone": "helicone.ai",
    "Qdrant": "qdrant.tech",
    "Chroma": "trychroma.com",
    "LangChain retrieval": "langchain.com",
    "Zep": "getzep.com",
    "Smithery (MCP registry)": "smithery.ai",
    "Glama (MCP registry)": "glama.ai",
    "Composio": "composio.dev",
    "Arcade AI": "arcade.dev",
    "Agent.ai": "agent.ai",
    "Verifiable Intent (Mastercard)": "mastercard.com",
    "Stripe Shared Payment Tokens": "stripe.com",
    "Mindgard": "mindgard.ai",
    "NeMo Guardrails (Nvidia)": "nvidia.com",
    "Guardrails AI": "guardrailsai.com",
    "LLM Guard": "protectai.com",
    "ValidMind": "validmind.com",
    "Microsoft Entra Agent ID": "microsoft.com",
    "Clerk": "clerk.com",
    "Ory": "ory.sh",
    "OLMo (AI2)": "allenai.org",
    "Kimi (Moonshot)": "moonshot.ai",
    "Cerebras": "cerebras.ai",
    "Lambda": "lambdalabs.com",
    "Google TPU": "cloud.google.com",
    "AMD": "amd.com",
    "L402": None,
    "Gemini in Chrome (Google)": "google.com",
    "Glean Assistant": "glean.com",
}


def slug(label):
    s = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return s


def _fetch_ico_as_png(url, dest):
    """Download an .ico URL and convert it to PNG at dest. Returns the MD5 of
    dest's bytes, or None if nothing usable came back."""
    tmp_ico = dest + ".tmp.ico"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
        if not data or len(data) < 100:
            return None
        with open(tmp_ico, "wb") as f:
            f.write(data)
        r = subprocess.run(
            ["sips", "-s", "format", "png", tmp_ico, "--out", dest],
            capture_output=True, text=True,
        )
        if r.returncode != 0 or not os.path.exists(dest):
            return None
        return hashlib.md5(open(dest, "rb").read()).hexdigest()
    except Exception:
        return None
    finally:
        if os.path.exists(tmp_ico):
            os.remove(tmp_ico)


def _fetch_png_direct(url, dest):
    """Download a URL that already serves a PNG (Google's favicon service).
    Returns the MD5 of dest's bytes, or None."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
        if not data or len(data) < 100:
            return None
        with open(dest, "wb") as f:
            f.write(data)
        return hashlib.md5(data).hexdigest()
    except Exception:
        return None


def fetch_one(label, domain, dest):
    """Try DuckDuckGo first, reject its generic placeholder, fall back to
    Google's favicon service. Returns 'ok', 'generic-only' or 'failed'."""
    h = _fetch_ico_as_png(f"https://icons.duckduckgo.com/ip3/{domain}.ico", dest)
    if h and h not in GENERIC_HASHES:
        return "ok"
    h2 = _fetch_png_direct(f"https://www.google.com/s2/favicons?domain={domain}&sz=128", dest)
    if h2 and h2 not in GENERIC_HASHES:
        return "ok"
    if os.path.exists(dest):
        os.remove(dest)
    return "generic-only" if (h or h2) else "failed"


def main():
    recheck = "--recheck" in sys.argv
    ok, generic, failed, skipped = 0, [], [], []
    for label, domain in DOMAINS.items():
        s = slug(label)
        dest = os.path.join(OUT, f"{s}.png")
        if domain is None:
            skipped.append(label)
            continue
        if not recheck and os.path.exists(dest) and os.path.getsize(dest) > 0:
            continue
        result = fetch_one(label, domain, dest)
        if result == "ok":
            ok += 1
        elif result == "generic-only":
            generic.append((label, domain))
        else:
            failed.append((label, domain))
    print(f"Done. {ok} fetched, {len(skipped)} skipped (no domain), "
          f"{len(generic)} generic-only, {len(failed)} failed.")
    if generic:
        print("Only a generic placeholder came back for (no real favicon found):")
        for label, domain in generic:
            print(f"  - {label} ({domain})")
    if failed:
        print("Failed outright for:")
        for label, domain in failed:
            print(f"  - {label} ({domain})")


if __name__ == "__main__":
    main()
