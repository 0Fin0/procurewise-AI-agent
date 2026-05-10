from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from procurewise.agent import ProcureWiseAgent
from procurewise.retriever import PolicyRetriever
from procurewise.tools import ProcurementTools


def main() -> None:
    agent = ProcureWiseAgent()
    cloud = agent.run(
        "We need to buy a $42,000 annual subscription from CloudDesk AI for the "
        "Customer Success team. It will process customer emails and support tickets.",
        create_case=False,
    )
    assert cloud.risk_level == "medium"
    assert "CloudDesk AI" in cloud.recommendation
    assert cloud.policy_evidence

    northstar = agent.run(
        "Finance wants a $155,000 analytics platform from Northstar Analytics "
        "that will analyze customer revenue and payment trends.",
        create_case=False,
    )
    assert northstar.risk_level == "high"

    tools = ProcurementTools()
    facts, _ = tools.extract_request_facts(
        "Buy a $42,000 annual subscription from CloudDesk AI for the Customer Success team."
    )
    assert facts.amount == 42000
    assert facts.vendor_name == "CloudDesk AI"
    assert facts.department == "Customer Success"

    evidence = PolicyRetriever().search("vendor will process customer emails and support tickets")
    assert evidence

    print("All ProcureWise checks passed.")


if __name__ == "__main__":
    main()

