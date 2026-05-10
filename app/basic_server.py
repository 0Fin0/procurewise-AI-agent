from __future__ import annotations

import mimetypes
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse
import os
import sys


ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT / "app" / "static"
sys.path.insert(0, str(ROOT / "src"))

from procurewise import ProcureWiseAgent


SAMPLE_REQUEST = (
    "We need to buy a $42,000 annual subscription from CloudDesk AI for the "
    "Customer Success team. It will process customer emails and support tickets. "
    "Can we approve it this week?"
)

SAMPLES = {
    "cloud": {
        "label": "CloudDesk AI",
        "text": SAMPLE_REQUEST,
    },
    "office": {
        "label": "Office Supply",
        "text": "The office manager wants to purchase $3,200 of printer paper and desk supplies from PaperTrail Office Supply.",
    },
    "finance": {
        "label": "Northstar",
        "text": "Finance wants a $155,000 analytics platform from Northstar Analytics that will analyze customer revenue and payment trends.",
    },
    "marketing": {
        "label": "BrightWave",
        "text": "Marketing wants to hire BrightWave Events for a $18,500 launch event and upload attendee contact lists.",
    },
}


def money(value: object) -> str:
    if value in (None, "", "None"):
        return "Not detected"
    try:
        return f"${float(value):,.0f}"
    except (TypeError, ValueError):
        return str(value)


def tool_details(result, name: str) -> dict:
    if not result:
        return {}
    for tool in result.tool_results:
        if tool.name == name:
            return tool.details
    return {}


class ProcureWiseHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/static/"):
            self._send_static(parsed.path)
            return

        query = parse_qs(parsed.query)
        sample_key = query.get("sample", ["cloud"])[0]
        request_text = SAMPLES.get(sample_key, SAMPLES["cloud"])["text"]
        self._send_page(request_text=request_text)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        form = parse_qs(body)
        request_text = form.get("request_text", [""])[0]
        create_case = form.get("create_case", ["off"])[0] == "on"
        result = None
        error = None
        if request_text.strip():
            try:
                result = ProcureWiseAgent().run(request_text, create_case=create_case)
            except Exception as exc:
                error = str(exc)
        self._send_page(request_text=request_text, result=result, error=error, create_case=create_case)

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send_static(self, request_path: str) -> None:
        relative = request_path.removeprefix("/static/").lstrip("/")
        file_path = (STATIC_DIR / relative).resolve()
        try:
            file_path.relative_to(STATIC_DIR.resolve())
        except ValueError:
            self.send_error(404)
            return

        if not file_path.is_file():
            self.send_error(404)
            return

        content = file_path.read_bytes()
        content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(content)

    def _send_page(
        self,
        request_text: str,
        result=None,
        error: str | None = None,
        create_case: bool = True,
    ) -> None:
        html = self._render_page(request_text, result, error, create_case)
        encoded = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _sample_buttons(self) -> str:
        return "".join(
            f'<a class="scenario-link" href="/?{urlencode({"sample": key})}">{escape(sample["label"])}</a>'
            for key, sample in SAMPLES.items()
        )

    def _render_page(
        self,
        request_text: str,
        result=None,
        error: str | None = None,
        create_case: bool = True,
    ) -> str:
        checked = "checked" if create_case else ""
        result_html = self._result_html(result, error)
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ProcureWise Agent</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #0d1117;
      --shell: #0f1b2f;
      --shell-2: #16243a;
      --surface: #171d27;
      --surface-alt: #202735;
      --ink: #f4f7fb;
      --muted: #9aa8bb;
      --line: rgba(148, 163, 184, 0.22);
      --teal: #20d4bb;
      --teal-dark: #12b8a5;
      --teal-soft: rgba(32, 212, 187, 0.15);
      --blue: #5aa2ff;
      --blue-soft: rgba(90, 162, 255, 0.15);
      --amber: #f6c96d;
      --amber-soft: rgba(246, 201, 109, 0.14);
      --red: #ff8c8c;
      --red-soft: rgba(255, 140, 140, 0.14);
      --green: #35e8a6;
      --green-soft: rgba(53, 232, 166, 0.14);
      --shadow: 0 24px 56px rgba(0, 0, 0, 0.34);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
      background:
        radial-gradient(circle at 82% 8%, rgba(32, 212, 187, 0.14), transparent 360px),
        radial-gradient(circle at 28% 18%, rgba(90, 162, 255, 0.10), transparent 300px),
        linear-gradient(180deg, #121923 0, var(--bg) 420px);
      color: var(--ink);
    }}
    .app-shell {{
      min-height: 100vh;
      display: grid;
      grid-template-columns: 248px minmax(0, 1fr);
    }}
    .rail {{
      background:
        linear-gradient(180deg, rgba(18, 35, 59, 0.98), rgba(13, 25, 43, 0.98)),
        var(--shell);
      color: #d9e4ef;
      padding: 18px 14px;
      display: flex;
      flex-direction: column;
      gap: 18px;
      border-right: 1px solid rgba(148, 163, 184, 0.14);
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 11px;
      padding: 4px 6px 12px;
      border-bottom: 1px solid rgba(255,255,255,0.12);
    }}
    .brand-logo {{
      width: 38px;
      height: 38px;
      border-radius: 8px;
      object-fit: cover;
      border: 1px solid rgba(255,255,255,0.26);
      box-shadow: 0 8px 18px rgba(0,0,0,0.18);
      background: #ffffff;
    }}
    .brand strong {{
      display: block;
      color: #ffffff;
      font-size: 16px;
      line-height: 1.1;
    }}
    .brand span {{
      color: #9fb0c4;
      font-size: 12px;
    }}
    .nav {{
      display: grid;
      gap: 6px;
    }}
    .nav-item {{
      display: flex;
      align-items: center;
      gap: 10px;
      min-height: 38px;
      padding: 8px 10px;
      border-radius: 7px;
      color: #d9e4ef;
      font-weight: 700;
      font-size: 14px;
    }}
    .nav-item.active {{
      background: linear-gradient(135deg, rgba(32, 212, 187, 0.25), rgba(90, 162, 255, 0.15));
      color: #ffffff;
      box-shadow: inset 0 0 0 1px rgba(32, 212, 187, 0.18);
    }}
    .nav-icon {{
      width: 20px;
      height: 20px;
      display: grid;
      place-items: center;
      border-radius: 6px;
      background: rgba(255,255,255,0.10);
      font-size: 12px;
      font-weight: 900;
    }}
    .rail-footer {{
      margin-top: auto;
      padding: 12px 10px;
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 8px;
      background: rgba(255,255,255,0.07);
    }}
    .rail-footer span {{
      display: block;
      color: #9fb0c4;
      font-size: 12px;
      margin-bottom: 4px;
    }}
    .rail-footer strong {{
      display: block;
      color: #ffffff;
      font-size: 14px;
    }}
    main {{
      min-width: 0;
      width: 100%;
      max-width: none;
      margin: 0;
      padding: 24px 30px;
    }}
    .topbar {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
      margin-bottom: 18px;
    }}
    h1 {{
      margin: 0;
      font-size: 30px;
      line-height: 1.12;
      letter-spacing: 0;
    }}
    .subhead {{
      margin: 4px 0 0;
      color: var(--muted);
      font-size: 14px;
    }}
    .status-row {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }}
    .status-chip {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      min-height: 34px;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 7px 11px;
      background: rgba(23, 29, 39, 0.82);
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
      white-space: nowrap;
    }}
    .dot {{
      width: 8px;
      height: 8px;
      border-radius: 999px;
      background: var(--green);
    }}
    .command-strip {{
      display: grid;
      grid-template-columns: minmax(0, 1.4fr) repeat(3, minmax(130px, 0.42fr));
      gap: 12px;
      margin-bottom: 18px;
    }}
    .queue-card, .queue-metric {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: linear-gradient(145deg, rgba(31, 39, 53, 0.94), rgba(20, 26, 36, 0.94));
      box-shadow: 0 18px 38px rgba(0, 0, 0, 0.22);
      padding: 14px 16px;
    }}
    .queue-card {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }}
    .queue-card h2 {{
      margin: 0;
      font-size: 17px;
      letter-spacing: 0;
    }}
    .queue-card p {{
      margin: 4px 0 0;
      color: var(--muted);
      line-height: 1.45;
    }}
    .queue-pill {{
      flex: 0 0 auto;
      border-radius: 999px;
      background: rgba(32, 212, 187, 0.16);
      color: #7cf8e8;
      padding: 7px 10px;
      font-weight: 900;
      font-size: 12px;
      white-space: nowrap;
    }}
    .queue-metric span {{
      display: block;
      color: var(--muted);
      font-size: 11px;
      font-weight: 900;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      margin-bottom: 6px;
    }}
    .queue-metric strong {{
      display: block;
      font-size: 20px;
      letter-spacing: 0;
      color: var(--teal);
    }}
    .workbench {{
      display: grid;
      grid-template-columns: minmax(420px, 0.74fr) minmax(0, 1.26fr);
      gap: 18px;
      align-items: start;
    }}
    .intake-column {{
      display: grid;
      gap: 14px;
      position: sticky;
      top: 24px;
    }}
    .panel {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }}
    .panel-head {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 16px 18px;
      border-bottom: 1px solid var(--line);
    }}
    .panel-title {{
      margin: 0;
      font-size: 16px;
      letter-spacing: 0;
    }}
    .panel-kicker {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }}
    form.request-form {{
      display: grid;
      gap: 14px;
      padding: 18px;
    }}
    textarea {{
      width: 100%;
      min-height: 214px;
      resize: vertical;
      border: 1px solid var(--line);
      border-radius: 7px;
      padding: 14px;
      font: inherit;
      line-height: 1.5;
      color: var(--ink);
      background: var(--surface-alt);
      outline: none;
    }}
    textarea:focus {{
      border-color: var(--teal);
      box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.14);
    }}
    .form-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }}
    button {{
      border: 0;
      border-radius: 7px;
      background: linear-gradient(135deg, var(--teal), var(--blue));
      color: #ffffff;
      min-height: 42px;
      padding: 11px 16px;
      font-weight: 800;
      cursor: pointer;
      box-shadow: 0 12px 28px rgba(32, 212, 187, 0.18);
    }}
    button:hover {{ filter: brightness(1.08); }}
    label.toggle {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      color: var(--muted);
      font-size: 14px;
      font-weight: 700;
    }}
    input[type="checkbox"] {{
      width: 18px;
      height: 18px;
      accent-color: var(--teal);
    }}
    .scenario-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
      padding-top: 2px;
    }}
    .scenario-link {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      min-height: 36px;
      border: 1px solid var(--line);
      border-radius: 7px;
      padding: 8px 10px;
      color: var(--ink);
      background: rgba(255,255,255,0.03);
      text-decoration: none;
      font-size: 13px;
      font-weight: 800;
    }}
    .scenario-link:hover {{
      border-color: var(--teal);
      color: #7cf8e8;
      background: var(--teal-soft);
    }}
    .scenario-link::after {{
      content: "Load";
      color: var(--muted);
      font-size: 11px;
      font-weight: 900;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .coverage-panel .section-body {{
      padding-top: 14px;
    }}
    .coverage-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }}
    .coverage-item {{
      border: 1px solid var(--line);
      border-radius: 7px;
      background: var(--surface-alt);
      padding: 11px;
    }}
    .coverage-item span {{
      display: block;
      color: var(--muted);
      font-size: 11px;
      font-weight: 900;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      margin-bottom: 5px;
    }}
    .coverage-item strong {{
      display: block;
      font-size: 14px;
    }}
    .snapshot {{
      padding: 16px 18px 18px;
      display: grid;
      gap: 10px;
      border-top: 1px solid var(--line);
    }}
    .snapshot-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }}
    .snapshot-item {{
      border: 1px solid var(--line);
      border-radius: 7px;
      padding: 11px;
      background: var(--surface-alt);
    }}
    .snapshot-item span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      margin-bottom: 4px;
    }}
    .snapshot-item strong {{
      font-size: 16px;
      overflow-wrap: anywhere;
    }}
    .empty-state {{
      min-height: 540px;
      padding: 28px;
      background:
        radial-gradient(circle at 68% 10%, rgba(32, 212, 187, 0.10), transparent 320px),
        linear-gradient(145deg, rgba(23, 29, 39, 0.98) 0%, rgba(15, 20, 30, 0.98) 100%);
    }}
    .empty-state .seal {{
      width: 58px;
      height: 58px;
      display: grid;
      place-items: center;
      border-radius: 8px;
      color: #ffffff;
      background: var(--teal);
      font-weight: 900;
      font-size: 19px;
    }}
    .empty-state h2 {{
      margin: 0;
      font-size: 23px;
    }}
    .empty-state p {{
      margin: 0;
      max-width: 520px;
      color: var(--muted);
      line-height: 1.55;
    }}
    .empty-art {{
      display: block;
      width: min(860px, 100%);
      aspect-ratio: 16 / 9;
      object-fit: cover;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #ffffff;
      box-shadow: 0 24px 55px rgba(0, 0, 0, 0.28);
      margin: 0 auto 22px;
      opacity: 0.92;
      filter: saturate(0.88) brightness(0.92);
    }}
    .empty-intro {{
      display: grid;
      gap: 12px;
      max-width: 860px;
      margin-left: auto;
      margin-right: auto;
      margin-bottom: 24px;
    }}
    .empty-intro .seal {{
      display: none;
    }}
    .empty-flow {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      max-width: 860px;
      margin-left: auto;
      margin-right: auto;
    }}
    .empty-step {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255,255,255,0.035);
      padding: 14px;
    }}
    .empty-step span {{
      display: inline-grid;
      place-items: center;
      width: 28px;
      height: 28px;
      border-radius: 999px;
      background: var(--teal-soft);
      color: #7cf8e8;
      font-weight: 900;
      margin-bottom: 10px;
    }}
    .empty-step strong {{
      display: block;
      margin-bottom: 4px;
      font-size: 15px;
    }}
    .empty-step p {{
      font-size: 13px;
      line-height: 1.45;
    }}
    .result-stack {{
      display: grid;
      gap: 14px;
    }}
    .decision-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      padding: 14px;
    }}
    .metric {{
      border: 1px solid var(--line);
      border-radius: 7px;
      padding: 12px;
      background: var(--surface-alt);
      min-width: 0;
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      margin-bottom: 6px;
    }}
    .metric strong {{
      display: block;
      font-size: 19px;
      overflow-wrap: anywhere;
    }}
    .case-value {{
      display: flex !important;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .case-success {{
      display: inline-flex;
      align-items: center;
      min-height: 22px;
      border-radius: 999px;
      padding: 4px 8px;
      background: var(--green-soft);
      color: var(--green);
      font-size: 12px;
      font-style: normal;
      font-weight: 900;
    }}
    .risk-pill {{
      width: fit-content;
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 15px !important;
    }}
    .risk-low {{ color: var(--green); background: var(--green-soft); }}
    .risk-medium {{ color: var(--amber); background: var(--amber-soft); }}
    .risk-high {{ color: var(--red); background: var(--red-soft); }}
    .recommendation {{
      padding: 18px;
    }}
    .recommendation p {{
      margin: 0;
      font-size: 16px;
      line-height: 1.62;
    }}
    .approval-band {{
      margin-top: 14px;
      border: 1px solid rgba(90, 162, 255, 0.32);
      border-radius: 7px;
      background: var(--blue-soft);
      padding: 13px;
      color: #b8d5ff;
      font-weight: 800;
    }}
    .section-body {{
      padding: 16px 18px 18px;
    }}
    .steps {{
      display: grid;
      gap: 10px;
      padding: 0;
      margin: 0;
      list-style: none;
    }}
    .steps li {{
      display: grid;
      grid-template-columns: 32px 1fr;
      gap: 10px;
      line-height: 1.45;
    }}
    .step-index {{
      width: 32px;
      height: 32px;
      display: grid;
      place-items: center;
      border-radius: 999px;
      color: #7cf8e8;
      background: var(--teal-soft);
      font-weight: 900;
    }}
    .evidence-list {{
      display: grid;
      gap: 10px;
    }}
    .evidence-item {{
      border: 1px solid var(--line);
      border-radius: 7px;
      padding: 12px;
      background: var(--surface-alt);
    }}
    .evidence-item header {{
      display: flex;
      justify-content: space-between;
      gap: 10px;
      flex-wrap: wrap;
      margin-bottom: 8px;
    }}
    .evidence-item strong {{
      font-size: 15px;
    }}
    .evidence-item span {{
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
    }}
    .evidence-item p {{
      margin: 0;
      color: #d9e2ee;
      line-height: 1.5;
    }}
    .table-wrap {{
      width: 100%;
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 7px;
    }}
    .trace-panel {{
      overflow: hidden;
    }}
    .trace-panel summary {{
      cursor: pointer;
      list-style: none;
    }}
    .trace-panel summary::-webkit-details-marker {{
      display: none;
    }}
    .trace-toggle {{
      display: inline-flex;
      align-items: center;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 7px 10px;
      color: #7cf8e8;
      background: var(--teal-soft);
      font-size: 12px;
      font-weight: 900;
    }}
    .trace-toggle::after {{
      content: "Show audit log";
    }}
    .trace-panel[open] .trace-toggle::after {{
      content: "Hide audit log";
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--surface);
      font-size: 13px;
    }}
    th {{
      background: var(--surface-alt);
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    th, td {{
      border-top: 1px solid var(--line);
      padding: 9px;
      text-align: left;
      vertical-align: top;
    }}
    thead th {{ border-top: 0; }}
    code {{
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      color: #d9e2ee;
      font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
      font-size: 12px;
    }}
    .notice {{
      padding: 16px;
      border: 1px solid #f0b7b7;
      border-radius: 8px;
      background: var(--red-soft);
      color: var(--red);
      font-weight: 800;
    }}
    .app-footer {{
      margin-top: 24px;
      padding: 12px 2px 4px;
      color: var(--muted);
      font-size: 12px;
      text-align: right;
    }}
    @media (max-width: 1120px) {{
      .app-shell {{ grid-template-columns: 1fr; }}
      .rail {{
        position: static;
        display: block;
      }}
      .brand {{ border-bottom: 0; }}
      .nav, .rail-footer {{ display: none; }}
      main {{ padding: 18px; }}
      .workbench {{ grid-template-columns: 1fr; }}
      .intake-column {{ position: static; }}
    }}
    @media (max-width: 760px) {{
      main {{ padding: 12px; }}
      .topbar {{ align-items: flex-start; flex-direction: column; }}
      .status-row {{ justify-content: flex-start; }}
      .command-strip {{ grid-template-columns: 1fr; }}
      .queue-card {{ align-items: flex-start; flex-direction: column; }}
      .decision-grid, .snapshot-grid, .scenario-grid, .coverage-grid, .empty-flow {{ grid-template-columns: 1fr; }}
      h1 {{ font-size: 26px; }}
      textarea {{ min-height: 180px; }}
    }}
  </style>
</head>
<body>
  <div class="app-shell">
    <aside class="rail">
      <div class="brand">
        <img class="brand-logo" src="/static/procurewise-logo.jpg" alt="ProcureWise logo">
        <div>
          <strong>ProcureWise</strong>
          <span>Risk Triage</span>
        </div>
      </div>
      <nav class="nav" aria-label="Workspace">
        <div class="nav-item active"><span class="nav-icon">R</span>Review</div>
        <div class="nav-item"><span class="nav-icon">V</span>Vendors</div>
        <div class="nav-item"><span class="nav-icon">P</span>Policy</div>
        <div class="nav-item"><span class="nav-icon">C</span>Cases</div>
      </nav>
      <div class="rail-footer">
        <span>Mode</span>
        <strong>RAG + tool workflow</strong>
      </div>
    </aside>
    <main>
      <header class="topbar">
        <div>
          <h1>Procurement Review Workbench</h1>
          <p class="subhead">Track A AI Agent | ISYS 573</p>
        </div>
        <div class="status-row">
          <div class="status-chip"><span class="dot"></span>Agent ready</div>
          <div class="status-chip">Docker tested</div>
        </div>
      </header>
      <section class="command-strip" aria-label="Review status">
        <div class="queue-card">
          <div>
            <h2>Active purchase review</h2>
            <p>Policy sources, vendor records, approval rules, and case output are connected for the demo.</p>
          </div>
          <span class="queue-pill">Demo ready</span>
        </div>
        <div class="queue-metric"><span>Policy sources</span><strong>4</strong></div>
        <div class="queue-metric"><span>Vendor records</span><strong>5</strong></div>
        <div class="queue-metric"><span>Case writer</span><strong>On</strong></div>
      </section>
      <section class="workbench">
        <div class="intake-column">
          <div class="panel">
            <div class="panel-head">
              <div>
                <span class="panel-kicker">Intake</span>
                <h2 class="panel-title">Purchase Request</h2>
              </div>
            </div>
            <form class="request-form" method="post">
              <textarea id="request_text" name="request_text" aria-label="Purchase request">{escape(request_text)}</textarea>
              <div class="scenario-grid">{self._sample_buttons()}</div>
              <div class="form-row">
                <button type="submit">Analyze request</button>
                <label class="toggle"><input type="checkbox" name="create_case" {checked}> Create case file</label>
              </div>
            </form>
          </div>
          <section class="panel coverage-panel">
            <div class="panel-head">
              <div>
                <span class="panel-kicker">Package</span>
                <h2 class="panel-title">Review Coverage</h2>
              </div>
            </div>
            <div class="section-body">
              <div class="coverage-grid">
                <div class="coverage-item"><span>Evidence</span><strong>Policy matches</strong></div>
                <div class="coverage-item"><span>Vendor</span><strong>Risk profile</strong></div>
                <div class="coverage-item"><span>Approval</span><strong>Routing path</strong></div>
                <div class="coverage-item"><span>Audit</span><strong>Tool trace</strong></div>
              </div>
            </div>
          </section>
        </div>
        {result_html}
      </section>
      <footer class="app-footer">ProcureWise Agent | ISYS 573 Group Project</footer>
    </main>
  </div>
</body>
</html>"""

    def _result_html(self, result, error: str | None) -> str:
        if error:
            return f'<section class="panel"><div class="section-body"><div class="notice">{escape(error)}</div></div></section>'

        if not result:
            return """
            <section class="panel empty-state">
              <img class="empty-art" src="/static/procurewise-empty-state.jpg" alt="Procurement review workflow illustration">
              <div class="empty-intro">
                <div class="seal">PW</div>
                <h2>Review queue is ready</h2>
                <p>The agent is staged to read the request, retrieve policy evidence, check vendor risk, route approval, and create a case record.</p>
              </div>
              <div class="empty-flow">
                <article class="empty-step"><span>1</span><strong>Parse Request</strong><p>Finds vendor, amount, team, category, and data sensitivity.</p></article>
                <article class="empty-step"><span>2</span><strong>Retrieve Evidence</strong><p>Matches the request against procurement, security, and approval policy.</p></article>
                <article class="empty-step"><span>3</span><strong>Run Tools</strong><p>Checks vendor profile, approval path, risk score, and case output.</p></article>
                <article class="empty-step"><span>4</span><strong>Draft Decision</strong><p>Returns a recommendation, next steps, policy matches, and audit trace.</p></article>
              </div>
            </section>
            """

        facts = tool_details(result, "request_parser")
        vendor = tool_details(result, "vendor_lookup")
        risk = tool_details(result, "risk_scorer")
        risk_class = f"risk-{escape(result.risk_level.lower())}"
        vendor_label = vendor.get("name") or facts.get("vendor") or "Not found"
        vendor_risk = vendor.get("risk_rating") or "Needs review"
        data_flag = "Yes" if facts.get("handles_sensitive_data") else "No"
        risk_score = risk.get("score", "-")
        case_value = escape(result.case_id or "Not created")
        case_badge = '<em class="case-success">Created</em>' if result.case_id else ""

        steps = "".join(
            f'<li><span class="step-index">{index}</span><span>{escape(step)}</span></li>'
            for index, step in enumerate(result.next_steps, start=1)
        )
        evidence = "".join(
            f"""
            <article class="evidence-item">
              <header>
                <strong>{escape(item.heading)}</strong>
                <span>{escape(item.source)}</span>
              </header>
              <p>{escape(item.text)}</p>
            </article>
            """
            for item in result.policy_evidence
        )
        tools = "".join(
            f"<tr><td>{escape(tool.name)}</td><td>{escape(tool.status)}</td><td><code>{escape(str(tool.details))}</code></td></tr>"
            for tool in result.tool_results
        )

        return f"""
        <div class="result-stack">
          <section class="panel">
            <div class="panel-head">
              <div>
                <span class="panel-kicker">Decision</span>
                <h2 class="panel-title">Review Summary</h2>
              </div>
            </div>
            <div class="decision-grid">
              <div class="metric"><span>Risk</span><strong class="risk-pill {risk_class}">{escape(result.risk_level.title())}</strong></div>
              <div class="metric"><span>Score</span><strong>{escape(str(risk_score))}</strong></div>
              <div class="metric"><span>Evidence</span><strong>{len(result.policy_evidence)} passages</strong></div>
              <div class="metric"><span>Case</span><strong class="case-value">{case_value}{case_badge}</strong></div>
            </div>
            <div class="recommendation">
              <p>{escape(result.recommendation)}</p>
              <div class="approval-band">{escape(result.approval_path)}</div>
            </div>
          </section>
          <section class="panel">
            <div class="panel-head">
              <div>
                <span class="panel-kicker">Facts</span>
                <h2 class="panel-title">Request Snapshot</h2>
              </div>
            </div>
            <div class="snapshot">
              <div class="snapshot-grid">
                <div class="snapshot-item"><span>Vendor</span><strong>{escape(str(vendor_label))}</strong></div>
                <div class="snapshot-item"><span>Vendor risk</span><strong>{escape(str(vendor_risk))}</strong></div>
                <div class="snapshot-item"><span>Amount</span><strong>{escape(money(facts.get("amount")))}</strong></div>
                <div class="snapshot-item"><span>Sensitive data</span><strong>{data_flag}</strong></div>
              </div>
            </div>
          </section>
          <section class="panel">
            <div class="panel-head">
              <div>
                <span class="panel-kicker">Action</span>
                <h2 class="panel-title">Next Steps</h2>
              </div>
            </div>
            <div class="section-body"><ol class="steps">{steps}</ol></div>
          </section>
          <section class="panel">
            <div class="panel-head">
              <div>
                <span class="panel-kicker">Evidence</span>
                <h2 class="panel-title">Policy Matches</h2>
              </div>
            </div>
            <div class="section-body"><div class="evidence-list">{evidence}</div></div>
          </section>
          <details class="panel trace-panel">
            <summary class="panel-head">
              <div>
                <span class="panel-kicker">Audit</span>
                <h2 class="panel-title">Tool Trace</h2>
              </div>
              <span class="trace-toggle"></span>
            </summary>
            <div class="section-body">
              <div class="table-wrap">
                <table><thead><tr><th>Tool</th><th>Status</th><th>Details</th></tr></thead><tbody>{tools}</tbody></table>
              </div>
            </div>
          </details>
        </div>
        """


def main() -> None:
    port = int(os.getenv("PORT", "8502"))
    host = os.getenv("HOST", "127.0.0.1")
    server = ThreadingHTTPServer((host, port), ProcureWiseHandler)
    print(f"ProcureWise UI running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
