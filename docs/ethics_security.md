# Ethics and Security Analysis

## Ethical Risks

ProcureWise influences procurement decisions, so it must be careful about overreliance, vendor fairness, transparency, and privacy. The agent is designed to assist reviewers rather than replace them.

## Human Accountability

The agent does not approve purchases, sign contracts, accept vendor risk, or make final legal decisions. It routes work and explains the evidence. Human stakeholders remain accountable for final approvals.

## Bias and Fairness

Vendor risk should be based on documented evidence such as contract status, security review, data handling, insurance, and spend threshold. The agent should not assume that small vendors, new vendors, or vendors from specific regions are automatically risky. If a vendor is unknown, the output asks for a vendor profile instead of rejecting the vendor permanently.

## Privacy

The system asks users to submit only information required for procurement review. Case records should avoid unnecessary personal data. In production, retention rules should align with company procurement, legal, and privacy policies.

## Security Controls

- Prompt instructions tell the agent not to invent vendor facts or policy.
- Retrieved policy evidence is displayed to reduce black-box recommendations.
- Tool traces are visible for audit.
- High-risk or sensitive-data requests are escalated to humans.
- API keys are stored outside source code.
- Case records are separated from source files.

## LLM-Specific Threats

The design addresses the following risks from OWASP's LLM guidance:

- Prompt injection: user text is treated as a request, not as system instruction.
- Sensitive information disclosure: outputs should avoid exposing unnecessary data.
- Excessive agency: the agent cannot issue purchase orders or sign contracts.
- Overreliance: final approval remains with accountable humans.
- Supply chain vulnerabilities: dependencies are documented and should be scanned before production use.

## NIST AI RMF Alignment

The project aligns with the NIST AI Risk Management Framework by emphasizing governance, mapping risks, measuring performance, and managing harms. In classroom terms, ProcureWise shows this through clear ownership, documented metrics, test scenarios, human review, and risk mitigation.

## Misuse Mitigation

Potential misuse includes trying to bypass approval, asking the agent to hide sensitive facts, or requesting approval for a prohibited vendor. Mitigations include immutable tool traces, policy citations, conservative routing, and human review for high-risk cases.

## References

- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [NIST AI RMF 1.0 publication](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10)
- [OWASP Top 10 for Large Language Model Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications)

