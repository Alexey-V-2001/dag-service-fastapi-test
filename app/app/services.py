from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from app.models import Graph, Node, Edge
from app.schemas import GraphCreate

def create_graph(db: Session, graph_data: GraphCreate) -> int:
    """
    Creates a new graph in the database with comprehensive validation.
    
    Args:
        db: Database session
        graph_data: Graph creation data structure
        
    Returns:
        Created graph ID
        
    Raises:
        ValueError: For invalid graph structures or constraints violation
    """
    if not graph_data.nodes:
        raise ValueError("Graph must contain at least one node.")
    
    graph = Graph()
    db.add(graph)
    db.flush()

    nodes_dict = {}

    for node_data in graph_data.nodes:
        if node_data.name in nodes_dict:
            raise ValueError(f"Duplicate node name: {node_data.name}")

        node = Node(name=node_data.name, graph_id=graph.id)
        db.add(node)
        db.flush()
        nodes_dict[node_data.name] = node
    
    if graph_data.edges:
        edge_set = set()

        for edge_data in graph_data.edges:
            if edge_data.source not in nodes_dict:
                raise ValueError(f"Source node not found: {edge_data.source}")
            if edge_data.target not in nodes_dict:
                raise ValueError(f"Target node not found: {edge_data.target}")
            
            if edge_data.source == edge_data.target:
                raise ValueError(f"Self-loop prohibited: {edge_data.source} -> {edge_data.target}")
            
            edge_key = (edge_data.source, edge_data.target)
            if edge_key in edge_set:
                raise ValueError(f"Duplicate edge detected: {edge_data.source} -> {edge_data.target}")
            
            edge_set.add(edge_key)
            
            edge = Edge(
                source_id=nodes_dict[edge_data.source].id,
                target_id=nodes_dict[edge_data.target].id,
                graph_id=graph.id
            )
            db.add(edge)
        
        adjacency_list = get_adjacency_list(db, graph.id)

        if is_acyclic(adjacency_list):
            db.rollback()
            raise ValueError("Invalid graph structure: Cyclic dependencies detected (non-DAG)")
    
    db.commit()

    return graph.id

def get_graph(db: Session, graph_id: int) -> Optional[Dict]:
    """
    Retrieves complete graph structure with topological relationships.
    
    Args:
        db: Database session
        graph_id: Target graph identifier
        
    Returns:
        Structured graph representation or None if not found
    """
    graph = db.query(Graph).filter(Graph.id == graph_id).first()

    if not graph:
        return None
    
    nodes = db.query(Node).filter(Node.graph_id == graph_id).all()
    edges = db.query(Edge).filter(Edge.graph_id == graph_id).all()
    
    node_id_to_name = {node.id: node.name for node in nodes}
    
    result = {
        "id": graph.id,
        "nodes": [{"id": node.id, "name": node.name} for node in nodes],
        "edges": [
            {
                "id": edge.id,
                "source": node_id_to_name[edge.source_id],
                "target": node_id_to_name[edge.target_id]
            }
            for edge in edges
        ]
    }
    
    return result

def delete_node(db: Session, graph_id: int, node_name: str) -> bool:
    """
    Safely removes a node and maintains graph integrity.
    
    Args:
        db: Database session
        graph_id: Parent graph identifier
        node_name: Target node identifier
        
    Returns:
        Success status of deletion operation
    """
    node = db.query(Node).filter(
        Node.graph_id == graph_id,
        Node.name == node_name
    ).first()
    
    if not node:
        return False
    
    db.delete(node)
    db.commit()
    
    return True

def get_adjacency_list(db: Session, graph_id: int) -> Dict[str, List[str]]:
    """
    Generates directional adjacency mapping for graph analysis.
    
    Args:
        db: Database session
        graph_id: Target graph identifier
        
    Returns:
        Adjacency list representation {source: [targets]}
    """
    nodes = db.query(Node).filter(Node.graph_id == graph_id).all()
    edges = db.query(Edge).filter(Edge.graph_id == graph_id).all()
    
    node_id_to_name = {node.id: node.name for node in nodes}
    
    adjacency_list = {node.name: [] for node in nodes}
    
    for edge in edges:
        source_name = node_id_to_name[edge.source_id]
        target_name = node_id_to_name[edge.target_id]
        adjacency_list[source_name].append(target_name)
    
    return adjacency_list

def get_reverse_adjacency_list(db: Session, graph_id: int) -> Dict[str, List[str]]:
    """
    Constructs inverse adjacency mapping for dependency resolution.
    
    Args:
        db: Database session
        graph_id: Target graph identifier
        
    Returns:
        Inverse adjacency list {target: [sources]}
    """
    nodes = db.query(Node).filter(Node.graph_id == graph_id).all()
    edges = db.query(Edge).filter(Edge.graph_id == graph_id).all()
    
    node_id_to_name = {node.id: node.name for node in nodes}
    
    reverse_adjacency_list = {node.name: [] for node in nodes}
    
    for edge in edges:
        source_name = node_id_to_name[edge.source_id]
        target_name = node_id_to_name[edge.target_id]
        reverse_adjacency_list[target_name].append(source_name)
    
    return reverse_adjacency_list


def is_acyclic(adjacency_list: Dict[str, List[str]]) -> bool:
    """
    Executes depth-first search to detect cyclic dependencies.
    
    Args:
        adjacency_list: Graph connection mapping
        
    Returns:
        Cycle detection status (True = cyclic)
    """
    visited = set()
    recursion_stack = set()

    def dfs(current_node: str) -> bool:
        """Depth-first search subroutine for cycle detection."""
        visited.add(current_node)
        recursion_stack.add(current_node)
        
        for neighbor in adjacency_list.get(current_node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in recursion_stack:
                return True
        
        recursion_stack.remove(current_node)
        return False

    return any(dfs(node) for node in adjacency_list if node not in visited)
