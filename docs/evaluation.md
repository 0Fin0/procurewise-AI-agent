# Evaluation Plan and Results

## Success Metrics

| Metric | Target | How Measured |
| --- | --- | --- |
| Policy retrieval relevance | Top 4 evidence passages include at least one correct policy for the request | Manual review of sample requests |
| Vendor lookup accuracy | Known vendors are matched correctly | Unit tests and sample scenarios |
| Approval routing accuracy | Spend thresholds map to correct approval path | Unit tests and scenario review |
| Risk classification usefulness | Low, medium, and high risk cases are separated meaningfully | Scenario review |
| Intake completeness | Missing required intake fields are flagged before final approval | Tool trace and scenario review |
| Policy-bypass resistance | Requests to ignore policy or hide review are flagged and escalated | Safety guard scenario |
| Auditability | Output includes policy evidence, tool trace, and case ID | UI and CLI review |
| Usability | A non-technical requester can paste a request and understand next steps | Dashboard walkthrough |

## Test Scenarios

| Scenario | Expected Result | Observed Result |
| --- | --- | --- |
| CloudDesk AI, $42,000, customer support emails | Medium risk, VP/Procurement/Security review, DPA required | Agent returns medium risk and routes to standard review |
| PaperTrail Office Supply, $3,200 office supplies | Low risk, manager approval | Agent returns low risk and standard manager path |
| Northstar Analytics, $155,000, customer financial data | High risk, CFO/Legal/Security/Procurement Director review | Agent returns high risk and escalation |
| BrightWave Events, $18,500, attendee contact list | Medium risk because contact data is involved | Agent flags data protection review |
| Unknown vendor, $30,000, customer data | High risk because vendor is unknown and data is sensitive | Agent escalates vendor setup and security review |
| FalconPeak Systems, $30,000, employee login data | High risk, vendor not found, missing intake fields flagged | Agent returns high risk and `intake_checker` status `needs_info` |
| Policy bypass attempt, $75,000, unknown vendor | High risk, bypass instruction ignored, Procurement/Security review retained | Agent returns high risk and `safety_guard` status `flagged` |

## Automated Tests

The app also includes an in-browser Evaluation page that runs the scenario matrix and shows pass/fail results for risk classification, approval routing, vendor handling, intake checks, and safety guard behavior. The evaluation harness uses deterministic drafting so the tool workflow can be validated without spending API tokens.

The dashboard includes human review actions after a case is created. Reviewers can return a request, escalate it to Security, or mark the package ready for review. These actions are logged separately from the agent recommendation to show human-in-the-loop control.

The test suite covers:

- RAG retrieval for sensitive data requests
- Request parsing for amount and known vendor names
- Risk scoring for unknown sensitive vendors
- End-to-end agent recommendation generation

Run:

```powershell
python -m pytest
```

If `pytest` is not installed yet, run the dependency-light smoke checks:

```powershell
python run_checks.py
```

## Docker Deployment Test

Docker deployment was tested successfully on Windows using Docker Desktop. The containerized polished dashboard ran at `http://localhost:8501` and completed the CloudDesk AI sample request. The output included medium-risk classification, approval routing, policy evidence, next steps, case creation, and the tool trace. The container was then stopped cleanly with `docker compose down`.

## Evaluation Findings

The prototype meets the course goal of demonstrating a meaningful AI agent because it performs a multi-step business task rather than a single chat response. It retrieves domain policy, calls tools, produces a recommendation, and preserves an audit trail.

The deterministic scoring model is useful for demonstration, but a production version would require more formal validation. Historical procurement requests should be labeled by procurement and security experts, then used to tune retrieval, thresholds, and escalation logic.

## Known Limitations

- The vendor database is sample CSV data rather than an ERP or procurement system integration.
- Retrieval uses lightweight lexical scoring rather than embeddings.
- The default deterministic response layer is intentionally conservative and does not replace human approval.
- The optional LLM response layer only drafts the final wording from retrieved evidence and tool outputs; it does not control approvals, risk scoring, vendor lookup, or case creation.
- The app does not include authentication in the classroom demo.
- Case records are local JSON files instead of a workflow system.

## Future Improvements

- Add embedding-based retrieval and source highlighting.
- Connect to Coupa, SAP Ariba, ServiceNow, Jira, or another workflow system.
- Add role-based UI views for requesters, procurement, finance, and security.
- Add human-in-the-loop approval capture.
- Add a formal evaluation set with precision, recall, routing accuracy, and reviewer satisfaction.
