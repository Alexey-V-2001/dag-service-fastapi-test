"""
Test configuration with fixtures.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def db_engine():
    """
    Creates an in-memory temporary database for tests and removes it afterwards.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    
    yield engine
    
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(db_engine):
    """
    Creates a database session for tests.
    """
    Session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = Session()
    
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """
    Returns a FastAPI test client.
    """
    # Patch the dependency that provides the DB session
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Override the get_db dependency with the test version
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    # Restore the original dependency overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sample_graph_data():
    """
    Returns sample graph data for testing.
    """
    return {
        "nodes": [
            {"name": "a"},
            {"name": "b"},
            {"name": "c"},
            {"name": "d"}
        ],
        "edges": [
            {"source": "a", "target": "b"},
            {"source": "b", "target": "c"},
            {"source": "c", "target": "d"}
        ]
    }


@pytest.fixture
def created_graph(client, sample_graph_data):
    """
    Creates a test graph via the API and returns its ID.
    """
    response = client.post("/api/graph/", json=sample_graph_data)
    assert response.status_code == 201
    return response.json()["id"]
