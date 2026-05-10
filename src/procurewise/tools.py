from __future__ import annotations

import csv
import json
import re
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from .config import CASE_DIR, VENDOR_FILE
from .schemas import RequestFacts, ToolResult, VendorProfile


AMOUNT_PATTERN = re.compile(r"\$?\s*([0-9][0-9,]*(?:\.\d+)?)\s*(k|thousand|m|million)?", re.I)
DEPARTMENT_PATTERN = re.compile(r"(?:for|department:)\s+(?:the\s+)?([A-Za-z &]+?)(?: team| department|\.|,|$)", re.I)


class ProcurementTools:
    def __init__(self, vendor_file: Path = VENDOR_FILE, case_dir: Path = CASE_DIR) -> None:
        self.vendor_file = vendor_file
        self.case_dir = case_dir
        self.vendors = self._load_vendors()

    def extract_request_facts(self, request: str) -> tuple[RequestFacts, ToolResult]:
        amount = self._extract_amount(request)
        vendor = self._extract_vendor(request)
        department = self._extract_department(request)
        category = self._extract_category(request)
        handles_sensitive_data = self._handles_sensitive_data(request)
        facts = RequestFacts(
            raw_text=request,
            amount=amount,
            vendor_name=vendor,
            department=department,
            category=category,
            handles_sensitive_data=handles_sensitive_data,
        )
        return facts, ToolResult(
            name="request_parser",
            status="completed",
            details={
                "amount": amount,
                "vendor": vendor,
                "department": department,
                "category": category,
                "handles_sensitive_data": handles_sensitive_data,
            },
        )

    def lookup_vendor(self, facts: RequestFacts) -> tuple[VendorProfile | None, ToolResult]:
        if not facts.vendor_name:
            return None, ToolResult(
                name="vendor_lookup",
                status="needs_review",
                details={"message": "No vendor name was detected in the request."},
            )

        for vendor in self.vendors:
            if vendor.name.lower() in facts.vendor_name.lower() or facts.vendor_name.lower() in vendor.name.lower():
                return vendor, ToolResult(
                    name="vendor_lookup",
                    status="completed",
                    details={
                        "vendor_id": vendor.vendor_id,
                        "name": vendor.name,
                        "risk_rating": vendor.risk_rating,
                        "active_contract": vendor.active_contract,
                        "soc2": vendor.soc2,
                    },
                )

        return None, ToolResult(
            name="vendor_lookup",
            status="not_found",
            details={"message": f"{facts.vendor_name} was not found in the vendor database."},
        )

    def determine_approval_path(self, facts: RequestFacts) -> ToolResult:
        amount = facts.amount or 0
        if amount >= 100000:
            path = "CFO, Legal, Security, and Procurement Director approval required"
            tier = "enterprise"
        elif amount >= 25000:
            path = "Department VP, Procurement, and Security review required"
            tier = "standard_review"
        elif amount >= 5000:
            path = "Department manager and Procurement approval required"
            tier = "manager_review"
        else:
            path = "Requester manager approval required"
            tier = "low_spend"

        return ToolResult(
            name="approval_router",
            status="completed",
            details={"amount": amount, "tier": tier, "approval_path": path},
        )

    def assess_risk(self, facts: RequestFacts, vendor: VendorProfile | None) -> ToolResult:
        points = 0
        reasons: list[str] = []

        if facts.amount and facts.amount >= 25000:
            points += 2
            reasons.append("Spend is above the standard procurement review threshold.")
        if facts.handles_sensitive_data:
            points += 3
            reasons.append("The request may involve customer, employee, or confidential data.")
        if vendor is None:
            points += 3
            reasons.append("Vendor could not be matched to the approved vendor database.")
        else:
            if vendor.risk_rating.lower() == "high":
                points += 4
                reasons.append("Vendor has a high risk rating.")
            elif vendor.risk_rating.lower() == "medium":
                points += 2
                reasons.append("Vendor has a medium risk rating.")
            if vendor.soc2.lower() != "yes":
                points += 2
                reasons.append("SOC 2 status is missing or not confirmed.")
            if vendor.active_contract.lower() != "yes":
                points += 2
                reasons.append("No active contract is on file.")

        if points >= 8:
            level = "high"
        elif points >= 3:
            level = "medium"
        else:
            level = "low"

        return ToolResult(
            name="risk_scorer",
            status="completed",
            details={"risk_level": level, "score": points, "reasons": reasons},
        )

    def create_case(
        self,
        facts: RequestFacts,
        vendor: VendorProfile | None,
        approval: ToolResult,
        risk: ToolResult,
        recommendation: str,
    ) -> ToolResult:
        self.case_dir.mkdir(parents=True, exist_ok=True)
        case_id = f"PW-{datetime.utcnow().strftime('%Y%m%d')}-{uuid4().hex[:6].upper()}"
        payload = {
            "case_id": case_id,
            "created_at_utc": datetime.utcnow().isoformat(timespec="seconds"),
            "request": facts.raw_text,
            "facts": {
                "amount": facts.amount,
                "vendor_name": facts.vendor_name,
                "department": facts.department,
                "category": facts.category,
                "handles_sensitive_data": facts.handles_sensitive_data,
            },
            "vendor": vendor.__dict__ if vendor else None,
            "approval": approval.details,
            "risk": risk.details,
            "recommendation": recommendation,
        }
        (self.case_dir / f"{case_id}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return ToolResult(
            name="case_writer",
            status="completed",
            details={"case_id": case_id, "path": str(self.case_dir / f"{case_id}.json")},
        )

    def _load_vendors(self) -> list[VendorProfile]:
        vendors: list[VendorProfile] = []
        with self.vendor_file.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                vendors.append(VendorProfile(**row))
        return vendors

    def _extract_amount(self, text: str) -> float | None:
        candidates: list[float] = []
        for match in AMOUNT_PATTERN.finditer(text):
            value = float(match.group(1).replace(",", ""))
            suffix = (match.group(2) or "").lower()
            if suffix in {"k", "thousand"}:
                value *= 1000
            elif suffix in {"m", "million"}:
                value *= 1000000
            candidates.append(value)
        return max(candidates) if candidates else None

    def _extract_vendor(self, text: str) -> str | None:
        lower_text = text.lower()
        for vendor in self.vendors:
            if vendor.name.lower() in lower_text:
                return vendor.name
        explicit = re.search(r"(?:vendor|from|with)\s*[:\-]?\s*([A-Z][A-Za-z0-9 &.-]{2,40})", text)
        if explicit:
            return explicit.group(1).strip().rstrip(".")
        return None

    def _extract_department(self, text: str) -> str | None:
        match = DEPARTMENT_PATTERN.search(text)
        return match.group(1).strip() if match else None

    def _extract_category(self, text: str) -> str | None:
        categories = {
            "software": ["subscription", "software", "saas", "license", "platform"],
            "professional_services": ["consulting", "implementation", "services"],
            "hardware": ["laptop", "server", "device", "hardware"],
            "marketing": ["campaign", "advertising", "event", "sponsorship"],
        }
        lower_text = text.lower()
        for category, terms in categories.items():
            if any(term in lower_text for term in terms):
                return category
        return "general"

    def _handles_sensitive_data(self, text: str) -> bool:
        terms = [
            "customer",
            "employee",
            "support ticket",
            "email",
            "pii",
            "personal data",
            "financial",
            "confidential",
            "student",
        ]
        lower_text = text.lower()
        return any(term in lower_text for term in terms)
