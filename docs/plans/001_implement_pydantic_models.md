# Plan: Implement Pydantic Models for BPMN Schema

**Issue**: #1  
**Status**: Draft  
**Assignee**: AI Agent  
**Branch**: `feature/1-implement-pydantic-models`

## Análisis de Impacto

### Archivos a crear
- `src/bpmn_generator/models/schema.py` - Todos los tipos de nodos BPMN
- `src/bpmn_generator/models/state.py` - AgentState y ProcessUpdate
- `tests/unit/models/test_schema.py` - Tests para schema
- `tests/unit/models/test_state.py` - Tests para state

### Nuevas dependencias
- Ninguna (ya están en pyproject.toml)

### Breaking changes
- Ninguno (primera implementación)

---

## Diseño Propuesto

### 1. Schema Models (`schema.py`)

Implementar los 12 tipos de nodos BPMN usando discriminated unions:

**Eventos**: StartEventNode, EndEventNode, BoundaryEventNode  
**Tareas**: UserTaskNode, ServiceTaskNode, ScriptTaskNode, SendTaskNode, ReceiveTaskNode  
**Control**: GatewayNode, SubProcessNode  
**Data**: DataObjectNode, DataObjectReferenceNode

**ProcessArtifact** con validator `validate_graph_integrity()`

### 2. State Models (`state.py`)

**AgentState**, **ProcessUpdate**, **ClarificationQuestion**

---

## Orden de Implementación

1. Eventos (Start, End, Boundary)
2. Tareas (User, Service, Script, Send, Receive)
3. Control Flow (Gateway, SubProcess)
4. Data Architecture (DataObject, DataObjectReference, DataAssociation)
5. BPMNEdge
6. Union type BPMNNode
7. ProcessArtifact con validator
8. state.py (AgentState, ProcessUpdate, ClarificationQuestion)
9. Tests unitarios (100% coverage)

---

## Verificación

```bash
pytest tests/unit/models/ -v --cov=src/bpmn_generator/models
```

**Criterios de Aceptación**:
- [ ] 12 tipos de nodos implementados
- [ ] ProcessArtifact valida referencias
- [ ] Tests pasan con 100% coverage
- [ ] Mypy y Ruff sin errores

**Referencia**: `docs/architecture/02_Modelo_datos_y_estado.md`
