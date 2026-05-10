from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from procurewise import ProcureWiseAgent


st.set_page_config(page_title="ProcureWise Agent", page_icon="PW", layout="wide")

st.title("ProcureWise Agent")

sample = (
    "We need to buy a $42,000 annual subscription from CloudDesk AI for the "
    "Customer Success team. It will process customer emails and support tickets. "
    "Can we approve it this week?"
)

with st.sidebar:
    st.header("Request")
    use_sample = st.button("Load sample")
    create_case = st.checkbox("Create case file", value=True)

if "request_text" not in st.session_state or use_sample:
    st.session_state.request_text = sample

request_text = st.text_area(
    "Purchase request",
    key="request_text",
    height=180,
    placeholder="Paste a procurement request, quote summary, vendor question, or approval request.",
)

run = st.button("Analyze request", type="primary")

if run and request_text.strip():
    with st.spinner("Checking policy, vendor data, approval path, and risk..."):
        agent = ProcureWiseAgent()
        result = agent.run(request_text, create_case=create_case)

    metric_cols = st.columns(3)
    metric_cols[0].metric("Risk level", result.risk_level.title())
    metric_cols[1].metric("Evidence found", len(result.policy_evidence))
    metric_cols[2].metric("Case", result.case_id or "Not created")

    st.subheader("Recommendation")
    st.write(result.recommendation)

    st.subheader("Approval Path")
    st.info(result.approval_path)

    st.subheader("Next Steps")
    for step in result.next_steps:
        st.checkbox(step, value=False)

    st.subheader("Policy Evidence")
    for evidence in result.policy_evidence:
        with st.expander(f"{evidence.source} - {evidence.heading}"):
            st.write(evidence.text)
            st.caption(f"Retrieval score: {evidence.score}")

    st.subheader("Tool Trace")
    st.dataframe(
        [
            {"tool": item.name, "status": item.status, "details": item.details}
            for item in result.tool_results
        ],
        use_container_width=True,
    )
elif run:
    st.warning("Enter a request before running the agent.")

