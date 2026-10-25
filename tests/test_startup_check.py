from backend import startup_check


def test_container_startup_fails_closed_when_pin_or_hash_check_fails(monkeypatch, capsys):
    monkeypatch.setattr(
        startup_check,
        "pinned_model_cache_status",
        lambda: (False, "model.safetensors hash mismatch"),
    )

    assert startup_check.main() == 1
    assert "Startup blocked" in capsys.readouterr().err


def test_container_startup_accepts_verified_local_artifacts(monkeypatch, capsys):
    monkeypatch.setattr(startup_check, "pinned_model_cache_status", lambda: (True, ""))

    assert startup_check.main() == 0
    assert "hashes verified" in capsys.readouterr().out
