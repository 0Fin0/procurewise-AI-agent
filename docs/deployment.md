# Deployment Guide

## Local Development

The fastest demo is the polished browser dashboard. It does not require extra packages.

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

Keep the terminal open while using the app.

## Optional Developer Environment

Create a virtual environment, install dependencies, and run the demo:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_demo.py
```

Run the polished browser dashboard:

```powershell
python app/basic_server.py
```

Then open `http://127.0.0.1:8502`.

Run the optional Streamlit prototype:

```powershell
streamlit run app/streamlit_app.py
```

Windows launcher:

```powershell
.\start_local_app.ps1
```

Then open `http://127.0.0.1:8502`.

## Docker

Build and run the container:

```powershell
docker compose up --build
```

Docker runs the same polished browser dashboard. Open the app at:

```text
http://localhost:8501
```

## Environment Variables

The default local demo does not require a `.env` file. Docker Compose sets safe default values automatically.

If you want to test the API-backed LLM drafting path, copy `.env.example` to `.env`.

```text
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
PROCUREWISE_USE_LLM=false
PROCUREWISE_CASE_DIR=data/runtime
```

The app runs without an API key in deterministic mode. For an LLM-backed demo, set `OPENAI_API_KEY`, set `PROCUREWISE_USE_LLM=true`, and choose the model with `OPENAI_MODEL`. The LLM drafts the final recommendation from retrieved evidence and tool outputs. It does not replace the vendor lookup, approval routing, risk score, or case creation tools.

For a live API demo, use Docker or install the dependencies in `.venv` first so the OpenAI package is available:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
.\start_local_app.ps1
```

## Infrastructure Design

Recommended production deployment:

- Container runtime: Docker
- Hosting: Azure Container Apps, AWS ECS, Google Cloud Run, or Kubernetes
- Secrets: cloud secret manager, not `.env` files
- Storage: managed database for cases and vendor profiles
- Retrieval: managed vector database or Postgres with vector search
- Logs: centralized audit and application logging
- Authentication: SSO with role-based access control

## Security Measures

- Do not bake API keys into the image.
- Run as a non-root user in production.
- Limit case records to the minimum business data required.
- Validate vendor and amount fields before routing.
- Keep human approval for financial commitments and risk acceptance.
- Log tool results and retrieved evidence for auditability.

## Scalability Considerations

The demo uses local files. For scale, move the vendor data, policies, and cases into managed services. The agent workflow itself is stateless except for case writing, so multiple containers can run behind a load balancer if they share storage.

## References

- [Dockerfile overview - Docker Docs](https://docs.docker.com/build/concepts/dockerfile/)
- [Containerize a Python application - Docker Docs](https://docs.docker.com/guides/python/containerize/)
