from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    GraphCreate, 
    GraphCreateResponse, 
    GraphRead, 
    AdjacencyList, 
    ErrorResponse,
    HTTPValidationError
)
from app.services import (
    create_graph, 
    get_graph, 
    get_adjacency_list, 
    get_reverse_adjacency_list, 
    delete_node
)

router = APIRouter(tags=["Graph Operations"])


@router.post(
    "/", 
    response_model=GraphCreateResponse, 
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Graph creation error"},
        422: {"model": HTTPValidationError, "description": "Input validation error"}
    }
)
def create_graph_endpoint(
    graph_data: GraphCreate,
    db: Session = Depends(get_db)
):
    """
    Creates a new graph.
    
    - **graph_data**: Graph creation data (nodes and edges)
    
    Returns:
        Created graph ID
    """
    try:
        graph_id = create_graph(db, graph_data)
        return {"id": graph_id}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": str(e)}
        )


@router.get(
    "/{graph_id}/", 
    response_model=GraphRead,
    responses={
        404: {"model": ErrorResponse, "description": "Graph not found"},
        422: {"model": HTTPValidationError, "description": "Input validation error"}
    }
)
def read_graph(
    graph_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieves graph information.
    
    - **graph_id**: Graph ID
    
    Returns:
        Graph data (nodes and edges)
    """
    graph = get_graph(db, graph_id)
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"Graph with ID {graph_id} not found"}
        )
    return graph


@router.get(
    "/{graph_id}/adjacency_list", 
    response_model=AdjacencyList,
    responses={
        404: {"model": ErrorResponse, "description": "Graph not found"},
        422: {"model": HTTPValidationError, "description": "Input validation error"}
    }
)
def get_adjacency_list_endpoint(
    graph_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieves graph's adjacency list.
    
    - **graph_id**: Graph ID
    
    Returns:
        Graph adjacency list
    """
    graph = get_graph(db, graph_id)
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"Graph with ID {graph_id} not found"}
        )
    
    adjacency_list = get_adjacency_list(db, graph_id)
    return {"adjacency_list": adjacency_list}


@router.get(
    "/{graph_id}/reverse_adjacency_list", 
    response_model=AdjacencyList,
    responses={
        404: {"model": ErrorResponse, "description": "Graph not found"},
        422: {"model": HTTPValidationError, "description": "Input validation error"}
    }
)
def get_reverse_adjacency_list_endpoint(
    graph_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieves reverse adjacency list (transposed graph).
    
    - **graph_id**: Graph ID
    
    Returns:
        Graph's reverse adjacency list
    """
    graph = get_graph(db, graph_id)
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"Graph with ID {graph_id} not found"}
        )
    
    reverse_adjacency_list = get_reverse_adjacency_list(db, graph_id)
    return {"adjacency_list": reverse_adjacency_list}


@router.delete(
    "/{graph_id}/node/{node_name}", 
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse, "description": "Graph or node not found"},
        422: {"model": HTTPValidationError, "description": "Input validation error"}
    }
)
def delete_node_endpoint(
    graph_id: int,
    node_name: str,
    db: Session = Depends(get_db)
):
    """
    Deletes a node from the graph.
    
    - **graph_id**: Graph ID
    - **node_name**: Node name
    
    Returns:
        204 No Content on success
    """
    graph = get_graph(db, graph_id)
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"Graph with ID {graph_id} not found"}
        )
    
    success = delete_node(db, graph_id, node_name)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"Node '{node_name}' not found in graph {graph_id}"}
        )
    
    return None
