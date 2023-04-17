import pytest
from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture(scope="function", autouse=True)
def _set_notify_settings(monkeypatch: MonkeyPatch):
    monkeypatch.setenv(
        "NOTIFY_API_KEY",
        "LS0zBhVFhnEycXZxckovSExXW",
    )
