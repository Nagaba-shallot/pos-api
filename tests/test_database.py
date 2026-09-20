import database
from database import engine


def test_tests_run_on_in_memory_sqlite():
    assert engine.dialect.name == "sqlite"
    assert str(engine.url) == "sqlite://"
    assert "postgres" not in str(engine.url)


def test_development_default_is_still_postgresql():
    assert database.DEFAULT_DATABASE_URL.startswith("postgresql://")


def test_sqlite_foreign_keys_are_enforced():
    with engine.connect() as connection:
        assert connection.exec_driver_sql("PRAGMA foreign_keys").scalar() == 1


def test_isolation_step_1_create_data(client):
    response = client.post("/categories/", json={"name": "Left behind?"})

    assert response.status_code == 201
    assert len(client.get("/categories/").json()) == 1


def test_isolation_step_2_data_from_previous_test_is_gone(client):
    assert client.get("/categories/").json() == []