import pytest

from aceest import create_app


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
