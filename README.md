# 🧙 De Poortwachter

Een eigen prompt-injection-spel in de stijl van Gandalf: 7 levels, en elk level is beter beveiligd dan het vorige.

## Starten

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open daarna http://localhost:5000

### Eigen wachtwoorden en instellingen

```bash
cp .env.example .env    # Windows: copy .env.example .env
```

Vul in `.env` je eigen wachtwoorden in (`POORTWACHTER_PW_1` t/m `_7`) en eventueel je API-key. `.env` staat in `.gitignore` en komt dus niet op GitHub. Laat je een wachtwoord leeg, dan gebruikt de app het voorbeeldwachtwoord uit `levels.py`. Dat is prima om zelf te testen, maar die voorbeelden zijn publiek.

### Model kiezen

| Provider | Instellen |
|---|---|
| **Ollama** (standaard, gratis, lokaal) | `ollama pull llama3.2` en laat Ollama draaien |
| OpenAI | `pip install openai`, `LLM_PROVIDER=openai`, `OPENAI_API_KEY=...`, eventueel `OPENAI_MODEL=...` |
| Anthropic | `pip install anthropic`, `LLM_PROVIDER=anthropic`, `ANTHROPIC_API_KEY=...`, eventueel `ANTHROPIC_MODEL=...` |
| Mock | `LLM_PROVIDER=mock`: lekt altijd alles, handig om je filters te testen |

Een ander Ollama-model kies je met `OLLAMA_MODEL=mistral` (of een ander model).

## De levels

| Level | Verdediging |
|---|---|
| 1 | Geen: het model geeft het wachtwoord gewoon |
| 2 | Alleen een instructie in de system prompt |
| 3 | + outputfilter (wachtwoord letterlijk in het antwoord → geblokkeerd) |
| 4 | + inputfilter op verdachte woorden |
| 5 | + fuzzy outputfilter (spaties, omgedraaid, beginletters/acrostichon) |
| 6 | + LLM-als-rechter: een tweede call die beoordeelt of er iets lekt |
| 7 | Alles tegelijk |

## Leren van je aanvallen

Elke poging komt in `attempts.jsonl` te staan, **inclusief het ongefilterde antwoord** van het model. Zo zie je welke verdediging je tegenhield en wat het model eigenlijk wilde zeggen. Prima materiaal voor een blogpost!

## Ideeën om verder te bouwen

- Een filter dat vertalingen, Base64 of ROT13 terugvertaalt voordat het controleert
- Multi-turn gesprekken (het geheugen maakt aanvallen vaak makkelijker)
- Een level waarin het model een "tool" heeft, zoals een nep-database, voor indirect prompt injection
- Een scorebord: hoeveel pogingen had je per level nodig?
- Vrienden laten spelen (zie hieronder)

## Online zetten?

Dat kan prima, met een paar voorzorgen. Stel je eigen wachtwoorden in als environment variables bij je hostingprovider, zet `FLASK_SECRET_KEY` vast, zet `debug=True` uit, voeg rate limiting toe (bijvoorbeeld met Flask-Limiter) en stel een uitgavenlimiet in bij je API-provider. Het log bevat wat spelers typen, dus vertel ze dat ook.
