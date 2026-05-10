# ProcureWise AI Agent Final Report

## Executive Summary

ProcureWise is an AI agent that helps with purchase requests. Many companies need to review purchases before they are approved. This is especially true when the purchase is expensive, involves software, or gives a vendor access to customer or employee data. Without a tool like ProcureWise, a requester may not know which policy applies, who needs to approve the request, or what security review is needed.

Our project uses ProcureWise to make that process easier. A user enters a purchase request in plain language. The agent reads the request, finds important details, searches policy documents, checks vendor data, scores risk, and gives a clear recommendation. The recommendation includes the approval path, policy evidence, next steps, and a case record.

This project is a Track A AI Agent project. We chose Track A because our goal is to build one focused agent that works well. The agent is not meant to replace people. It helps people make better decisions by showing evidence and explaining the next steps. Final approval still belongs to human reviewers such as procurement, finance, legal, and security.

Our team members are Jesus Arteaga, Omar Ferrufino, and Marie Trejo Sandoval. Jesus supported the business use case, stakeholder needs, testing scenarios, and presentation planning. Omar worked on the agent workflow, user interface, GitHub setup, Docker testing, and documentation coordination. Marie supported the ethics and security review, evaluation, limitations, and report review.

## Business Use Case Definition

Procurement teams help employees buy the products and services they need. At the same time, they must protect the company from cost, legal, security, privacy, and compliance risks. A simple purchase request can become complicated if it involves a new vendor, a high dollar amount, customer data, employee data, or an AI tool.

For example, a team may ask to buy a software subscription that will process customer emails and support tickets. That request is not just a normal software purchase. It may need a security review, a data protection agreement, vendor risk checks, and approval from a department leader. If the requester does not know this, the request may be delayed.

The current way of handling this kind of work is often manual. A procurement analyst may need to read the request, look up policy rules, check a vendor list, ask follow-up questions, and route the request to the right people. This takes time and can lead to uneven results. Two people may handle similar requests in different ways.

ProcureWise helps solve this problem by giving the requester and the procurement team a first review. The agent does not approve the purchase by itself. Instead, it helps organize the request and shows what needs to happen next. This gives the business faster guidance while keeping human oversight in place.

The main stakeholders are business requesters, procurement analysts, finance approvers, security reviewers, legal reviewers, executives, and audit teams. Requesters want fast answers. Procurement wants complete information. Finance wants spend controls. Security and legal want to reduce risk. Audit teams want clear records that show why a decision was made.

The agent performs several tasks in order. It reads the request, extracts the vendor and amount, checks whether sensitive data is involved, searches policy documents, looks up the vendor, decides the approval route, scores the risk, writes a case file, and explains the result to the user. The result is easier to understand than a long policy document.

Success for this project means the agent should give useful policy evidence, match known vendors correctly, choose the right approval path, separate low, medium, and high risk requests, and show a clear tool trace. It should also be easy enough for a non-technical user to run during a demo.

## Agent Architecture Design

ProcureWise is a single AI agent with a structured workflow. The workflow is designed like a graph. Each step handles one part of the job. This makes the system easier to explain, test, and improve. The same design can work with LangGraph, but the local version can also run without an API key.

The first step is request parsing. The agent takes the user’s text and looks for the purchase amount, vendor name, department, category, and data sensitivity. For example, if the request mentions customer emails, the agent treats it as a sensitive data request. If the request mentions a subscription or platform, the agent treats it as software.

The second step is retrieval augmented generation, also called RAG. RAG means the agent searches a knowledge base before giving an answer. Our knowledge base includes procurement policy, security policy, an approval matrix, and responsible AI policy. The agent retrieves policy passages that match the request. This helps the answer stay grounded in evidence.

The third step is tool use. ProcureWise has tools that act like small business systems. One tool checks the sample vendor database. Another tool decides the approval path. Another tool scores the risk. Another tool writes a case file. These tools help the agent do more than just chat.

The fourth step is response drafting. The agent uses the parsed facts, policy evidence, vendor result, approval path, and risk score to write a recommendation. The recommendation tells the user whether the request can move forward, what approval path is needed, and what steps must happen next.

The fifth step is case creation. If the user keeps case creation turned on, the agent writes a JSON case file. This file stores the request, facts, vendor result, approval result, risk score, and recommendation. This creates a simple audit trail for the project demo.

The agent has clear limits. It does not sign contracts, issue purchase orders, or approve vendor risk. It does not invent policy or vendor facts. If a vendor is unknown or information is missing, the agent says that more review is needed. This keeps the system safer and easier to trust.

The user interface supports the workflow. A user enters a request, clicks the analyze button, and sees the result. The output includes risk level, recommendation, approval path, next steps, policy evidence, and tool trace. The interface is simple enough for a classroom demo and clear enough for a business user.

## Agent Implementation

The project is built in Python. The main agent code is in the `src/procurewise` folder. The user interface is in the `app` folder. The policy files are in `data/knowledge_base`. The sample vendor file is `data/vendors.csv`. The sample requests are in `data/sample_requests.csv`.

The main workflow is in `src/procurewise/agent.py`. This file controls the agent steps. It parses the request, retrieves policy, runs tools, drafts the answer, and creates a case when needed. The code can use LangGraph if it is installed, but it also has a direct local workflow so the project can run without paid API access.

The RAG code is in `src/procurewise/retriever.py`. It loads the policy documents, breaks them into sections by heading, and scores them against the user request. The highest scoring sections are returned as policy evidence. This is a simple RAG method, but it is enough to show the idea clearly.

The tools are in `src/procurewise/tools.py`. The request parser finds facts from the request. The vendor lookup checks the vendor CSV file. The approval router maps spending levels to review paths. The risk scorer adds risk points for things like high spend, sensitive data, unknown vendors, missing contracts, and missing security evidence. The case writer saves the result.

The prompt design is stored in `src/procurewise/prompts.py`. The prompt tells the agent to be careful, use evidence, avoid making up facts, and explain missing information. Even though the local version uses deterministic response logic, the prompt file shows how the project can support an API-based LLM later.

The interface has two options. The Streamlit app runs in Docker and opens at `http://localhost:8501`. The no-dependency browser app runs locally at `http://127.0.0.1:8502`. The local browser app is useful because teammates can run it without installing extra Python packages.

One challenge was making the project easy to run on different computers. Some team members use Windows and some may use macOS. To help with this, the project includes Windows launchers, a macOS command file, a Discord setup guide, and a README. It also includes Docker files for deployment.

Another challenge was making the system feel like an agent without requiring a paid API key. We solved this by building the agent workflow with real retrieval and tools. The project can still be upgraded later with an OpenAI API or another LLM API for richer final response writing.

## Containerization and Deployment

Containerization is included through Docker. The project has a `Dockerfile`, a `docker-compose.yml` file, and a `.dockerignore` file. These files package the app so it can run in a container. This helps show how the project could be deployed outside a normal local Python setup.

Docker Desktop was tested successfully on Windows. The containerized Streamlit app ran at `http://localhost:8501`. The CloudDesk AI sample request was tested in the Docker version. The app returned a medium risk result, showed policy evidence, routed the request to the correct approval path, listed next steps, created a case, and displayed the tool trace.

After the Docker test, the container was stopped cleanly. The command `docker compose down` removed the container and the Docker network. This means the deployment files are not only included, but were also tested on a real Windows machine.

The default Docker setup does not need a `.env` file. This is important because teammates or graders can run the container without first creating extra configuration. The `.env.example` file is still included for future work, especially if the team adds an API-based LLM connection later.

In a real company, this system would need stronger deployment controls. It would need login, role-based access, secret management, database storage, logging, and security monitoring. It could be hosted on a cloud container service or on Kubernetes. For this project, Docker shows the basic deployment approach clearly.

## Evaluation and Ethics

The project was tested with several sample requests. The CloudDesk AI request is a medium risk case because it is a software purchase above the standard review threshold and it handles customer support data. The Northstar Analytics request is a high risk case because it is expensive, involves customer financial data, and uses a vendor with a high risk rating.

The PaperTrail Office Supply request is a low risk case because it is a small office supply purchase from a low risk vendor. The BrightWave Events request is a medium risk case because it involves attendee contact data. These examples show that the agent can handle different levels of risk.

The automated checks also passed. The checks confirm that policy retrieval works, known vendors can be found, risk scoring works for unknown sensitive vendors, and the end-to-end agent returns a recommendation. The command `python run_checks.py` returned that all ProcureWise checks passed.

The Docker deployment test also passed. This matters because deployment is part of the project rubric. The Docker test showed that the app can run as a container and still complete the sample request. This strengthens the deployment section of the project.

The main ethical risk is overreliance. A user may trust the agent too much and treat its answer as final approval. ProcureWise reduces this risk by making the agent a decision support tool. It gives recommendations and evidence, but humans still make final approval decisions.

Another ethical issue is fairness to vendors. A new or small vendor should not be rejected just because it is unknown. ProcureWise does not permanently reject unknown vendors. It says the vendor profile must be created or reviewed before approval. This keeps the process fairer and more evidence based.

Privacy is also important. Purchase requests should not include extra personal information. The case file should store only what is needed for review and audit. If a request involves customer, employee, student, financial, or confidential data, the agent flags the need for a data protection review.

Security is important because AI agents can be misused. A requester might try to hide risk or ask the agent to bypass approval. ProcureWise handles this by showing policy evidence, tool results, and risk reasons. The agent also avoids excessive agency because it cannot create a purchase order, sign a contract, or approve vendor risk by itself.

The project follows ideas from the NIST AI Risk Management Framework and OWASP guidance for LLM systems. These sources stress governance, transparency, risk measurement, privacy, and human control. ProcureWise reflects these ideas by keeping humans in charge and showing the evidence behind its output.

## Documentation

The project includes documentation for the final submission package. The README explains what the project is and how to run it. The architecture document explains the workflow and components. The deployment guide explains local, Docker, and future production deployment. The evaluation document explains the test scenarios and results.

The ethics and security document explains risks such as overreliance, privacy, fairness, prompt injection, and excessive agency. The demo script gives a five-minute video plan. The proposal and progress report drafts are also included so the team can show the full project process.

The GitHub repository contains the working code, documentation, sample data, launchers, Docker files, and setup guides. The repository is available at `https://github.com/0Fin0/procurewise-AI-agent`. This makes it easier for teammates and the professor to review the project.

The team also created a Discord-ready ZIP package and a team setup guide. These files help teammates on Windows and macOS download and run the app. This is useful because not everyone has the same computer setup.

## Team Contributions

Jesus Arteaga supported the project by helping with the business use case, stakeholder needs, testing scenarios, and presentation planning. His work helped connect the technical agent to a real business problem.

Omar Ferrufino coordinated the technical build. He worked on the agent workflow, RAG and tools implementation, user interface, GitHub repository setup, Docker testing, and documentation coordination. This work helped turn the project into a runnable submission package.

Marie Trejo Sandoval supported the ethics and security analysis, evaluation review, limitations, and report review. Her work helped make sure the project addressed the risks of using AI in a business decision process.

All team members are expected to review the final demo, test the app if possible, and help prepare the final presentation video. The final video should show the app running with at least two examples, including one medium risk case and one high risk case.

## Conclusion

ProcureWise is a practical AI agent for procurement and vendor risk review. It solves a real business problem by helping users understand policy, vendor status, approval paths, and risk level. It uses RAG, tools, a structured workflow, a user interface, Docker deployment, evaluation, and ethics documentation.

The project meets the Track A AI Agent requirements because it is a single agent that performs a meaningful business task. It retrieves knowledge, uses tools, reasons through a workflow, and gives an evidence-based recommendation. It also keeps human approval in place, which is important for safety and accountability.

Future improvements could make the project stronger. The team could add an API-based LLM connection, connect to a real vendor management system, use vector search for RAG, add login controls, and create a more advanced approval workflow. Even without those future upgrades, ProcureWise shows how an AI agent can support a real business process in a responsible way.

## Works Cited

Bahree, Amit. Generative AI in Action.

Infante, Roberto. AI Agents and Applications With LangChain, LangGraph, and MCP.

Baum, David. Generative AI and LLMs for Dummies.

Docker. "Dockerfile Overview." Docker Docs, https://docs.docker.com/build/concepts/dockerfile/.

LangChain. "LangGraph Overview." Docs by LangChain, https://docs.langchain.com/oss/python/langgraph.

National Institute of Standards and Technology. "Artificial Intelligence Risk Management Framework." NIST, https://www.nist.gov/itl/ai-risk-management-framework.

OWASP. "OWASP Top 10 for Large Language Model Applications." OWASP, https://owasp.org/www-project-top-10-for-large-language-model-applications.
