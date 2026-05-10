# Five-Minute Video Demo Script

## 0:00-0:30 - Problem and Value

"Our project is ProcureWise, a procurement and vendor-risk AI agent. The business problem is that purchase approvals often slow down because requesters do not know which policy applies, procurement has to manually check vendor status, and security reviews are triggered late. ProcureWise helps by reading the request, retrieving policy, checking vendor data, routing approvals, scoring risk, and drafting next steps."

## 0:30-1:00 - Track and Architecture

"We selected Track A, a single AI Agent, because the goal is a focused but polished workflow. The agent uses a LangGraph-style sequence: parse request, retrieve policy, run tools, draft response, and write an audit case. The knowledge base contains procurement, approval, security, and responsible AI policies."

## 1:00-2:15 - Demo Request

Paste this request into the app:

```text
We need to buy a $42,000 annual subscription from CloudDesk AI for the Customer Success team. It will process customer emails and support tickets. Can we approve it this week?
```

"The request includes spend, vendor, department, software category, and sensitive customer data. When I click Analyze, the agent retrieves policy evidence, checks the vendor database, determines the approval path, and scores risk."

## 2:15-3:15 - Output Walkthrough

"The result is medium risk. The agent recommends conditional review instead of immediate approval. It shows that the required path is Department VP, Procurement, and Security review. It also lists next steps such as attaching the business justification, routing approval, and completing data protection review. Notice that the app shows the evidence passages and the tool trace, so the result is auditable."

## 3:15-4:00 - Second Scenario

Paste:

```text
Finance wants a $155,000 analytics platform from Northstar Analytics that will analyze customer revenue and payment trends.
```

"This one is high risk because the amount is over $100,000, the vendor has a high risk rating, and the request involves sensitive customer financial data. The agent escalates to CFO, Legal, Security, and Procurement Director."

## 4:00-4:40 - Ethics and Security

"The agent does not approve purchases by itself. That is intentional. It supports human reviewers with evidence and recommendations, but final authority stays with procurement, finance, legal, and security owners. This reduces overreliance and excessive agency."

## 4:40-5:00 - Deployment

"The project includes a Dockerfile, compose file, documentation, tests, and a final report. It can run locally in deterministic mode or be extended with an LLM API key for production-style natural language generation."

