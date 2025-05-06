"""
Tests for API endpoints.
"""

def test_create_graph(client, sample_graph_data):
    """
    Tests graph creation through the API.
    """
    response = client.post("/api/graph/", json=sample_graph_data)
    
    assert response.status_code == 201
    
    data = response.json()
    assert "id" in data
    assert isinstance(data["id"], int)


def test_create_graph_with_cycle(client):
    """
    Tests creating a graph with a cycle through the API.
    """
    graph_data = {
        "nodes": [
            {"name": "a"},
            {"name": "b"},
            {"name": "c"}
        ],
        "edges": [
            {"source": "a", "target": "b"},
            {"source": "b", "target": "c"},
            {"source": "c", "target": "a"}  # This creates a cycle
        ]
    }
    
    response = client.post("/api/graph/", json=graph_data)
    
    assert response.status_code == 400
    
    data = response.json()
    assert "cyclic" in data["detail"]["message"].lower()


def test_create_graph_with_invalid_node_name(client):
    """
    Tests creating a graph with an invalid node name.
    """
    graph_data = {
        "nodes": [
            {"name": "a"},
            {"name": "b123"}  # Does not meet the requirement (only Latin letters)
        ],
        "edges": []
    }
    
    response = client.post("/api/graph/", json=graph_data)
    
    assert response.status_code == 422


def test_get_graph(client, created_graph):
    """
    Tests retrieving graph information.
    """
    response = client.get(f"/api/graph/{created_graph}/")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "id" in data
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) == 4
    assert len(data["edges"]) == 3


def test_get_nonexistent_graph(client):
    """
    Tests retrieving a nonexistent graph.
    """
    response = client.get("/api/graph/999/")
    
    assert response.status_code == 404


def test_get_adjacency_list(client, created_graph):
    """
    Tests retrieving the adjacency list.
    """
    response = client.get(f"/api/graph/{created_graph}/adjacency_list")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "adjacency_list" in data
    
    adj_list = data["adjacency_list"]
    assert "a" in adj_list
    assert "b" in adj_list
    assert "c" in adj_list
    assert "d" in adj_list
    assert adj_list["a"] == ["b"]
    assert adj_list["b"] == ["c"]
    assert adj_list["c"] == ["d"]
    assert adj_list["d"] == []


def test_get_reverse_adjacency_list(client, created_graph):
    """
    Tests retrieving the reverse adjacency list.
    """
    response = client.get(f"/api/graph/{created_graph}/reverse_adjacency_list")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "adjacency_list" in data
    
    adj_list = data["adjacency_list"]
    assert "a" in adj_list
    assert "b" in adj_list
    assert "c" in adj_list
    assert "d" in adj_list
    assert adj_list["a"] == []
    assert adj_list["b"] == ["a"]
    assert adj_list["c"] == ["b"]
    assert adj_list["d"] == ["c"]


def test_delete_node(client, created_graph):
    """
    Tests deleting a node from the graph.
    """
    response = client.delete(f"/api/graph/{created_graph}/node/b")
    
    assert response.status_code == 204
    
    response = client.get(f"/api/graph/{created_graph}/")
    data = response.json()
    
    node_names = [node["name"] for node in data["nodes"]]
    assert "a" in node_names
    assert "b" not in node_names
    assert "c" in node_names
    assert "d" in node_names
    assert len(data["edges"]) == 1


def test_create_graph_without_edges(client):
    """
    Tests the creation of a graph without edges.
    """
    graph_data = {
        "nodes": [
            {"name": "a"},
            {"name": "b"},
            {"name": "c"}
        ],
        "edges": []
    }
    
    response = client.post("/api/graph/", json=graph_data)
    
    assert response.status_code == 201


def test_create_graph_with_single_node(client):
    """
    Tests the creation of a graph with a single node.
    """
    graph_data = {
        "nodes": [
            {"name": "a"}
        ],
        "edges": []
    }
    
    response = client.post("/api/graph/", json=graph_data)
    
    assert response.status_code == 201


def test_create_empty_graph(client):
    """
    Tests the creation of an empty graph (without nodes).
    """
    graph_data = {
        "nodes": [],
        "edges": []
    }
    
    response = client.post("/api/graph/", json=graph_data)
    
    assert response.status_code == 400
    assert "Graph must contain at least one node." in response.json()["detail"]["message"]
