from procurewise.retriever import PolicyRetriever


def test_retriever_finds_security_policy_for_sensitive_data():
    retriever = PolicyRetriever()
    evidence = retriever.search("vendor will process customer emails and support tickets")
    assert evidence
    assert any("Security" in item.heading or "Data" in item.heading for item in evidence)

