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
