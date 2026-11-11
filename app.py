import json
import os
import time

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from defenses import fuzzy_leak, input_blocked, judge_leak, literal_leak
from levels import GUARD_NAME, LEVELS
from llm import chat

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or os.urandom(32)

LOG_FILE = os.getenv("ATTEMPT_LOG", "attempts.jsonl")
MAX_INPUT = 1000

BLOCK_MSGS = {
    "input": "Ik zie heus wel wat je probeert... Daar praat ik niet over. 🧙",
    "output": "Oei, bijna verklapte ik iets! Dat antwoord houd ik voor mezelf.",
    "fuzzy": "Haha, slim trucje, maar ik zie de letters er toch in staan.",
    "judge": "Mijn collega-tovenaar fluistert dat ik dit beter niet kan zeggen.",
}


def unlocked() -> int:
    return session.get("unlocked", 1)


def get_level(data):
    try:
        n = int(data.get("level", 0))
    except (TypeError, ValueError):
        return None
    return LEVELS.get(n) if n <= unlocked() else None


def log_attempt(entry: dict) -> None:
    entry["ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


@app.get("/")
def index():
    return redirect(url_for("level_page", n=min(unlocked(), len(LEVELS))))


@app.get("/level/<int:n>")
def level_page(n):
    if n not in LEVELS or n > unlocked():
        return redirect(url_for("index"))
    return render_template("index.html", level=LEVELS[n], total=len(LEVELS),
                           unlocked=unlocked(), guard=GUARD_NAME)


@app.post("/api/chat")
def api_chat():
    data = request.get_json(silent=True) or {}
    lvl = get_level(data)
    message = str(data.get("message", "")).strip()[:MAX_INPUT]
    if lvl is None:
        return jsonify(error="Dit level is (nog) niet beschikbaar."), 403
    if not message:
        return jsonify(error="Typ eerst iets."), 400

    blocked, raw = None, None
    try:
        if lvl.input_filter and input_blocked(message):
            blocked = "input"
        else:
            raw = chat(lvl.system_prompt, message)
            if lvl.output_filter and literal_leak(raw, lvl.password):
                blocked = "output"
            elif lvl.fuzzy_filter and fuzzy_leak(raw, lvl.password):
                blocked = "fuzzy"
            elif lvl.llm_judge and judge_leak(raw, lvl.password):
                blocked = "judge"
    except Exception as e:  # noqa: BLE001 - toon modelfouten netjes in de UI
        return jsonify(error=f"Kon het model niet bereiken: {e}"), 502

    reply = BLOCK_MSGS[blocked] if blocked else raw
    # Het log bevat ook het ongefilterde antwoord: goud voor je analyse (en je blog!).
    log_attempt({"level": lvl.number, "message": message, "raw": raw, "blocked": blocked})
    return jsonify(reply=reply, blocked=blocked)


@app.post("/api/guess")
def api_guess():
    data = request.get_json(silent=True) or {}
    lvl = get_level(data)
    if lvl is None:
        return jsonify(error="Dit level is (nog) niet beschikbaar."), 403
    correct = str(data.get("guess", "")).strip().upper() == lvl.password.upper()
    log_attempt({"level": lvl.number, "guess": True, "correct": correct})
    if not correct:
        return jsonify(correct=False)
    session["unlocked"] = max(unlocked(), lvl.number + 1)
    done = lvl.number >= len(LEVELS)
    return jsonify(correct=True, done=done,
                   next=None if done else url_for("level_page", n=lvl.number + 1))


@app.post("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
