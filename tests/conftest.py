import pytest
from app import create_app
import database.db as database

@pytest.fixture(scope="session", autouse=True)
def setup_test_database(tmp_path_factory):
    """Never reset the database used by the running website."""
    original_path, original_mysql = database.SQLITE_DB_PATH, database.USE_MYSQL
    database.SQLITE_DB_PATH = tmp_path_factory.mktemp("workshop_tests") / "workshop.db"
    database.USE_MYSQL = False
    database.init_db()
    yield
    database.SQLITE_DB_PATH, database.USE_MYSQL = original_path, original_mysql

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key"
    })
    yield app


@pytest.fixture(autouse=True)
def disable_external_ai_during_tests(monkeypatch):
    """Automated tests must remain deterministic even when a real API key is set."""
    from routes.ai_routes import ai_service
    monkeypatch.setattr(ai_service.gemini_service, 'client', None)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """Returns a client logged in as Quản lý xưởng."""
    with client.session_transaction() as sess:
        sess['user_id'] = 2
        sess['user_name'] = 'Nguyễn Văn Quản Lý'
        sess['user_email'] = 'manager@workshop.edu.vn'
        sess['user_role'] = 'QuanLyXuong'
    return client

@pytest.fixture
def worker_client(client):
    """Returns a client logged in as Nhân viên."""
    with client.session_transaction() as sess:
        sess['user_id'] = 4
        sess['user_name'] = 'Lê Văn Công Nhân'
        sess['user_email'] = 'worker@workshop.edu.vn'
        sess['user_role'] = 'NhanVien'
    return client

@pytest.fixture
def admin_client(client):
    """Returns a client logged in as Admin."""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_name'] = 'Quản Trị Viên'
        sess['user_email'] = 'admin@workshop.edu.vn'
        sess['user_role'] = 'Admin'
    return client
