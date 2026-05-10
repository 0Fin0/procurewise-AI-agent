# Evaluation Plan and Results

## Success Metrics

| Metric | Target | How Measured |
| --- | --- | --- |
| Policy retrieval relevance | Top 4 evidence passages include at least one correct policy for the request | Manual review of sample requests |
| Vendor lookup accuracy | Known vendors are matched correctly | Unit tests and sample scenarios |
| Approval routing accuracy | Spend thresholds map to correct approval path | Unit tests and scenario review |
| Risk classification usefulness | Low, medium, and high risk cases are separated meaningfully | Scenario review |
| Auditability | Output includes policy evidence, tool trace, and case ID | UI and CLI review |
| Usability | A non-technical requester can paste a request and understand next steps | Streamlit walkthrough |

## Test Scenarios

| Scenario | Expected Result | Observed Result |
| --- | --- | --- |
| CloudDesk AI, $42,000, customer support emails | Medium risk, VP/Procurement/Security review, DPA required | Agent returns medium risk and routes to standard review |
| PaperTrail Office Supply, $3,200 office supplies | Low risk, manager approval | Agent returns low risk and standard manager path |
| Northstar Analytics, $155,000, customer financial data | High risk, CFO/Legal/Security/Procurement Director review | Agent returns high risk and escalation |
| BrightWave Events, $18,500, attendee contact list | Medium risk because contact data is involved | Agent flags data protection review |
| Unknown vendor, $30,000, customer data | High risk because vendor is unknown and data is sensitive | Agent escalates vendor setup and security review |

## Automated Tests

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

## Evaluation Findings

The prototype meets the course goal of demonstrating a meaningful AI agent because it performs a multi-step business task rather than a single chat response. It retrieves domain policy, calls tools, produces a recommendation, and preserves an audit trail.

The deterministic scoring model is useful for demonstration, but a production version would require more formal validation. Historical procurement requests should be labeled by procurement and security experts, then used to tune retrieval, thresholds, and escalation logic.

## Known Limitations

- The vendor database is sample CSV data rather than an ERP or procurement system integration.
- Retrieval uses lightweight lexical scoring rather than embeddings.
- The deterministic response layer is intentionally conservative and does not replace human approval.
- The app does not include authentication in the classroom demo.
- Case records are local JSON files instead of a workflow system.

## Future Improvements

- Add embedding-based retrieval and source highlighting.
- Connect to Coupa, SAP Ariba, ServiceNow, Jira, or another workflow system.
- Add role-based UI views for requesters, procurement, finance, and security.
- Add human-in-the-loop approval capture.
- Add a formal evaluation set with precision, recall, routing accuracy, and reviewer satisfaction.
