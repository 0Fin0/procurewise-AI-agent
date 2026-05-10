from procurewise.agent import ProcureWiseAgent


def test_agent_returns_recommendation_without_case_file():
    agent = ProcureWiseAgent()
    result = agent.run(
        "We need a $42,000 annual subscription from CloudDesk AI for customer support emails.",
        create_case=False,
    )
    assert result.risk_level in {"medium", "high"}
    assert "CloudDesk AI" in result.recommendation
    assert result.policy_evidence
    assert any(tool.name == "risk_scorer" for tool in result.tool_results)
