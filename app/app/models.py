from datetime import datetime, timezone
from app.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship

class Graph(Base):
    __tablename__ = "graphs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    nodes = relationship("Node", back_populates="graph", cascade="all, delete-orphan")
    edges = relationship("Edge", back_populates="graph", cascade="all, delete-orphan")

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    graph_id = Column(Integer, ForeignKey("graphs.id", ondelete="CASCADE"))

    graph = relationship("Graph", back_populates="nodes")
    outgoing_edges = relationship("Edge", back_populates="source", foreign_keys="Edge.source_id", cascade="all, delete-orphan")
    incoming_edges = relationship("Edge", back_populates="target", foreign_keys="Edge.target_id", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('name', 'graph_id', name='unique_node_name_per_graph'),
    )

class Edge(Base):
    __tablename__ = "edges"

    id = Column(Integer, primary_key=True, index=True)
    graph_id = Column(Integer, ForeignKey("graphs.id", ondelete="CASCADE"))
    source_id = Column(Integer, ForeignKey("nodes.id", ondelete="CASCADE"))
    target_id = Column(Integer, ForeignKey("nodes.id", ondelete="CASCADE"))

    graph = relationship("Graph", back_populates="edges")
    source = relationship("Node", back_populates="outgoing_edges", foreign_keys=[source_id])
    target = relationship("Node", back_populates="incoming_edges", foreign_keys=[target_id])

    __table_args__ = (
        UniqueConstraint('source_id', 'target_id', 'graph_id', name='unique_edge_per_graph'),
    )