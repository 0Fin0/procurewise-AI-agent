from __future__ import annotations

from typing import Any, TypedDict

from .llm import RecommendationDrafter
from .prompts import RESPONSE_TEMPLATE, SYSTEM_PROMPT
from .retriever import PolicyRetriever
from .schemas import AgentResult, Evidence, RequestFacts, ToolResult, VendorProfile
from .tools import ProcurementTools


class AgentState(TypedDict, total=False):
    request: str
    facts: RequestFacts
    evidence: list[Evidence]
    vendor: VendorProfile | None
    missing_intake_fields: list[str]
    policy_bypass_attempt: bool
    decision_status: str
    recommended_human_action: str
    tool_results: list[ToolResult]
    recommendation: str
    next_steps: list[str]
    risk_level: str
    approval_path: str
    case_id: str | None


class ProcureWiseAgent:
    def __init__(
        self,
        retriever: PolicyRetriever | None = None,
        tools: ProcurementTools | None = None,
        drafter: RecommendationDrafter | None = None,
    ) -> None:
        self.retriever = retriever or PolicyRetriever()
        self.tools = tools or ProcurementTools()
        self.drafter = drafter or RecommendationDrafter()
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
                self._find_tool(state["tool_results"], "intake_checker"),
                self._find_tool(state["tool_results"], "safety_guard"),
                self._find_tool(state["tool_results"], "decision_advisor"),
                state["evidence"],
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
            missing_intake_fields=state.get("missing_intake_fields", []),
            decision_status=state.get("decision_status", ""),
            recommended_human_action=state.get("recommended_human_action", ""),
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
        safety = self.tools.check_request_safety(state["facts"])
        approval = self.tools.determine_approval_path(state["facts"])
        intake = self.tools.check_intake_completeness(state["facts"])
        risk = self.tools.assess_risk(state["facts"], vendor, safety)
        decision = self.tools.advise_decision(vendor, approval, intake, safety, risk)
        state["vendor"] = vendor
        state["tool_results"].extend([vendor_result, safety, approval, intake, risk, decision])
        state["missing_intake_fields"] = intake.details["missing_required"]
        state["policy_bypass_attempt"] = safety.details["policy_bypass_attempt"]
        state["risk_level"] = risk.details["risk_level"]
        state["approval_path"] = approval.details["approval_path"]
        state["decision_status"] = decision.details["decision_status"]
        state["recommended_human_action"] = decision.details["recommended_human_action"]
        return state

    def _draft_response(self, state: AgentState) -> AgentState:
        fallback = self._deterministic_recommendation(state)
        recommendation, result = self.drafter.draft(state, fallback)
        state["recommendation"] = recommendation
        state["next_steps"] = self._next_steps(state)
        state["tool_results"].append(result)
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
            f"Recommended human action: {state['recommended_human_action']}.",
            f"Route the request through: {state['approval_path']}.",
        ]
        missing_intake = state.get("missing_intake_fields", [])
        if missing_intake:
            steps.insert(
                0,
                "Complete missing intake fields before final approval: "
                + ", ".join(missing_intake)
                + ".",
            )
        else:
            steps.insert(0, "Intake package is complete; preserve evidence with the approval record.")
        if state.get("policy_bypass_attempt"):
            steps.insert(
                0,
                "Do not follow the bypass instruction; continue the documented procurement and security review.",
            )
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
