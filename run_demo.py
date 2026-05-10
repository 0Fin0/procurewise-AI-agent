from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from procurewise.agent import ProcureWiseAgent


DEMO_REQUEST = (
    "We need to buy a $42,000 annual subscription from CloudDesk AI for the "
    "Customer Success team. It will process customer emails and support tickets. "
    "Can we approve it this week?"
)


def main() -> None:
    agent = ProcureWiseAgent()
    result = agent.run(DEMO_REQUEST)
    print(result.to_markdown())


if __name__ == "__main__":
    main()
