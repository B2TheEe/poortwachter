"""Kies je model via de omgevingsvariabele LLM_PROVIDER: ollama (standaard), openai, anthropic of mock."""
import os

PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()


def chat(system: str, user: str) -> str:
    if PROVIDER == "ollama":
        return _ollama(system, user)
    if PROVIDER == "openai":
        return _openai(system, user)
    if PROVIDER == "anthropic":
        return _anthropic(system, user)
    if PROVIDER == "mock":
        # Lekt altijd alles: handig om je filters te testen zonder model.
        return f"(mock) Je vroeg: {user}. Mijn instructies waren: {system}"
    raise ValueError(f"Onbekende LLM_PROVIDER: {PROVIDER}")


def _ollama(system, user):
    import requests
    url = os.getenv("OLLAMA_URL", "http://localhost:11434") + "/api/chat"
    resp = requests.post(url, timeout=120, json={
        "model": os.getenv("OLLAMA_MODEL", "llama3.2"),
        "stream": False,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
    })
    resp.raise_for_status()
    return resp.json()["message"]["content"]


def _openai(system, user):
    from openai import OpenAI
    resp = OpenAI().chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
    )
    return resp.choices[0].message.content or ""


def _anthropic(system, user):
    import anthropic
    resp = anthropic.Anthropic().messages.create(
        model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-5-5"),
        max_tokens=600,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(b.text for b in resp.content if b.type == "text")
