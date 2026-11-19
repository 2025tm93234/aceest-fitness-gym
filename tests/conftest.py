import os

import pytest

from aceest import MODULES, create_app, versions

ALL_MODULES = {m.__name__.rsplit(".", 1)[-1] for m in MODULES}


def pytest_collection_modifyitems(config, items):
    """Run only the tests of modules shipped by APP_VERSION (default: latest)."""
    release = versions.canonical(os.environ.get("APP_VERSION", versions.LATEST))
    enabled = set(versions.module_names(release))
    for item in items:
        module = item.path.stem.replace("test_", "", 1)
        if module in ALL_MODULES and module not in enabled:
            item.add_marker(pytest.mark.skip(reason=f"{module} is not part of ACEest {release}"))


@pytest.fixture
def app(tmp_path):
    flask_app = create_app(db_path=str(tmp_path / "test.db"))
    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def make_client(client):
    """Create a client through the API and return its name."""

    def _make(name="Ravi", **fields):
        response = client.post("/clients", json=dict(name=name, **fields))
        assert response.status_code == 201, response.get_json()
        return name

    return _make
