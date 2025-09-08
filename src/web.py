from __future__ import annotations

from typing import Any, Dict, List

from flask import Flask, jsonify, redirect, render_template_string, request, url_for
import webbrowser
import os

from .intents import Intent
from .solver import default_registry_and_solver


app = Flask(__name__)

registry, solver = default_registry_and_solver()


INDEX_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Intent Demo</title>
    <style>
      body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, "Noto Sans", "Apple Color Emoji", "Segoe UI Emoji"; margin: 40px; }
      .card { max-width: 720px; padding: 24px; border: 1px solid #ddd; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
      label { display:block; margin: 12px 0 6px; font-weight: 600; }
      input[type=text] { width: 100%; padding: 10px 12px; border: 1px solid #ccc; border-radius: 8px; }
      .kv { display:flex; gap:8px; margin-bottom: 8px; }
      .row { margin-top: 12px; }
      button { margin-top: 16px; padding: 10px 14px; border: 0; background: #2d6cdf; color: white; border-radius: 8px; cursor: pointer; }
      .result { margin-top:16px; padding: 12px; background:#f6f8fa; border-radius:8px; }
      .muted { color:#666; font-size: 12px; }
    </style>
  </head>
  <body>
    <div class="card">
      <h2>Intent-centric Demo</h2>
      <form method="post" action="{{ url_for('solve_form') }}">
        <label>Intent name</label>
        <input type="text" name="name" placeholder="transfer | notify | swap" value="{{ name or '' }}" />

        <label>Tags (comma separated)</label>
        <input type="text" name="tags" placeholder="transfer,payment" value="{{ tags or '' }}" />

        <label>Params (key=value per line)</label>
        <div class="row">
          <textarea name="params" rows="6" style="width:100%; padding:10px 12px; border:1px solid #ccc; border-radius:8px;" placeholder="to=alice\namount=10"></textarea>
        </div>

        <div class="row">
          <label><input type="checkbox" name="explain" {% if explain %}checked{% endif %}/> Explain</label>
        </div>
        <button type="submit">Run Intent</button>
        <div class="muted">Built-in: transfer(to, amount), notify(to, text), swap(from_token, to_token, amount)</div>
      </form>

      {% if payload %}
      <div class="result">
        <div><strong>Result:</strong> {{ payload.result or 'No capability found.' }}</div>
        <pre class="muted">{{ payload.intent | tojson(indent=2) }}</pre>

        {% if payload.explain %}
        <div style="margin-top:8px;">
          <strong>Explain</strong>
          <div class="muted">chosen: {{ payload.explain.chosen_capability or 'None' }}</div>
          <pre class="muted">{{ payload.explain.ranking | tojson(indent=2) }}</pre>
        </div>
        {% endif %}
      </div>
      {% endif %}
    </div>
  </body>
  </html>
"""


def parse_kv_lines(text: str) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        try:
            if "." in value:
                params[key] = float(value)
            else:
                params[key] = int(value)
            continue
        except ValueError:
            pass
        params[key] = value
    return params


@app.get("/")
def index():
    return render_template_string(INDEX_HTML, payload=None, name="transfer", tags="transfer,payment", explain=False)


@app.post("/solve")
def solve_form():
    name = request.form.get("name", "").strip()
    tags_raw = request.form.get("tags", "").strip()
    params_raw = request.form.get("params", "").strip()
    tags: List[str] = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []
    params = parse_kv_lines(params_raw)
    want_explain = request.form.get("explain") is not None

    # Auto-infer tags from intent name if user did not provide tags
    if not tags:
        alias_to_tags = {
            "transfer": ["transfer", "payment"],
            "pay": ["transfer", "payment"],
            "notify": ["notify", "message"],
            "message": ["notify", "message"],
            "swap": ["swap", "trade"],
        }
        tags = alias_to_tags.get(name, [])

    intent = Intent(name=name, params=params, tags=tags)
    if want_explain:
        explained = solver.solve_with_explain(intent)
        payload = {"intent": intent.to_dict(), "result": explained.get("result"), "explain": explained}
    else:
        result = solver.solve(intent)
        payload = {"intent": intent.to_dict(), "result": result, "explain": None}
    return render_template_string(INDEX_HTML, payload=payload, name=name, tags=tags_raw, explain=want_explain)


@app.post("/api/solve")
def solve_api():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", ""))
    params = dict(data.get("params", {}))
    tags = list(data.get("tags", []))
    if not tags:
        alias_to_tags = {
            "transfer": ["transfer", "payment"],
            "pay": ["transfer", "payment"],
            "notify": ["notify", "message"],
            "message": ["notify", "message"],
            "swap": ["swap", "trade"],
        }
        tags = alias_to_tags.get(name, [])
    intent = Intent(name=name, params=params, tags=tags)
    if data.get("explain"):
        explained = solver.solve_with_explain(intent)
        return jsonify({"intent": intent.to_dict(), **explained})
    else:
        result = solver.solve(intent)
        return jsonify({"intent": intent.to_dict(), "result": result})


def main() -> int:
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    url = f"http://{host}:{port}"
    print(f"Starting app at {url}")
    try:
        if host in ("127.0.0.1", "localhost"):
            webbrowser.open_new(url)
    except Exception:
        pass
    app.run(host=host, port=port, debug=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



