# ProcureWise AI Agent

ProcureWise is a Track A AI Agent project for ISYS 573. It helps procurement, finance, and IT teams triage purchase requests by retrieving policy evidence, checking vendor risk data, identifying approval requirements, and drafting a clear recommendation.

Team members:

- Jesus Arteaga
- Omar Ferrufino
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

If you received this project as a ZIP from Discord, unzip it first and read:

```text
TEAM_SETUP_FROM_ZIP.md
```

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

The core demo works without an API key. Docker also runs without a `.env` file. To use an LLM-backed implementation later, copy `.env.example` to `.env`, add your API key, and install the optional packages listed in `requirements.txt`.

## Repository Structure

```text
app/                         Polished browser dashboard and optional Streamlit prototype
data/knowledge_base/         RAG source documents
data/vendors.csv             Sample vendor risk database
data/sample_requests.csv     Evaluation and demo scenarios
docs/                        Final report, architecture, ethics, deployment, demo script
src/procurewise/             Agent, retrieval, tools, prompts, schemas
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
- Final report simplified source: `docs/final_report_grade9.md`
- Original detailed report draft: `docs/final_report.md`
- Architecture: `docs/architecture.md`
- Evaluation plan and results: `docs/evaluation.md`
- Ethics and security analysis: `docs/ethics_security.md`
- Deployment instructions: `docs/deployment.md`
- 5-minute video script: `docs/demo_script.md`
- Proposal and progress report drafts: `docs/project_proposal.md`, `docs/progress_report.md`
