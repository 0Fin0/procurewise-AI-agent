# Project Proposal

## Project Title

ProcureWise AI Agent: Procurement and Vendor Risk Triage Assistant

## Team Members

- Jesus Arteaga
- Omar Ferrufino
- Marie Trejo Sandoval

## Track Selection

Track A: AI Agent Project

The team selected Track A because the business problem is focused enough for a single well-designed agent and broad enough to demonstrate RAG, tool use, structured reasoning, safety controls, and a polished user experience.

## Business Use Case

Procurement teams often receive incomplete purchase requests. Requesters may not know which approval path applies, whether security review is required, or whether the vendor already has an approved profile. This slows purchasing and creates compliance risk.

ProcureWise helps requesters and procurement analysts by reading a purchase request, retrieving relevant policy, checking vendor status, scoring risk, and drafting an approval recommendation.

## Stakeholders

- Business requesters who need faster guidance
- Procurement analysts who review purchase requests
- Finance approvers who manage spend thresholds
- Security reviewers who assess data and vendor risk
- Legal reviewers who evaluate contracts and data terms
- Executives who approve high-value purchases

## Proposed Capabilities

- Parse purchase requests for amount, vendor, department, category, and data sensitivity
- Retrieve relevant policy passages using RAG
- Look up vendor risk data
- Determine approval routing
- Score risk
- Create an audit case
- Display recommendation, evidence, tool trace, and next steps

## Data Sources

- Procurement intake policy
- Vendor security policy
- Approval matrix
- Responsible AI and automation policy
- Sample vendor risk database
- Sample purchase requests for evaluation

## External Tools

- LangGraph or equivalent graph workflow
- Streamlit for the interface
- Docker for containerization
- Optional OpenAI API for LLM response generation

## Preliminary Timeline

- Week 6: Proposal and topic selection
- Week 8: Knowledge base and sample vendor data
- Week 10: RAG and tool workflow
- Week 11: Progress demo
- Week 14: UI, Docker, testing, and documentation
- Week 16: Final report, demo video, and submission package

## Team Roles

- Jesus Arteaga: business use case support, stakeholder needs, testing scenarios, and presentation support
- Omar Ferrufino: agent engineering, RAG/tools implementation, UI, GitHub setup, and documentation coordination
- Marie Trejo Sandoval: ethics and security analysis, evaluation support, limitations, and report review
