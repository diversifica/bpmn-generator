# Plan: Implementar Orquestación LangGraph

**Issue**: #7 (Probable)  
**Status**: Draft  
**Assignee**: AI Agent  
**Branch**: `feature/7-implement-orchestration`

## Análisis de Impacto

### Archivos a crear
- `src/bpmn_generator/graph/workflow.py` - Definición del StateGraph
- `src/bpmn_generator/graph/routers.py` - Lógica de ruteo
- `src/bpmn_generator/main.py` - Entry point CLI
- `tests/integration/test_workflow.py` - Tests de integración

### Breaking changes
- Ninguno (es funcionalidad nueva que conecta lo existente)

---

## Diseño Propuesto

### 1. Workflow Definition (`workflow.py`)

```python
def create_graph() -> CompiledGraph:
    workflow = StateGraph(AgentState)
    
    # Habilitar persistencia
    memory = MemorySaver()
    
    # Añadir nodos
    workflow.add_node("analyst", analyzer_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("chat", chat_node)
    workflow.add_node("generator", xml_generator_node)
    
    # Definir flujo
    workflow.set_entry_point("analyst")
    
    workflow.add_edge("analyst", "critic")
    
    workflow.add_conditional_edges(
        "critic",
        route_critic,  # Determina si ir a 'generator' o 'chat'
        {
            "sufficient": "generator",
            "insufficient": "chat"
        }
    )
    
    workflow.add_edge("chat", "analyst") # Vuelve a analizar tras respuesta usuario
    workflow.add_edge("generator", END)
    
    return workflow.compile(checkpointer=memory, interrupt_before=["chat"])
```

### 2. Router Logic (`routers.py`)

```python
def route_critic(state: AgentState) -> Literal["sufficient", "insufficient"]:
    """Decide si el artefacto es suficiente para generar XML."""
    if state["is_sufficient"]:
        return "sufficient"
    return "insufficient"
```

### 3. Main CLI (`main.py`)

Implementar un bucle interactivo que:
1. Pida input inicial al usuario
2. Ejecute el grafo hasta interrupción (chat) o fin
3. Si es interrupción (chat), muestre la pregunta y pida respuesta
4. Si es fin (generator), guarde el XML y termine

---

## Orden de Implementación

1. **routers.py**: Lógica de decisión simple
2. **workflow.py**: Construcción del grafo
3. **main.py**: Interfaz de usuario
4. Tests de integración

---

## Verificación

```bash
pytest tests/integration/test_workflow.py -v
python src/bpmn_generator/main.py  # Prueba manual
```

**Criterios de Aceptación**:
- [ ] El grafo compila sin errores
- [ ] El flujo transita correctamente: Analyst -> Critic -> [Generator | Chat]
- [ ] Se interrumpe antes de Chat para input de usuario (simulado en tests)
- [ ] Persistencia funciona (state checkpointing)
