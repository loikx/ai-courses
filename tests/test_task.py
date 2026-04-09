from pathlib import Path

import pytest

import task


def test_export_report_rejects_incomplete_source_data(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Экспорт останавливается, если журналы или чек-лист не заполнены."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(task, "CONTEXT_LOGS", [])
    monkeypatch.setattr(task, "RULES_LOGS", [])
    monkeypatch.setattr(task, "MULTICHAT_LOGS", [])
    monkeypatch.setattr(
        task,
        "IMPLEMENTATION_CHECKLIST",
        {
            "models_created": False,
            "cursorrules_created": False,
            "health_endpoint": False,
            "post_subscribe": False,
            "get_subscriptions": False,
            "delete_subscribe": False,
        },
    )

    with pytest.raises(
        ValueError,
        match=r"CONTEXT_LOGS|RULES_LOGS|MULTICHAT_LOGS|IMPLEMENTATION_CHECKLIST",
    ):
        task.export_report()

    assert not (tmp_path / "artifacts" / "report_p3.md").exists()
