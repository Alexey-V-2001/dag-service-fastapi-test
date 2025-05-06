"""
Tests for business logic functions (service layer).
"""

import pytest
from app.schemas import GraphCreate, NodeBase, EdgeBase
from app.services import (
    create_graph, 
    get_graph, 
    get_adjacency_list, 
    get_reverse_adjacency_list, 
    delete_node,
    is_acyclic
)


def test_create_graph_service(db_session):
    """
    Tests graph creation via service function.
    """
    graph_data = GraphCreate(
        nodes=[
            NodeBase(name="a"),
            NodeBase(name="b"),
            NodeBase(name="c")
        ],
        edges=[
            EdgeBase(source="a", target="b"),
            EdgeBase(source="b", target="c")
        ]
    )
    
    graph_id = create_graph(db_session, graph_data)
    
    assert graph_id is not None
    
    graph = get_graph(db_session, graph_id)
    assert graph is not None
    assert graph["id"] == graph_id
    assert len(graph["nodes"]) == 3
    assert len(graph["edges"]) == 2


def test_create_graph_with_cycle_service(db_session):
    """
    Tests cyclic graph creation via service function.
    """
    graph_data = GraphCreate(
        nodes=[
            NodeBase(name="a"),
            NodeBase(name="b"),
            NodeBase(name="c")
        ],
        edges=[
            EdgeBase(source="a", target="b"),
            EdgeBase(source="b", target="c"),
            EdgeBase(source="c", target="a")  # This creates a cycle
        ]
    )
    
    # Creation attempt should raise exception
    with pytest.raises(ValueError) as excinfo:
        create_graph(db_session, graph_data)
    
    assert "cyclic" in str(excinfo.value).lower()


def test_is_acyclic(db_session):
    """
    Tests acyclicity check function.
    """
    graph_data = GraphCreate(
        nodes=[
            NodeBase(name="a"),
            NodeBase(name="b"),
            NodeBase(name="c")
        ],
        edges=[
            EdgeBase(source="a", target="b"),
            EdgeBase(source="b", target="c")
        ]
    )
    
    graph_id = create_graph(db_session, graph_data)
    adjacency_list = get_adjacency_list(db_session, graph_id)
    print(adjacency_list)
    
    assert is_acyclic(adjacency_list) is True


def test_get_adjacency_list_service(db_session):
    """
    Tests adjacency list retrieval function.
    """
    graph_data = GraphCreate(
        nodes=[
            NodeBase(name="a"),
            NodeBase(name="b"),
            NodeBase(name="c")
        ],
        edges=[
            EdgeBase(source="a", target="b"),
            EdgeBase(source="b", target="c")
        ]
    )
    
    graph_id = create_graph(db_session, graph_data)
    
    adj_list = get_adjacency_list(db_session, graph_id)
    
    assert "a" in adj_list
    assert "b" in adj_list
    assert "c" in adj_list
    assert adj_list["a"] == ["b"]
    assert adj_list["b"] == ["c"]
    assert adj_list["c"] == []


def test_get_reverse_adjacency_list_service(db_session):
    """
    Tests reverse adjacency list retrieval function.
    """
    graph_data = GraphCreate(
        nodes=[
            NodeBase(name="a"),
            NodeBase(name="b"),
            NodeBase(name="c")
        ],
        edges=[
            EdgeBase(source="a", target="b"),
            EdgeBase(source="b", target="c")
        ]
    )
    
    graph_id = create_graph(db_session, graph_data)
    
    rev_adj_list = get_reverse_adjacency_list(db_session, graph_id)
    
    assert "a" in rev_adj_list
    assert "b" in rev_adj_list
    assert "c" in rev_adj_list
    assert rev_adj_list["a"] == []
    assert rev_adj_list["b"] == ["a"]
    assert rev_adj_list["c"] == ["b"]


def test_delete_node_service(db_session):
    """
    Tests node deletion function.
    """
    graph_data = GraphCreate(
        nodes=[
            NodeBase(name="a"),
            NodeBase(name="b"),
            NodeBase(name="c")
        ],
        edges=[
            EdgeBase(source="a", target="b"),
            EdgeBase(source="b", target="c")
        ]
    )
    
    graph_id = create_graph(db_session, graph_data)
    
    result = delete_node(db_session, graph_id, "b")
    assert result is True
    
    graph = get_graph(db_session, graph_id)
    node_names = [node["name"] for node in graph["nodes"]]
    assert "a" in node_names
    assert "b" not in node_names
    assert "c" in node_names
    assert len(graph["edges"]) == 0  # All edges should be removed
