import re
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict

class NodeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)

    @field_validator('name')
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z]+$', v):
            raise ValueError('Node name must contain only latin letters.')
        return v


class EdgeBase(BaseModel):
    source: str
    target: str

    @field_validator('source', 'target')
    def validate_node_names(cls, v):
        if not re.match(r'^[a-zA-Z+]$', v):
            raise ValueError('Edge name must contain only latin letters.')
        return v


class GraphCreate(BaseModel):
    nodes: List[NodeBase]
    edges: List[EdgeBase]


class NodeRead(NodeBase):
    id: int

    class ConfigDict:
        from_attributes = True


class EdgeRead(EdgeBase):
    id: int

    class ConfigDict:
        from_attributes = True


class GraphRead(BaseModel):
    id: int
    nodes: List[NodeRead]
    edges: List[EdgeRead]

    class ConfigDict:
        from_attributes = True


class GraphCreateResponse(BaseModel):
    id: int


class AdjacencyList(BaseModel):
    adjacency_list: Dict[str, List[str]]


class ErrorResponse(BaseModel):
    message: str
