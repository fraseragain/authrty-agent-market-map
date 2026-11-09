#!/usr/bin/env python3
"""Fetch a logo per market-map item via DuckDuckGo's favicon service (no key needed).

Reads the (item -> domain) map below, downloads
https://icons.duckduckgo.com/ip3/<domain>.ico for each, converts it to PNG with
macOS `sips`, and writes assets/logos/<slug>.png. Items with domain=None are
skipped (no company behind them, or the logo is fetched another way, e.g.
Authrty's own file in assets/logos/authrty.png).
"""
import os
import re
import subprocess
import urllib.request

OUT = os.path.join(os.path.dirname(__file__), "assets", "logos")
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
    "Cradle (hardware eng.)": None,
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
}


def slug(label):
    s = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return s


def main():
    missing, failed, skipped = [], [], []
    for label, domain in DOMAINS.items():
        s = slug(label)
        dest = os.path.join(OUT, f"{s}.png")
        if domain is None:
            skipped.append(label)
            continue
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            continue
        url = f"https://icons.duckduckgo.com/ip3/{domain}.ico"
        tmp_ico = os.path.join(OUT, f"{s}.ico")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
            if not data or len(data) < 100:
                missing.append((label, domain))
                continue
            with open(tmp_ico, "wb") as f:
                f.write(data)
            r = subprocess.run(
                ["sips", "-s", "format", "png", tmp_ico, "--out", dest],
                capture_output=True, text=True,
            )
            os.remove(tmp_ico)
            if r.returncode != 0 or not os.path.exists(dest):
                failed.append((label, domain, r.stderr.strip() or "sips conversion failed"))
        except Exception as e:
            if os.path.exists(tmp_ico):
                os.remove(tmp_ico)
            failed.append((label, domain, str(e)))
    print(f"Done. {len(DOMAINS) - len(skipped)} attempted, {len(skipped)} skipped (no domain).")
    if missing:
        print("No icon body returned for:")
        for label, domain in missing:
            print(f"  - {label} ({domain})")
    if failed:
        print("Failed:")
        for label, domain, err in failed:
            print(f"  - {label} ({domain}): {err}")


if __name__ == "__main__":
    main()
