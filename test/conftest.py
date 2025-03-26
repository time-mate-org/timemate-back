from fastapi.testclient import TestClient
import pytest
from sqlmodel import SQLModel, Session, create_engine
from database.engine import get_session, engine
from main import app

# Configuração do banco de testes
TEST_SQLITE_URL = "sqlite:///:memory:?cache=shared"
connect_args = {"check_same_thread": False}
test_engine = create_engine(
    TEST_SQLITE_URL, echo=False, connect_args=connect_args)

# Fixture para criar as tabelas e fornecer sessão


@pytest.fixture(autouse=True)
def create_tables():
    with test_engine.connect() as conn:
        SQLModel.metadata.create_all(conn)
        conn.commit()  # Garanta o commit explícito
        yield
        SQLModel.metadata.drop_all(conn)


@pytest.fixture(name='db_session', autouse=True)
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(name="client")
def fixture_client(db_session: Session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_session] = override_get_db
    return TestClient(app)
