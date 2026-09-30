"""Reject false evidence, passing scaffolds and stale task validation."""
import json

import pytest

from PROPOSAL_TEAM.tools.pinecone_knowledge_base import PineconeKnowledgeBase
from PROPOSAL_TEAM.tools.compliance_engine import Block4_EvidenceRetriever, Block5_ComplianceWriter
from QA_TEAM.tools.test_templates import _generate_test_file, _generate_function_tests
from tools.evaluate_workflows import evaluate, resolve_workflow
from tools.task_record import record_task, resume_task


def test_proposal_retrieval_cannot_return_invented_evidence():
    with pytest.raises(NotImplementedError, match="retrieval is not implemented"):
        PineconeKnowledgeBase().search("Proof of compliance")
    assert Block4_EvidenceRetriever().retrieve_evidence([], ["requirement"]) == {}
    text = Block5_ComplianceWriter().generate_response("soc2", "control evidence", [])
    assert "UNVERIFIED DRAFT" in text
    assert "fully addresses" not in text


def test_indexing_is_preparation_not_upload(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("Actual source text: Access controls must be documented.")
    kb = PineconeKnowledgeBase()
    assert kb._extract_text(source) == source.read_text()
    assert kb.index_compliance_document(str(source), "soc2").index_status == "prepared_not_uploaded"
    source.write_text("")
    with pytest.raises(ValueError, match="No source text"):
        kb._extract_text(source)


def test_demo_results_are_explicit(tmp_path):
    kb = PineconeKnowledgeBase(demo_mode=True)
    kb.index_compliance_document(str(tmp_path / "example.pdf"), "soc2")
    results = kb.search("anything")
    assert results and all(r["demo_only"] and not r["verified_evidence"] for r in results)
    assert all(r["relevance_score"] is None for r in results)


def test_qa_mock_template_has_module_and_cannot_claim_passing_coverage():
    component = {"type": "function", "name": "fetch_customer"}
    snippet = _generate_function_tests(component, "customers")
    assert "customers.external_dependency" in snippet
    text = _generate_test_file("customers", [component])
    compile(text, "generated-scaffold", "exec")
    assert "allow_module_level=True" in text
    assert "assert True" not in text


def task_data(artifact):
    return {"task_id": "test-task", "objective": "Validate a deliverable", "team": "CODEX_TEAM",
            "role": "codex-team-manager", "runtime": "codex", "status": "validated",
            "artifacts": [str(artifact)], "checks": [{"name": "content reviewed", "status": "passed"}]}


def test_task_requires_evidence_and_detects_later_changes(tmp_path, monkeypatch):
    from tools import task_record
    # Keep artifacts and state confined to a fixture repository.
    monkeypatch.setattr(task_record, "discover_agents", lambda root: {"CODEX_TEAM": [root / "codex-team-manager.md"]})
    artifact = tmp_path / "report.md"
    artifact.write_text("reviewed output")
    data = task_data(artifact)
    state = tmp_path / "state"
    record_task(data, root=tmp_path, state=state)
    saved = resume_task("test-task", root=tmp_path, state=state)
    assert saved["validation_current"]
    assert saved["record"]["cost_usd"] is None
    artifact.write_text("changed after review")
    assert not resume_task("test-task", root=tmp_path, state=state)["validation_current"]
    data["checks"][0]["status"] = "failed"
    with pytest.raises(ValueError, match="exclusively passing"):
        record_task(data, root=tmp_path, state=state)
    data["task_id"] = "../escape"
    with pytest.raises(ValueError, match="task id"):
        record_task(data, root=tmp_path, state=state)


def test_workflow_contracts_preserve_roles_and_require_send_authorization():
    assert evaluate()["ok"]
    result = resolve_workflow("gmail_send", ["google_workspace_gmail"], [])
    assert result["status"] == "blocked"
    assert result["unauthorized_actions"] == ["send_email"]
