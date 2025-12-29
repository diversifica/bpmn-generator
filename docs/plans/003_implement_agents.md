# Plan: Implementar Agentes LLM

**Issue**: #4  
**Status**: Draft  
**Assignee**: AI Agent  
**Branch**: `feature/4-implement-agents`

## Análisis de Impacto

### Archivos a crear
- `src/bpmn_generator/agents/analyst.py` - analyzer_node
- `src/bpmn_generator/agents/critic.py` - critic_node
- `src/bpmn_generator/agents/chat.py` - chat_node
- `src/bpmn_generator/agents/generator.py` - xml_generator_node
- `tests/unit/agents/test_analyst.py`
- `tests/unit/agents/test_critic.py`
- `tests/unit/agents/test_chat.py`
- `tests/unit/agents/test_generator.py`

### Nuevas dependencias
- Ninguna (ya están en pyproject.toml)

### Breaking changes
- Ninguno

---

## Diseño Propuesto

### 1. Analyst Node (`analyst.py`)

```python
def analyzer_node(state: AgentState) -> dict:
    """Analiza conversación y propone cambios al ProcessArtifact."""
    # 1. Cargar prompt con reglas ISO 19510
    # 2. Inyectar artifact JSON actual
    # 3. Invocar LLM con structured output (ProcessUpdate)
    # 4. Retornar last_update
```

### 2. Critic Node (`critic.py`)

```python
def critic_node(state: AgentState) -> dict:
    """Valida suficiencia del artefacto."""
    # 1. Verificar criterios algorítmicos (Doc 00)
    # 2. Identificar missing_info
    # 3. Retornar is_sufficient, missing_info
```

### 3. Chat Node (`chat.py`)

```python
def chat_node(state: AgentState) -> dict:
    """Interactúa con usuario para clarificaciones."""
    # 1. Generar ClarificationQuestion
    # 2. Esperar respuesta (interrupt)
    # 3. Retornar messages actualizados
```

### 4. Generator Node (`generator.py`)

```python
def xml_generator_node(state: AgentState) -> dict:
    """Genera XML BPMN 2.0 determinista."""
    # 1. Calcular posiciones con layout.py
    # 2. Generar XML con lxml
    # 3. Validar con bpmn_validator.py
    # 4. Retornar XML string
```

---

## Orden de Implementación

1. **analyst.py**: Core del sistema
2. **critic.py**: Validación de suficiencia
3. **chat.py**: Interacción con usuario
4. **generator.py**: Generación XML determinista
5. Tests unitarios

---

## Verificación

```bash
pytest tests/unit/agents/ -v --cov=src/bpmn_generator/agents
```

**Criterios de Aceptación**:
- [ ] analyzer_node retorna ProcessUpdate válido
- [ ] critic_node identifica missing_info correctamente
- [ ] chat_node genera ClarificationQuestion
- [ ] xml_generator_node produce XML válido
- [ ] Tests pasan con 80%+ coverage
- [ ] Mypy y Ruff sin errores

**Referencia**: Doc 03 Sección 2, Doc 04
