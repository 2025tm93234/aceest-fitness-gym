import pytest

from aceest import create_app, versions

ALL_VERSIONS = list(versions.RELEASES) + list(versions.ALIASES)


def make(tmp_path, version):
    app = create_app(db_path=str(tmp_path / "v.db"), version=version)
    app.config["TESTING"] = True
    return app.test_client()


@pytest.mark.parametrize("version", ALL_VERSIONS)
def test_every_version_boots_and_reports_itself(tmp_path, version):
    client = make(tmp_path, version)
    body = client.get("/version").get_json()
    assert body["version"] == versions.canonical(version)
    assert sorted(body["features"]) == sorted(versions.module_names(version))
    assert client.get("/health").status_code == 200


def test_version_header_is_added_to_every_response(tmp_path):
    response = make(tmp_path, "2.2.1").get("/health")
    assert response.headers["X-App-Version"] == "2.2.1"


def test_releases_are_strictly_cumulative():
    previous = set()
    for release in versions.RELEASES:
        current = set(versions.module_names(release))
        assert previous < current, f"{release} adds nothing"
        previous = current


def test_aliases_ship_identical_features():
    for alias, release in versions.ALIASES.items():
        assert versions.module_names(alias) == versions.module_names(release)


def test_latest_release_ships_every_module():
    from aceest import MODULES

    every = {m.__name__.rsplit(".", 1)[-1] for m in MODULES}
    assert set(versions.module_names(versions.LATEST)) == every


def test_unknown_version_is_rejected():
    with pytest.raises(ValueError):
        versions.canonical("9.9.9")


def test_features_only_appear_in_the_release_that_adds_them(tmp_path):
    assert make(tmp_path, "1.0").get("/clients").status_code == 404
    assert make(tmp_path, "1.1").get("/clients").status_code == 200
    assert make(tmp_path, "2.2.4").get("/analytics/overview").status_code == 404
    assert make(tmp_path, "3.2.4").get("/analytics/overview").status_code == 200
