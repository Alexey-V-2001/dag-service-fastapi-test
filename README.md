# DAG Service

Service for Working with Directed Acyclic Graphs (DAG).

---

## Technical Specification

Develop a FastAPI service for storing and displaying directed acyclic graphs (DAGs) (hereafter "the service") with PostgreSQL as the database.  

### Technology Stack  

* **Language**: Python 3.11  
* **Framework**: FastAPI  
* **Database**: PostgreSQL 13  
* **ORM**: SQLAlchemy 2.0+ permitted (optional)  

### Graph Requirements  

The service must enforce these constraints. API attempts to create/modify graphs violating these requirements must return client errors. Error codes and messages must match the provided openapi.json specification.  

1. **Graph must**:  
    - Be directed and acyclic  
    - Contain at least one node  
2. **Node names must**:  
    - Use only Latin characters  
    - Be ≤255 characters  
    - Be unique within a graph (duplicates allowed across different graphs)  
3. **Only one edge permitted between any two nodes**  

### API Specifications  

1. **HTTP API** must fully comply with provided openapi.json:  
    - Response codes and request schemas must match the specification exactly  
2. **Scalability requirements**:  
    - Support ≥1,000 concurrent graphs  
    - Handle ≥100 nodes per graph  
    - Manage ≥1,000 edges per graph  
3. **Error handling**:  
    - Database integrity violations must NOT return "500 Internal Server Error"  
    - Error messages must be informative and actionable  

### Graph Representation Examples  

#### Node-Edge List  
```json  
{  
    "nodes": [  
        {"name": "a"},  
        {"name": "b"},  
        {"name": "c"},  
        {"name": "d"}  
    ],  
    "edges": [  
        {"source": "a", "target": "c"},  
        {"source": "b", "target": "c"},  
        {"source": "c", "target": "d"}  
    ]  
}  
```

#### Adjacency List  
```json  
{  
    "adjacency_list": {  
        "a": ["c"],  
        "c": ["d"],  
        "d": [],  
        "b": ["c"]  
    }  
}  
```

#### Transposed Graph Adjacency List  
```json  
{  
    "adjacency_list": {  
        "a": [],  
        "c": ["a", "b"],  
        "d": ["c"],  
        "b": []  
    }  
}  
```

### Testing Requirements  

- **≥80% test coverage** using pytest  
- Utilize FastAPI's built-in TestClient  
- Validate all constraint enforcement mechanisms  
- Test edge cases (e.g., cycle creation attempts, duplicate nodes/edges)  

---

