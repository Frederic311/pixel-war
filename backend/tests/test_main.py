import importlib
import sys
from pathlib import Path


class FakeRedis:
    def __init__(self):
        self.store = {}

    def exists(self, key):
        return key in self.store

    def set(self, key, value):
        self.store[key] = value

    def get(self, key):
        return self.store.get(key)

    def ping(self):
        return True


def load_backend_module(monkeypatch):
    repo_root = Path(__file__).resolve().parents[2]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    if "backend.main" in sys.modules:
        return sys.modules["backend.main"]

    fake_redis = FakeRedis()

    import redis as redis_module

    monkeypatch.setattr(
        redis_module,
        "Redis",
        lambda **kwargs: fake_redis,
    )

    backend_main = importlib.import_module("backend.main")
    return backend_main


def test_livez_returns_alive(monkeypatch):
    backend_main = load_backend_module(monkeypatch)
    assert backend_main.livez() == {"status": "alive"}


def test_grid_is_initialized(monkeypatch):
    backend_main = load_backend_module(monkeypatch)
    payload = backend_main.get_grid()

    assert "grid" in payload
    assert len(payload["grid"]) == 50
    assert len(payload["grid"][0]) == 50


def test_update_pixel_changes_grid(monkeypatch):
    backend_main = load_backend_module(monkeypatch)

    backend_main.update_pixel(backend_main.PixelUpdate(x=1, y=2, color=4))
    payload = backend_main.get_grid()

    assert payload["grid"][2][1] == 4