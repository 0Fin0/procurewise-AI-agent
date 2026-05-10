from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse
import os
import sys


ROOT = Path(__file__).resolve().parents[1]
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
        "label": "Office Supplies",
        "text": "The office manager wants to purchase $3,200 of printer paper and desk supplies from PaperTrail Office Supply.",
    },
    "finance": {
        "label": "Northstar Analytics",
        "text": "Finance wants a $155,000 analytics platform from Northstar Analytics that will analyze customer revenue and payment trends.",
    },
    "marketing": {
        "label": "BrightWave Events",
        "text": "Marketing wants to hire BrightWave Events for a $18,500 launch event and upload attendee contact lists.",
    },
}


class ProcureWiseHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        query = parse_qs(urlparse(self.path).query)
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
        self._send_page(request_text=request_text, result=result, error=error)

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send_page(self, request_text: str, result=None, error: str | None = None) -> None:
        html = self._render_page(request_text, result, error)
        encoded = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _render_page(self, request_text: str, result=None, error: str | None = None) -> str:
        sample_buttons = "".join(
            f'<a class="sample-button" href="/?{urlencode({"sample": key})}">{escape(sample["label"])}</a>'
            for key, sample in SAMPLES.items()
        )
        result_html = ""
        if error:
            result_html = f"""
            <section class="notice error">
              <strong>Request failed</strong>
              <p>{escape(error)}</p>
            </section>
            """
        elif result:
            risk_class = f"risk-{escape(result.risk_level.lower())}"
            case_value = escape(result.case_id or "Not created")
            evidence = "".join(
                f"""
                <article class="evidence-item">
                  <div>
                    <strong>{escape(item.heading)}</strong>
                    <span>{escape(item.source)}</span>
                  </div>
                  <p>{escape(item.text)}</p>
                </article>
                """
                for item in result.policy_evidence
            )
            steps = "".join(
                f"""
                <li>
                  <span class="step-index">{index}</span>
                  <span>{escape(step)}</span>
                </li>
                """
                for index, step in enumerate(result.next_steps, start=1)
            )
            tools = "".join(
                f"<tr><td>{escape(tool.name)}</td><td>{escape(tool.status)}</td>"
                f"<td><code>{escape(str(tool.details))}</code></td></tr>"
                for tool in result.tool_results
            )
            result_html = f"""
            <section class="decision-strip">
              <div>
                <span class="eyebrow">Risk level</span>
                <strong class="risk-pill {risk_class}">{escape(result.risk_level.title())}</strong>
              </div>
              <div>
                <span class="eyebrow">Policy evidence</span>
                <strong>{len(result.policy_evidence)} passages</strong>
              </div>
              <div>
                <span class="eyebrow">Case</span>
                <strong>{case_value}</strong>
              </div>
            </section>
            <section class="result-grid">
              <article class="primary-result">
                <span class="eyebrow">Recommendation</span>
                <p>{escape(result.recommendation)}</p>
              </article>
              <article class="approval-result">
                <span class="eyebrow">Approval path</span>
                <p>{escape(result.approval_path)}</p>
              </article>
            </section>
            <section class="content-section">
              <div class="section-heading">
                <h2>Next Steps</h2>
              </div>
              <ol class="steps">{steps}</ol>
            </section>
            <section class="content-section">
              <div class="section-heading">
                <h2>Policy Evidence</h2>
              </div>
              <div class="evidence-list">{evidence}</div>
            </section>
            <section class="content-section">
              <div class="section-heading">
                <h2>Tool Trace</h2>
              </div>
              <div class="table-wrap">
                <table><thead><tr><th>Tool</th><th>Status</th><th>Details</th></tr></thead><tbody>{tools}</tbody></table>
              </div>
            </section>
            """

        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ProcureWise Agent</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f5f7fa;
      --surface: #ffffff;
      --surface-alt: #f9fafb;
      --ink: #182132;
      --muted: #65758b;
      --line: #dce3ea;
      --line-strong: #c5ceda;
      --accent: #116466;
      --accent-dark: #0b4b4d;
      --accent-soft: #e4f2f1;
      --blue: #2454a6;
      --blue-soft: #e8eefb;
      --amber: #9a5a00;
      --amber-soft: #fff4df;
      --red: #a23a3a;
      --red-soft: #fff1f1;
      --green: #177245;
      --green-soft: #e8f5ee;
      --panel: #ffffff;
      --shadow: 0 18px 50px rgba(24, 33, 50, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
      background:
        linear-gradient(180deg, #eef4f8 0, rgba(238, 244, 248, 0) 340px),
        var(--bg);
      color: var(--ink);
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 24px 18px 52px;
    }}
    .topbar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 22px;
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 0;
    }}
    .brand-mark {{
      width: 44px;
      height: 44px;
      display: grid;
      place-items: center;
      border-radius: 8px;
      background: var(--accent);
      color: #ffffff;
      font-weight: 800;
      letter-spacing: 0;
    }}
    .brand-copy {{
      min-width: 0;
    }}
    h1 {{
      margin: 0;
      font-size: 30px;
      line-height: 1.1;
      letter-spacing: 0;
    }}
    .subtitle {{
      margin: 3px 0 0;
      color: var(--muted);
      font-size: 14px;
    }}
    h2 {{
      margin: 0;
      font-size: 17px;
      line-height: 1.2;
      letter-spacing: 0;
    }}
    .status-chip {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      min-height: 34px;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 7px 12px;
      background: rgba(255, 255, 255, 0.74);
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }}
    .status-dot {{
      width: 8px;
      height: 8px;
      border-radius: 999px;
      background: var(--green);
    }}
    .workspace {{
      display: grid;
      grid-template-columns: minmax(0, 1.3fr) minmax(280px, 0.7fr);
      gap: 18px;
      align-items: start;
    }}
    .request-panel, .side-panel, .content-section, .primary-result, .approval-result, .decision-strip {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }}
    .request-panel {{
      padding: 18px;
      display: grid;
      gap: 14px;
    }}
    .panel-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }}
    .field-label {{
      font-size: 13px;
      color: var(--muted);
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    textarea {{
      width: 100%;
      min-height: 210px;
      resize: vertical;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 14px;
      font: inherit;
      line-height: 1.5;
      color: var(--ink);
      background: var(--surface-alt);
      outline: none;
    }}
    textarea:focus {{
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(17, 100, 102, 0.13);
    }}
    .actions {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
    }}
    .action-left {{
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
    }}
    button {{
      border: 0;
      border-radius: 6px;
      background: var(--accent);
      color: white;
      min-height: 42px;
      padding: 11px 16px;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 10px 22px rgba(17, 100, 102, 0.2);
    }}
    button:hover {{ background: var(--accent-dark); }}
    label {{
      color: var(--muted);
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
    }}
    input[type="checkbox"] {{
      width: 18px;
      height: 18px;
      accent-color: var(--accent);
    }}
    .sample-row {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .sample-button {{
      display: inline-flex;
      align-items: center;
      min-height: 34px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px 10px;
      color: var(--ink);
      background: #ffffff;
      text-decoration: none;
      font-size: 13px;
      font-weight: 700;
    }}
    .sample-button:hover {{
      border-color: var(--accent);
      color: var(--accent-dark);
    }}
    .side-panel {{
      padding: 16px;
      display: grid;
      gap: 12px;
    }}
    .side-list {{
      display: grid;
      gap: 10px;
      margin: 0;
      padding: 0;
      list-style: none;
    }}
    .side-list li {{
      display: grid;
      grid-template-columns: 30px 1fr;
      gap: 10px;
      align-items: start;
      margin: 0;
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--surface-alt);
    }}
    .side-list span {{
      width: 30px;
      height: 30px;
      display: grid;
      place-items: center;
      border-radius: 6px;
      background: var(--blue-soft);
      color: var(--blue);
      font-weight: 800;
      font-size: 13px;
    }}
    .side-list strong {{
      display: block;
      margin-bottom: 2px;
      font-size: 14px;
    }}
    .side-list p {{
      margin: 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.35;
    }}
    .decision-strip {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 1px;
      overflow: hidden;
      margin-top: 18px;
      background: var(--line);
    }}
    .decision-strip > div {{
      padding: 16px;
      background: #ffffff;
      min-width: 0;
    }}
    .eyebrow {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      margin-bottom: 6px;
    }}
    .decision-strip strong {{
      display: block;
      font-size: 20px;
      overflow-wrap: anywhere;
    }}
    .risk-pill {{
      width: fit-content;
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 16px !important;
    }}
    .risk-low {{ color: var(--green); background: var(--green-soft); }}
    .risk-medium {{ color: var(--amber); background: var(--amber-soft); }}
    .risk-high {{ color: var(--red); background: var(--red-soft); }}
    .result-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.25fr) minmax(260px, 0.75fr);
      gap: 14px;
      margin-top: 14px;
    }}
    .primary-result, .approval-result, .content-section {{
      padding: 18px;
    }}
    .primary-result p, .approval-result p {{
      margin: 0;
      line-height: 1.6;
      font-size: 16px;
    }}
    .approval-result {{
      background: var(--blue-soft);
      border-color: #c8d5ef;
    }}
    .content-section {{
      margin-top: 14px;
    }}
    .section-heading {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }}
    .steps {{
      display: grid;
      gap: 10px;
      list-style: none;
      padding: 0;
      margin: 0;
    }}
    .steps li {{
      display: grid;
      grid-template-columns: 32px 1fr;
      gap: 10px;
      align-items: start;
      margin: 0;
      line-height: 1.45;
    }}
    .step-index {{
      width: 32px;
      height: 32px;
      display: grid;
      place-items: center;
      border-radius: 999px;
      color: var(--accent-dark);
      background: var(--accent-soft);
      font-weight: 800;
    }}
    .evidence-list {{
      display: grid;
      gap: 10px;
    }}
    .evidence-item {{
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 12px;
      background: var(--surface-alt);
    }}
    .evidence-item div {{
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
    }}
    .evidence-item p {{
      margin: 0;
      color: #2d394c;
      line-height: 1.5;
    }}
    .notice {{
      margin-top: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      background: #ffffff;
    }}
    .error {{
      border-color: #f0b7b7;
      background: var(--red-soft);
      color: var(--red);
    }}
    .table-wrap {{
      width: 100%;
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 6px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
      background: #ffffff;
    }}
    th {{
      background: var(--surface-alt);
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    th, td {{
      border-top: 1px solid var(--line);
      padding: 10px;
      text-align: left;
      vertical-align: top;
    }}
    thead th {{ border-top: 0; }}
    code {{
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      color: #314055;
    }}
    @media (max-width: 900px) {{
      .workspace, .result-grid {{ grid-template-columns: 1fr; }}
      .side-panel {{ order: -1; }}
    }}
    @media (max-width: 760px) {{
      main {{ padding: 18px 12px 36px; }}
      .topbar {{ align-items: flex-start; flex-direction: column; }}
      .decision-strip {{ grid-template-columns: 1fr; }}
      h1 {{ font-size: 27px; }}
      textarea {{ min-height: 180px; }}
    }}
  </style>
</head>
<body>
  <main>
    <header class="topbar">
      <div class="brand">
        <div class="brand-mark">PW</div>
        <div class="brand-copy">
          <h1>ProcureWise</h1>
          <p class="subtitle">Procurement Risk Triage</p>
        </div>
      </div>
      <div class="status-chip"><span class="status-dot"></span> Local agent ready</div>
    </header>
    <section class="workspace">
      <form class="request-panel" method="post">
        <div class="panel-header">
          <label class="field-label" for="request_text">Purchase Request</label>
        </div>
        <textarea id="request_text" name="request_text" aria-label="Purchase request">{escape(request_text)}</textarea>
        <div class="actions">
          <div class="action-left">
            <button type="submit">Analyze request</button>
            <label><input type="checkbox" name="create_case" checked> Create case file</label>
          </div>
        </div>
      </form>
      <aside class="side-panel">
        <h2>Scenario Library</h2>
        <div class="sample-row">{sample_buttons}</div>
        <ul class="side-list">
          <li><span>01</span><div><strong>Policy Match</strong><p>Procurement, approval, security</p></div></li>
          <li><span>02</span><div><strong>Vendor Status</strong><p>Profile, contract, assurance</p></div></li>
          <li><span>03</span><div><strong>Review Path</strong><p>Risk, approvals, case record</p></div></li>
        </ul>
      </aside>
    </section>
    {result_html}
  </main>
</body>
</html>"""


def main() -> None:
    port = int(os.getenv("PORT", "8502"))
    server = ThreadingHTTPServer(("127.0.0.1", port), ProcureWiseHandler)
    print(f"ProcureWise basic UI running at http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
