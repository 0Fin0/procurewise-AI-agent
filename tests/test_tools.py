from procurewise.tools import ProcurementTools


def test_tools_extract_amount_and_vendor():
    tools = ProcurementTools()
    facts, result = tools.extract_request_facts(
        "Buy a $42,000 annual subscription from CloudDesk AI for Customer Success."
    )
    assert result.status == "completed"
    assert facts.amount == 42000
    assert facts.vendor_name == "CloudDesk AI"
    assert facts.department == "Customer Success"
    assert facts.category == "software"


def test_risk_scorer_marks_unknown_sensitive_vendor_high():
    tools = ProcurementTools()
    facts, _ = tools.extract_request_facts(
        "Buy a $30,000 platform from UnknownCo for customer emails."
    )
    risk = tools.assess_risk(facts, vendor=None)
    assert risk.details["risk_level"] == "high"
