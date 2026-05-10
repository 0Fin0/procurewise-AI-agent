# Progress Report

## Team Members

- Jesus Arteaga
- Omar Ferrufino
- Marie Trejo Sandoval

## Current Status

The ProcureWise prototype has an initial end-to-end implementation. A user can submit a purchase request, and the agent parses request facts, retrieves policy evidence, checks vendor data, routes approvals, scores risk, and returns next steps.

## Completed Work

- Selected Track A AI Agent scope
- Defined the procurement/vendor-risk business use case
- Created sample policy knowledge base
- Created sample vendor database
- Implemented request parsing
- Implemented policy retrieval
- Implemented vendor lookup
- Implemented approval routing
- Implemented risk scoring
- Added a Streamlit user interface
- Added case file generation for auditability

## RAG Progress

The RAG implementation reads Markdown policy documents, chunks content by heading, tokenizes text, and scores passages using lexical relevance. Retrieved passages are shown in the final response so users can inspect the evidence.

## Workflow Progress

The workflow is structured as graph-ready nodes:

1. Parse request
2. Retrieve policy
3. Run tools
4. Draft response
5. Write case

The implementation uses LangGraph when available and falls back to a deterministic local workflow for classroom demonstration.

## Preliminary Ethical Analysis

The main ethical risks are overreliance, unfair vendor treatment, sensitive data exposure, and excessive automation. The current mitigation strategy keeps humans as final approvers, shows evidence, logs tool results, and escalates sensitive or high-risk requests.

## Open Work for Final Submission

- Expand documentation into final report
- Add evaluation scenarios and test results
- Finalize Docker instructions
- Prepare five-minute video demo script
- Polish README and repository structure
