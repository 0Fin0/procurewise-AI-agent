from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Evidence:
    source: str
    heading: str
    text: str
    score: float


@dataclass
class VendorProfile:
    vendor_id: str
    name: str
    risk_rating: str
    security_review_date: str
    soc2: str
    insurance_status: str
    active_contract: str
    data_sensitivity_allowed: str
    notes: str


@dataclass
class RequestFacts:
    raw_text: str
    amount: float | None = None
    vendor_name: str | None = None
    department: str | None = None
    category: str | None = None
    handles_sensitive_data: bool = False


@dataclass
class ToolResult:
    name: str
    status: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    request: str
    recommendation: str
    risk_level: str
    approval_path: str
    policy_evidence: list[Evidence]
    tool_results: list[ToolResult]
    next_steps: list[str]
    case_id: str | None = None
    missing_intake_fields: list[str] = field(default_factory=list)
    decision_status: str = ""
    recommended_human_action: str = ""

    def to_markdown(self) -> str:
        evidence_lines = [
            f"- {item.source} / {item.heading}: {item.text}" for item in self.policy_evidence
        ]
        tool_lines = [
            f"- {tool.name}: {tool.status} - {tool.details}" for tool in self.tool_results
        ]
        next_step_lines = [f"- {step}" for step in self.next_steps]
        return "\n".join(
            [
                f"# ProcureWise Recommendation",
                "",
                f"**Risk level:** {self.risk_level}",
                f"**Approval path:** {self.approval_path}",
                f"**Case ID:** {self.case_id or 'not created'}",
                f"**Missing intake fields:** {', '.join(self.missing_intake_fields) or 'none'}",
                f"**Decision status:** {self.decision_status or 'not set'}",
                f"**Recommended human action:** {self.recommended_human_action or 'not set'}",
                "",
                "## Recommendation",
                self.recommendation,
                "",
                "## Policy Evidence",
                *evidence_lines,
                "",
                "## Tool Results",
                *tool_lines,
                "",
                "## Next Steps",
                *next_step_lines,
            ]
        )
