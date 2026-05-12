# ProcureWise Architecture

## Architecture Summary

ProcureWise is a Track A single-agent system. The agent uses a structured workflow that combines RAG, tool calls, deterministic risk rules, optional LLM-backed response drafting, and a user-facing recommendation.

```mermaid
flowchart LR
    User["Business requester"] --> UI["Polished dashboard or CLI"]
    UI --> Agent["ProcureWise Agent"]
    Agent --> Parser["Request parser"]
    Agent --> RAG["Policy retriever"]
    Agent --> VendorTool["Vendor lookup tool"]
    Agent --> IntakeTool["Intake completeness tool"]
    Agent --> SafetyTool["Safety guard tool"]
    Agent --> ApprovalTool["Approval router"]
    Agent --> RiskTool["Risk scorer"]
    RAG --> KB["Policy knowledge base"]
    VendorTool --> VendorCSV["Vendor risk data"]
    RiskTool --> CaseWriter["Case writer"]
    ApprovalTool --> CaseWriter
    CaseWriter --> Audit["Audit case JSON"]
    Agent --> Response["Recommendation, evidence, next steps"]
    Response --> UI
```

## Agent Workflow

```mermaid
stateDiagram-v2
    [*] --> ParseRequest
    ParseRequest --> RetrievePolicy
    RetrievePolicy --> RunTools
    RunTools --> DraftResponse
    DraftResponse --> CreateCase
    CreateCase --> [*]
```

The implementation supports LangGraph when installed. The same nodes also run through a deterministic local workflow so the project can be demonstrated without paid API access. If an API key is provided, the final drafting step can call an LLM while keeping risk scoring, approvals, retrieval, and case creation controlled by local tools.

## Components

- User interface: `app/streamlit_app.py`
- Agent orchestration: `src/procurewise/agent.py`
- RAG retrieval: `src/procurewise/retriever.py`
- Tools and actions: `src/procurewise/tools.py`
- Prompt design: `src/procurewise/prompts.py`
- Knowledge base: `data/knowledge_base/*.md`
- Vendor data: `data/vendors.csv`
- Runtime case output: `data/runtime/*.json`

## State Design

The agent stores raw state between steps:

- Original request text
- Parsed facts such as amount, vendor, department, category, and data sensitivity
- Retrieved policy evidence
- Vendor lookup result
- Approval routing result
- Risk score result
- Recommendation
- Case ID

This follows the LangGraph pattern of making each node a focused function that reads and writes shared state.

## Retrieval Design

The RAG layer indexes local policy documents by heading. It uses tokenization, term frequency, and inverse document frequency scoring to retrieve the most relevant policy passages. This is intentionally lightweight for a classroom demo, but the architecture can be upgraded to embeddings and a vector database.

## Tool/API Design

The tools act like internal business APIs:

- `request_parser`: extracts structured facts from unstructured text.
- `intake_checker`: checks whether required procurement fields are present before approval.
- `safety_guard`: detects policy-bypass or concealment instructions and keeps normal review in place.
- `vendor_lookup`: checks whether the vendor is known and what its risk posture is.
- `approval_router`: maps spend level to required approvals.
- `risk_scorer`: combines spend, data sensitivity, vendor status, SOC 2 status, and contract status.
- `case_writer`: writes an audit-ready JSON case record.
- `human_review_recorder`: records human reviewer actions without letting the agent approve purchases.

The dashboard also includes a case history view that reads those JSON case records back into the user interface. This makes the case-writing action visible as a persistent audit artifact rather than a temporary response.

## Human Oversight

The agent never becomes the final approver. It recommends routing, evidence, risk level, and next steps. Final approval remains with department, procurement, security, finance, legal, or executive owners depending on request risk.

## Scalability

For a production implementation, the following upgrades would be made:

- Replace CSV vendor data with ERP/procurement API integrations.
- Replace local JSON case output with a ticketing or procurement workflow API.
- Add persistent vector storage for policy documents.
- Add authentication and role-based access controls.
- Add observability through LangSmith or an enterprise logging platform.
- Deploy with Docker on a managed container platform or Kubernetes.
