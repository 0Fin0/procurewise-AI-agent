# ProcureWise AI Agent Final Report

## Course and Project

ISYS 573: AI Agent / Agentic AI Group Project

Project title: ProcureWise AI Agent

Track: Track A - AI Agent Project

Final submission due: May 12, 2026

## Executive Summary

ProcureWise is an AI-powered procurement and vendor-risk triage assistant. The business problem is common in organizations that buy software, services, and data-processing tools: purchase requests arrive with incomplete information, policy requirements are scattered across documents, vendor risk records live in separate systems, and approvals are delayed because the requester does not know what evidence is needed.

The solution is a single AI agent that takes an unstructured purchase request and turns it into an audit-ready recommendation. It parses request details, retrieves relevant policy passages through Retrieval Augmented Generation, checks vendor risk data, determines the approval path, scores risk, creates a case record, and produces next steps for the user.

The agent is intentionally designed as decision support rather than autonomous approval. It does not sign contracts, issue purchase orders, or accept risk. It shows evidence and tool results so human stakeholders can verify the recommendation. This design supports business speed while respecting governance, privacy, security, and accountability.

## 1. Business Use Case Definition

### Business Scenario

Procurement teams are responsible for helping employees buy the goods and services they need while protecting the organization from financial, legal, operational, security, and privacy risk. In practice, purchase requests are often submitted through email, chat, spreadsheets, or ticketing systems with incomplete context. A request such as "Can we buy this AI support tool this week?" may require several checks:

- Is the amount above an approval threshold?
- Is the vendor already approved?
- Does the vendor process customer, employee, student, financial, or confidential data?
- Is a security review required?
- Is a contract or data processing agreement already in place?
- Which leaders need to approve the request?
- What evidence is missing?

Without an assistant, procurement analysts manually search policies, check vendor records, ask follow-up questions, and route approvals. This creates delays and inconsistent review quality.

### Current Approaches and Limitations

Many organizations rely on static procurement policy pages, enterprise resource planning systems, vendor management tools, and ticket queues. These tools are important, but they often require users to know where to search and how to interpret policy. Traditional workflow systems can route approvals after structured fields are entered, but they struggle with unstructured requests and policy explanation.

ProcureWise addresses the gap before formal approval routing. It helps a requester or analyst convert a messy request into a structured, evidence-backed recommendation.

### Stakeholders

The main stakeholders are:

- Business requesters who need fast guidance on what is required.
- Procurement analysts who review requests and enforce purchasing policy.
- Finance approvers who control spend thresholds.
- Security reviewers who evaluate vendor and data risk.
- Legal reviewers who handle contracts and data terms.
- Executives who approve high-value or high-risk purchases.
- Audit and compliance teams who need clear evidence of review.

### Agent Tasks

ProcureWise performs the following tasks:

1. Read an unstructured purchase request.
2. Extract amount, vendor, department, category, and data sensitivity.
3. Retrieve relevant procurement, approval, security, and responsible AI policy passages.
4. Look up the vendor in a sample vendor risk database.
5. Determine the approval path based on amount and risk.
6. Score overall request risk.
7. Draft a recommendation with cited evidence.
8. Create an audit case file.
9. Provide concrete next steps.

### Success Metrics

The project uses the following success metrics:

- Retrieval relevance: top evidence contains at least one applicable policy passage.
- Vendor lookup accuracy: known vendors are matched correctly.
- Approval routing accuracy: spend thresholds map to the correct approval path.
- Risk classification usefulness: low, medium, and high risk cases are separated meaningfully.
- Auditability: output includes policy evidence, tool trace, and case ID.
- Usability: a non-technical requester can paste a request and understand what to do next.

## 2. Agent Architecture Design

### Track Selection

The project uses Track A, a single AI Agent. This scope is appropriate because procurement triage is a focused business problem with a clear workflow. A multi-agent system could be useful in a larger enterprise setting, but a single agent is enough to demonstrate architecture, RAG, tools, prompt engineering, safety, UI, deployment, and evaluation.

### Agent Goal

The agent's goal is to help users understand whether a purchase request can proceed and what approvals or evidence are required.

### Constraints

The agent must:

- Use policy evidence before giving a recommendation.
- Use vendor and approval tools rather than inventing facts.
- Avoid final approval of financial commitments.
- Escalate sensitive-data and high-risk cases.
- Produce an explainable output.
- Preserve a case record for review.

### Knowledge Base and RAG

The knowledge base contains Markdown policy documents:

- Procurement intake policy
- Vendor security policy
- Approval matrix
- Responsible AI and automation policy

The retriever loads these documents, chunks them by headings, tokenizes text, and scores relevance. The response includes the top retrieved passages so the user can inspect why the agent made its recommendation.

This is a lightweight RAG implementation appropriate for a classroom prototype. A production version could replace the lexical scorer with embeddings and a vector database.

### Decision-Making Framework

The workflow uses the following reasoning pattern:

1. Parse the request.
2. Retrieve policy.
3. Run business tools.
4. Score risk.
5. Draft response.
6. Write case.

This is implemented in `src/procurewise/agent.py`. When LangGraph is available, the nodes are compiled into a `StateGraph`. If LangGraph is not installed, the same nodes run sequentially so the demo remains functional.

### Tool and API Integration

The prototype tools simulate internal business APIs:

- Request parser: extracts structured facts.
- Vendor lookup: checks vendor risk data.
- Approval router: applies approval thresholds.
- Risk scorer: combines vendor, spend, contract, SOC 2, and data sensitivity signals.
- Case writer: creates a JSON audit case.

### User Interaction Model

The Streamlit app is a direct tool interface, not a marketing page. A user pastes a purchase request, clicks Analyze, and receives:

- Risk level
- Case ID
- Recommendation
- Approval path
- Next steps
- Policy evidence
- Tool trace

This interface is designed for requesters and analysts who need a fast, readable result.

### Architecture Justification

LangGraph is suitable for this project because it supports stateful graph workflows composed of nodes and edges. The official LangGraph documentation describes it as an orchestration framework for long-running, stateful agents and workflows. ProcureWise uses that pattern by decomposing the agent into discrete steps and preserving state between them.

The Docker deployment follows standard containerization practices: dependencies are installed from `requirements.txt`, application files are copied into the image, a runtime port is exposed, and Streamlit starts as the container command.

## 3. Agent Implementation

### Implementation Overview

The implementation is organized as a Python project:

- `src/procurewise/retriever.py`: RAG retrieval
- `src/procurewise/tools.py`: parser, vendor lookup, approval router, risk scorer, case writer
- `src/procurewise/agent.py`: graph-style agent workflow
- `src/procurewise/prompts.py`: system prompt and response template
- `app/streamlit_app.py`: web user interface
- `tests/`: automated tests

### Prompt Engineering

The system prompt defines the agent's role, goal, and constraints. It tells the agent to be conservative, use retrieved evidence and tool results, avoid inventing facts, and list missing information when needed. The response template asks for recommendation, risk level, required approvals, policy evidence, and next steps.

The deterministic classroom mode uses the same design principles without requiring paid API access. This makes the demo reliable while still documenting how an LLM-backed version would be structured.

### RAG Implementation

The RAG implementation indexes policy sections by heading. When a request comes in, the query combines the raw request with parsed category and data sensitivity signals. The retriever scores each section and returns the top passages as evidence. The final answer includes source file, heading, passage text, and retrieval score.

### Tool Implementation

The tool layer adds business action:

- It extracts spend such as "$42,000" or "$155,000."
- It detects known vendors from `data/vendors.csv`.
- It classifies software, services, hardware, marketing, or general requests.
- It detects likely sensitive data from terms such as customer, employee, student, email, and financial.
- It routes approvals by spend threshold.
- It adds risk points for high spend, sensitive data, unknown vendor, high vendor risk, missing SOC 2, and missing active contract.
- It writes a case JSON file for audit.

### Error Handling and Safety

The agent handles missing vendor names by returning a needs-review vendor lookup result. Unknown vendors increase risk and trigger a next step to create or update the vendor profile. Missing amounts default to the lowest spend value for routing but are still visible in parsed facts. The response remains conservative if important information is missing.

### User Interface

The Streamlit app gives a simple request box and an Analyze button. The output is organized into metrics, recommendation, approval path, next steps, policy evidence, and tool trace. This supports transparency and usability.

### Challenges and Solutions

One challenge is demonstrating an AI agent without depending on a live enterprise procurement system. The solution is to model internal APIs with sample CSV and local case output. Another challenge is running the project without API keys during grading. The solution is a deterministic mode that still demonstrates the workflow, tools, RAG, and architecture.

## 4. Containerization and Deployment

### Container Package

The project includes:

- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`
- `.env.example`
- `requirements.txt`

The container runs the Streamlit app on port 8501.

### Deployment Instructions

Local run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

Docker run:

```powershell
docker compose up --build
```

Then open `http://localhost:8501`.

### Infrastructure Design

For production, ProcureWise would run as a containerized app behind SSO. Vendor profiles would come from an ERP, procurement, or vendor management API. Cases would be written to a workflow system such as ServiceNow, Jira, Coupa, or SAP Ariba. Policy retrieval would use a managed document store and vector database.

### Security Measures

Production security controls would include:

- Secret management for API keys
- Role-based access control
- Logging and monitoring
- Dependency scanning
- Data minimization
- Encryption in transit and at rest
- Human approval for high-risk decisions
- Prompt injection testing

## 5. Evaluation and Ethics

### Testing

The project includes automated tests for retrieval, parsing, risk scoring, and end-to-end agent output. The evaluation document also defines manual scenarios covering low, medium, and high risk requests.

### Performance Against Metrics

The prototype meets the main classroom metrics:

- It retrieves relevant policy evidence.
- It matches known vendors.
- It maps spend to approval paths.
- It differentiates low, medium, and high risk requests.
- It provides tool traces and case IDs.
- It gives a non-technical user clear next steps.

### Bias and Ethical Concerns

The main ethical concern is that users may overtrust an automated recommendation. ProcureWise mitigates this by showing evidence, preserving human approval, and refusing to act as the final approver. Another concern is vendor fairness. The agent does not reject unknown vendors automatically; it asks for more evidence and vendor setup.

### Privacy and Compliance

ProcureWise should not collect unnecessary personal data. Requests should include only the business facts needed for review. Case records should follow retention policies. Sensitive data requests trigger data protection review before sharing data with vendors.

### Security and Misuse

The agent could be misused if a requester tries to hide risk or asks it to bypass approval. The design mitigates this through tool traces, policy citations, conservative routing, and human escalation. OWASP's LLM guidance highlights risks such as prompt injection, sensitive information disclosure, excessive agency, and overreliance. ProcureWise directly addresses these by limiting actions and keeping humans in control.

### Limitations

The main limitations are:

- Sample data instead of live enterprise integrations
- Lightweight retrieval instead of embeddings
- Deterministic response drafting instead of full LLM generation by default
- No authentication in classroom demo
- Local case files instead of a production workflow system

### Future Improvements

Future work should include:

- Embedding-based retrieval
- LLM-backed response drafting with guardrails
- Human approval workflow
- Integration with procurement and ticketing systems
- Formal reviewer evaluation
- Access controls and production logging
- Dashboard for procurement metrics

## 6. Documentation

The repository includes:

- README
- Architecture documentation
- Deployment instructions
- Evaluation plan
- Ethics and security analysis
- Proposal
- Progress report
- Demo video script
- Code comments and tests

This makes the project ready to be uploaded to GitHub and submitted with the final report and video demo.

## Conclusion

ProcureWise demonstrates a practical AI agent for a real business workflow. It combines a focused use case, RAG over policy documents, tool-based actions, graph-style orchestration, a usable interface, deployment assets, evaluation, and ethical safeguards. The project shows how agentic techniques can improve business operations while keeping human accountability in place.

## References

- Amit Bahree, Generative AI in Action.
- Roberto Infante, AI Agents and Applications With LangChain, LangGraph, and MCP.
- David Baum, Generative AI and LLMs for Dummies.
- [LangGraph overview - Docs by LangChain](https://docs.langchain.com/oss/python/langgraph)
- [Use the graph API - Docs by LangChain](https://docs.langchain.com/oss/python/langgraph/use-graph-api)
- [Dockerfile overview - Docker Docs](https://docs.docker.com/build/concepts/dockerfile/)
- [Containerize a Python application - Docker Docs](https://docs.docker.com/guides/python/containerize/)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [NIST AI RMF 1.0 publication](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10)
- [OWASP Top 10 for Large Language Model Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications)

