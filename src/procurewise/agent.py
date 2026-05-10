from __future__ import annotations

from typing import Any, TypedDict

from .prompts import RESPONSE_TEMPLATE, SYSTEM_PROMPT
from .retriever import PolicyRetriever
from .schemas import AgentResult, Evidence, RequestFacts, ToolResult, VendorProfile
from .tools import ProcurementTools


class AgentState(TypedDict, total=False):
    request: str
    facts: RequestFacts
    evidence: list[Evidence]
    vendor: VendorProfile | None
    tool_results: list[ToolResult]
    recommendation: str
    next_steps: list[str]
    risk_level: str
    approval_path: str
    case_id: str | None


class ProcureWiseAgent:
    def __init__(self, retriever: PolicyRetriever | None = None, tools: ProcurementTools | None = None) -> None:
        self.retriever = retriever or PolicyRetriever()
        self.tools = tools or ProcurementTools()
        self.graph = self._build_graph_if_available()

    def run(self, request: str, create_case: bool = True) -> AgentResult:
        initial_state: AgentState = {"request": request, "tool_results": []}
        if self.graph is not None:
            state = self.graph.invoke(initial_state)
        else:
            state = self._run_direct(initial_state)

        if create_case:
            case_result = self.tools.create_case(
                state["facts"],
                state.get("vendor"),
                self._find_tool(state["tool_results"], "approval_router"),
                self._find_tool(state["tool_results"], "risk_scorer"),
                state["recommendation"],
            )
            state["tool_results"].append(case_result)
            state["case_id"] = case_result.details["case_id"]

        return AgentResult(
            request=request,
            recommendation=state["recommendation"],
            risk_level=state["risk_level"],
            approval_path=state["approval_path"],
            policy_evidence=state["evidence"],
            tool_results=state["tool_results"],
            next_steps=state["next_steps"],
            case_id=state.get("case_id"),
        )

    def _run_direct(self, state: AgentState) -> AgentState:
        for node in [self._parse_request, self._retrieve_policy, self._run_tools, self._draft_response]:
            state = node(state)
        return state

    def _build_graph_if_available(self) -> Any | None:
        try:
            from langgraph.graph import END, START, StateGraph
        except Exception:
            return None

        try:
            graph = StateGraph(AgentState)
            graph.add_node("parse_request", self._parse_request)
            graph.add_node("retrieve_policy", self._retrieve_policy)
            graph.add_node("run_tools", self._run_tools)
            graph.add_node("draft_response", self._draft_response)
            graph.add_edge(START, "parse_request")
            graph.add_edge("parse_request", "retrieve_policy")
            graph.add_edge("retrieve_policy", "run_tools")
            graph.add_edge("run_tools", "draft_response")
            graph.add_edge("draft_response", END)
            return graph.compile()
        except Exception:
            return None

    def _parse_request(self, state: AgentState) -> AgentState:
        facts, result = self.tools.extract_request_facts(state["request"])
        state["facts"] = facts
        state["tool_results"].append(result)
        return state

    def _retrieve_policy(self, state: AgentState) -> AgentState:
        facts = state["facts"]
        query = " ".join(
            [
                state["request"],
                facts.category or "",
                "sensitive data" if facts.handles_sensitive_data else "",
                "approval threshold vendor risk",
            ]
        )
        state["evidence"] = self.retriever.search(query, top_k=4)
        state["tool_results"].append(
            ToolResult(
                name="policy_retriever",
                status="completed",
                details={"documents_returned": len(state["evidence"])},
            )
        )
        return state

    def _run_tools(self, state: AgentState) -> AgentState:
        vendor, vendor_result = self.tools.lookup_vendor(state["facts"])
        approval = self.tools.determine_approval_path(state["facts"])
        risk = self.tools.assess_risk(state["facts"], vendor)
        state["vendor"] = vendor
        state["tool_results"].extend([vendor_result, approval, risk])
        state["risk_level"] = risk.details["risk_level"]
        state["approval_path"] = approval.details["approval_path"]
        return state

    def _draft_response(self, state: AgentState) -> AgentState:
        state["recommendation"] = self._deterministic_recommendation(state)
        state["next_steps"] = self._next_steps(state)
        return state

    def _deterministic_recommendation(self, state: AgentState) -> str:
        facts = state["facts"]
        risk_level = state["risk_level"]
        vendor = state.get("vendor")
        amount = f"${facts.amount:,.0f}" if facts.amount else "an unspecified amount"
        vendor_name = vendor.name if vendor else (facts.vendor_name or "the requested vendor")

        if risk_level == "high":
            decision = "Do not approve yet."
            reason = "The request needs security and procurement review before commitment."
        elif risk_level == "medium":
            decision = "Conditionally proceed after required review."
            reason = "The request has manageable risk, but approval and evidence gaps must be closed."
        else:
            decision = "Proceed through the standard approval path."
            reason = "The vendor and spend profile appear low risk based on available data."

        evidence_summary = "; ".join(
            f"{item.heading} from {item.source}" for item in state["evidence"][:3]
        )
        return (
            f"{decision} The purchase for {vendor_name} at {amount} is classified as "
            f"{risk_level} risk. {reason} Required approval path: {state['approval_path']}. "
            f"Most relevant policy evidence: {evidence_summary}."
        )

    def _next_steps(self, state: AgentState) -> list[str]:
        facts = state["facts"]
        vendor = state.get("vendor")
        risk_level = state["risk_level"]
        steps = [
            "Attach the business justification, quote, and contract terms to the procurement request.",
            f"Route the request through: {state['approval_path']}.",
        ]
        if vendor is None:
            steps.append("Create or update the vendor profile before purchase approval.")
        elif vendor.soc2.lower() != "yes":
            steps.append("Collect SOC 2 or equivalent security evidence from the vendor.")
        if facts.handles_sensitive_data:
            steps.append("Complete a data protection review before sharing customer or employee data.")
        if risk_level == "high":
            steps.append("Escalate to Security and Legal before issuing a purchase order.")
        return steps

    def _find_tool(self, tools: list[ToolResult], name: str) -> ToolResult:
        for tool in tools:
            if tool.name == name:
                return tool
        raise ValueError(f"Tool result not found: {name}")

    def prompt_preview(self, request: str) -> str:
        evidence = self.retriever.search(request)
        evidence_text = "\n".join(f"- {item.source}: {item.text}" for item in evidence)
        return SYSTEM_PROMPT + "\n" + RESPONSE_TEMPLATE.format(
            request=request,
            evidence=evidence_text,
            tools="Tool results are inserted after parser, vendor lookup, approval routing, and risk scoring run.",
        )
