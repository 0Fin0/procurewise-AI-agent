# ProcureWise AI Agent

ProcureWise is an AI Agent project for ISYS 573. It helps procurement, finance, and IT teams triage purchase requests by retrieving policy evidence, checking vendor risk data, identifying approval requirements, and drafting a clear recommendation.

Team members:

- Omar Ferrufino
- Jesus Arteaga
- Marie Trejo Sandoval

The project is designed to satisfy the final package requirements:

- Business use case and stakeholder value
- Single AI agent architecture with a reasoning workflow
- Retrieval Augmented Generation over a domain knowledge base
- Tool/API style actions for vendor lookup, approval routing, risk scoring, and case creation
- Polished browser dashboard for reviewing purchase requests
- Docker deployment package
- Evaluation, ethics, security, and final report documentation

## Project Track

Track A: AI Agent Project

This is a single agent with a structured workflow:

1. Understand the request.
2. Retrieve relevant procurement and security policy passages.
3. Run tools against vendor and approval data.
4. Score risk and decide the needed action.
5. Create an audit-ready case summary.
6. Produce a user-facing recommendation with cited policy evidence.

## Quick Start

The fastest local demo does not need extra packages:

Windows:

```powershell
.\start_local_app.ps1
```

Or double-click:

```text
start_local_app.bat
```

macOS:

```zsh
python3 app/basic_server.py
```

Or:

```zsh
sh start_local_app.command
```

Then open:

```text
http://127.0.0.1:8502
```

Keep the terminal window open while using the app.

## Developer Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_demo.py
```

To run a dependency-light verification:

```powershell
python run_checks.py
```

To run the polished browser dashboard:

```powershell
python app/basic_server.py
```

Then open `http://127.0.0.1:8502`.

To run the optional Streamlit prototype:

```powershell
streamlit run app/streamlit_app.py
```

On Windows, you can also run:

```powershell
.\start_local_app.ps1
```

Or double-click `start_local_app.bat`. Keep the terminal window open while using the app.

To run the Docker version of the polished dashboard:

```powershell
docker compose up --build
```

Then open `http://localhost:8501`.

The core demo works without an API key. Docker also runs without a `.env` file. An optional LLM-backed response drafter is implemented for teams that want to show a live API-based agent path. To turn it on, copy `.env.example` to `.env`, add your API key, and set:

```text
PROCUREWISE_USE_LLM=true
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Even in LLM mode, the risk score, approval path, vendor lookup, policy evidence, and case creation still come from the agent tools. The LLM only drafts the final recommendation from those tool outputs, and the tool trace records whether the response came from LLM mode or deterministic fallback mode.

For a live API demo, use Docker or install the dependencies in `.venv` first so the OpenAI package is available:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
.\start_local_app.ps1
```

## Repository Structure

```text
app/                         Polished browser dashboard and optional Streamlit prototype
data/knowledge_base/         RAG source documents
data/vendors.csv             Sample vendor risk database
data/sample_requests.csv     Evaluation and demo scenarios
docs/                        Final report, architecture, ethics, deployment, and evaluation
src/procurewise/             Agent, optional LLM drafter, retrieval, tools, prompts, schemas
tests/                       Local unit tests
Dockerfile                   Container build
docker-compose.yml           Local container launch
run_demo.py                  CLI demo
```

## Sample Request

```text
We need to buy a $42,000 annual subscription from CloudDesk AI for the Customer Success team.
It will process customer emails and support tickets. Can we approve it this week?
```

The agent will retrieve relevant policy, check CloudDesk AI in the vendor database, determine the approval path, flag data handling requirements, and draft the next steps.

## Deliverables

- Final report Word document: `docs/ProcureWise_Final_Report.docx`
- Architecture: `docs/architecture.md`
- Evaluation plan and results: `docs/evaluation.md`
- Ethics and security analysis: `docs/ethics_security.md`
- Deployment instructions: `docs/deployment.md`

## Public Repository Notes

The repository is prepared for public GitHub use. Local-only files such as `.env`, runtime case files, ZIP archives, cache folders, and the assignment PDF are ignored and should not be committed.
