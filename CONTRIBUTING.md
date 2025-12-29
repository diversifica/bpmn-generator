# Contributing Guide - BPMN Generator

## 🎯 Filosofía del Proyecto

Este proyecto está diseñado para ser **desarrollado y mantenido por agentes de IA** (LLMs) bajo supervisión humana. Por ello, la metodología prioriza:

1. **Determinismo**: Pasos claros y verificables
2. **Trazabilidad**: Cada cambio documentado y justificado
3. **Modularidad**: Componentes independientes y testeables
4. **Validación Automática**: CI/CD que no permite regresiones

---

## 📋 Workflow Obligatorio

### Git Flow Strategy

Este proyecto usa **Git Flow** con dos ramas principales:

- **`main`**: Código en producción (solo releases)
- **`develop`**: Rama de desarrollo activa (base para features)

**Regla de oro**: NUNCA commitear directamente en `main` ni `develop`.

---

### 1. Planificación (PLANNING Mode)

**NUNCA** empieces a codificar sin un plan aprobado.

#### 1.1 Crear Issue
```markdown
**Tipo**: feature | bug | chore | docs

**Contexto**:
- ¿Qué problema resuelve?
- ¿Por qué es necesario ahora?

**Criterios de Aceptación** (Checklist):
- [ ] Criterio 1 medible y verificable
- [ ] Criterio 2 medible y verificable
- [ ] Tests pasan
- [ ] Documentación actualizada

**Impacto si NO se hace**:
- Consecuencia 1
- Consecuencia 2
```

#### 1.2 Crear Implementation Plan
Antes de tocar código, crea `docs/plans/ISSUE_NUMBER_description.md`:

```markdown
# Plan: [Título del Issue]

## Análisis de Impacto
- **Archivos a modificar**: lista completa
- **Nuevas dependencias**: si aplica
- **Breaking changes**: si aplica

## Diseño Propuesto
### Cambios en Modelos (src/bpmn_generator/models/)
- Archivo X: Añadir campo Y con validador Z

### Cambios en Agentes (src/bpmn_generator/agents/)
- Archivo A: Modificar prompt para incluir regla B

### Cambios en Tests
- test_X.py: Añadir caso para validar Y

## Orden de Implementación
1. Paso 1 (archivo, función, razón)
2. Paso 2 (archivo, función, razón)
3. ...

## Verificación
- [ ] Comando para verificar: `pytest tests/test_X.py`
- [ ] Output esperado: "X tests passed"
```

**Aprobación**: El plan debe ser revisado y aprobado antes de proceder.

---

### 2. Implementación (EXECUTION Mode)

#### 2.1 Crear Rama desde `develop`
```bash
# 1. Asegurarse de estar en develop actualizado
git checkout develop
git pull origin develop

# 2. Crear rama de feature/bug/chore
git checkout -b tipo/numero-descripcion-corta

# Ejemplos:
git checkout -b feature/23-add-subprocess-support
git checkout -b bug/45-fix-gateway-validation
git checkout -b chore/12-refactor-prompt-loading
```

**Nomenclatura de ramas**:
- `feature/ISSUE-descripcion` - Nueva funcionalidad
- `bug/ISSUE-descripcion` - Corrección de error
- `chore/ISSUE-descripcion` - Mantenimiento, refactor
- `docs/ISSUE-descripcion` - Solo documentación

#### 2.2 Commits Atómicos
**Formato obligatorio**:
```
tipo(#issue): descripción imperativa en español

- Detalle 1
- Detalle 2

Refs: #issue_number
```

**Ejemplos**:
```
feature(#23): añade soporte para SubProcess con loop_characteristics

- Extiende SubProcessNode con campo loop_characteristics
- Actualiza validator para verificar is_collection en DataObjects
- Añade tests para bucles secuenciales y paralelos

Refs: #23
```

```
bug(#45): corrige validación de default_flow en ExclusiveGateway

- Añade check en ProcessArtifact.validate_graph_integrity()
- Verifica que default_flow apunte a edge existente
- Añade test de regresión

Refs: #45
```

#### 2.3 Reglas de Código

**Python Style**:
- **PEP 8** estricto (verificado por `ruff`)
- **Type hints** obligatorios en todas las funciones
- **Docstrings** en formato Google para clases y funciones públicas

```python
def analyze_process(description: str, current_artifact: ProcessArtifact) -> ProcessUpdate:
    """Analiza descripción de proceso y genera actualización estructurada.
    
    Args:
        description: Texto en lenguaje natural del usuario.
        current_artifact: Estado actual del proceso.
        
    Returns:
        ProcessUpdate con nodos/edges a añadir.
        
    Raises:
        ValidationError: Si la descripción está vacía.
    """
    ...
```

**Imports**:
```python
# Standard library
import json
from typing import Optional, List

# Third party
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage

# Local
from bpmn_generator.models.schema import BPMNNode, ProcessArtifact
```

**Logging** (NO `print()`):
```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"Processing artifact with {len(nodes)} nodes")
logger.warning(f"Missing role in task {task_id}, defaulting to None")
logger.error(f"Validation failed: {error}", exc_info=True)
```

#### 2.4 Tests Obligatorios

**Cobertura mínima**: 80% (verificado por CI)

**Estructura**:
```python
# tests/unit/models/test_schema.py
import pytest
from bpmn_generator.models.schema import ProcessArtifact, UserTaskNode

def test_process_artifact_validates_edge_references():
    """Verifica que edges con source_id inválido generen error."""
    artifact = ProcessArtifact(
        process_id="test",
        process_name="Test",
        nodes=[UserTaskNode(id="task1", label="Tarea 1")],
        edges=[{"source_id": "invalid", "target_id": "task1"}]
    )
    
    assert not artifact.is_valid
    assert "non-existent source node" in artifact.validation_errors[0]
```

**Casos de test requeridos**:
- ✅ Happy path (caso exitoso)
- ✅ Edge cases (límites, valores nulos)
- ✅ Error cases (validaciones, excepciones)

---

### 3. Verificación (VERIFICATION Mode)

#### 3.1 Pre-commit Checks (Automático)
```bash
# Ejecutado automáticamente por pre-commit hooks
ruff check src/ tests/           # Linting
ruff format --check src/ tests/  # Formatting
mypy src/                        # Type checking
pytest tests/ --cov=src --cov-report=term-missing  # Tests + coverage
```

#### 3.2 Manual Testing
Antes de abrir PR, ejecuta el sistema end-to-end:

```python
# tests/manual/test_e2e.py
from bpmn_generator import BPMNGenerator

generator = BPMNGenerator()
result = generator.generate("El usuario envía un formulario...")

# Verificar manualmente en Camunda Modeler
with open("output_test.bpmn", "w") as f:
    f.write(result)
```

---

### 4. Pull Request

#### 4.1 Preparar PR
```bash
# Asegurarse de que develop está actualizado
git checkout develop
git pull origin develop

# Rebase tu rama sobre develop
git checkout feature/23-add-subprocess-support
git rebase develop

# Push de tu rama
git push origin feature/23-add-subprocess-support
```

#### 4.2 Abrir PR hacia `develop`
**Base branch**: `develop` (NO `main`)

#### 4.3 Checklist Obligatorio
```markdown
## Descripción
Breve resumen del cambio (1-2 líneas).

## Issue
Closes #NUMERO

## Cambios Realizados
- Cambio 1
- Cambio 2

## Tipo de Cambio
- [ ] Bug fix (non-breaking)
- [ ] New feature (non-breaking)
- [ ] Breaking change
- [ ] Documentation update

## Testing
### Tests Automatizados
- [ ] Tests unitarios pasan (`pytest tests/unit/`)
- [ ] Tests de integración pasan (`pytest tests/integration/`)
- [ ] Cobertura >= 80%

### Tests Manuales
**Pasos para reproducir**:
1. Ejecutar `python -m bpmn_generator.cli "descripción del proceso"`
2. Abrir `output.bpmn` en Camunda Modeler
3. Verificar que [comportamiento esperado]

**Resultado esperado**: [descripción]
**Resultado obtenido**: [captura o descripción]

## Checklist Final
- [ ] Código sigue PEP 8 (ruff check pasa)
- [ ] Type hints completos (mypy pasa)
- [ ] Docstrings en funciones públicas
- [ ] Tests añadidos/actualizados
- [ ] Documentación actualizada (si aplica)
- [ ] CHANGELOG.md actualizado
- [ ] No hay `print()` en código final
- [ ] No hay TODOs sin issue asociado
- [ ] Rama actualizada con `develop` (rebase)
```

#### 4.4 Revisión de Código

**Criterios de aprobación**:
- ✅ CI en verde (todos los checks pasan)
- ✅ Cobertura de tests >= 80%
- ✅ Al menos 1 aprobación humana
- ✅ No conflictos con `develop`
- ✅ Rebase sobre `develop` actualizado

**Criterios de rechazo automático**:
- ❌ Tests fallan
- ❌ Cobertura < 80%
- ❌ Ruff/mypy con errores
- ❌ Commits sin formato correcto
- ❌ Sin tests para nuevo código
- ❌ PR hacia `main` (debe ser hacia `develop`)

#### 4.5 Merge
Una vez aprobado:
```bash
# Squash merge hacia develop
git checkout develop
git merge --squash feature/23-add-subprocess-support
git commit -m "feature(#23): add subprocess support with loop characteristics"
git push origin develop
```

---

## 🏗️ Arquitectura y Convenciones

### Estructura de Directorios
```
src/bpmn_generator/
├── __init__.py              # API pública
├── models/
│   ├── __init__.py
│   ├── schema.py            # Pydantic models (BPMNNode, ProcessArtifact)
│   └── state.py             # AgentState, ProcessUpdate
├── agents/
│   ├── __init__.py
│   ├── analyst.py           # analyzer_node
│   ├── critic.py            # critic_node
│   ├── chat.py              # chat_node
│   └── generator.py         # xml_generator_node
├── graph/
│   ├── __init__.py
│   ├── workflow.py          # StateGraph definition
│   └── routers.py           # Conditional edge functions
└── utils/
    ├── __init__.py
    ├── bpmn_validator.py    # XSD validation
    ├── layout.py            # Manhattan Grid algorithm
    └── prompts.py           # Prompt loading/templating
```

### Naming Conventions

**Archivos**: `snake_case.py`
**Clases**: `PascalCase`
**Funciones/Variables**: `snake_case`
**Constantes**: `UPPER_SNAKE_CASE`

**Nodos del grafo**: `{role}_node` (ej: `analyst_node`, `critic_node`)
**Routers**: `{context}_router` (ej: `after_update_router`)

### Dependencias

**Añadir nueva dependencia**:
1. Añadir a `pyproject.toml` en la sección apropiada
2. Documentar en `docs/architecture/dependencies.md` (crear si no existe)
3. Justificar en el PR por qué es necesaria

**Dependencias core** (no cambiar sin aprobación):
- `langgraph >= 0.2.0`
- `langchain-core >= 0.3.0`
- `pydantic >= 2.0.0`
- `lxml >= 5.0.0` (validación XSD)

---

## 🔍 Debugging y Troubleshooting

### Logs Estructurados
```python
logger.info(
    "Artifact updated",
    extra={
        "process_id": artifact.process_id,
        "nodes_count": len(artifact.nodes),
        "edges_count": len(artifact.edges),
        "is_valid": artifact.is_valid
    }
)
```

### Debugging LangGraph
```python
# Habilitar debug mode
from langgraph.graph import StateGraph

graph = StateGraph(AgentState)
# ... definir nodos ...
compiled = graph.compile(debug=True)  # Logs detallados
```

### Inspeccionar Checkpoints
```python
from langgraph.checkpoint.sqlite import SqliteSaver

memory = SqliteSaver.from_conn_string("checkpoints.db")
states = memory.list(thread_id="session_123")

for state in states:
    print(f"Step {state.step}: {state.values['current_phase']}")
```

---

## 🚀 Release Process

### Versionado (Semantic Versioning)
- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.1.0): New features (backward compatible)
- **PATCH** (0.0.1): Bug fixes

### Checklist de Release
1. [ ] Actualizar `__version__` en `src/bpmn_generator/__init__.py`
2. [ ] Actualizar `CHANGELOG.md` con cambios desde última versión
3. [ ] Crear tag: `git tag -a v0.1.0 -m "Release 0.1.0"`
4. [ ] Push tag: `git push origin v0.1.0`
5. [ ] GitHub Actions automáticamente publica a PyPI

---

## 📚 Recursos

- **Documentación Técnica**: `docs/architecture/`
- **ISO 19510 Reference**: `docs/references/ISO_IEC_19510-2013.pdf`
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **Pydantic Docs**: https://docs.pydantic.dev/

---

## ❓ FAQ para Agentes

### ¿Cómo añado un nuevo tipo de nodo BPMN?
1. Añadir clase Pydantic en `src/bpmn_generator/models/schema.py`
2. Añadir al `Union` de `BPMNNode`
3. Actualizar `ProcessUpdate` schema
4. Añadir regla en prompt del analista (`prompts/base/analyst_rules.txt`)
5. Actualizar generador XML (`src/bpmn_generator/agents/generator.py`)
6. Añadir tests en `tests/unit/models/test_schema.py`

### ¿Cómo modifico un prompt?
1. **NO hardcodear** en código Python
2. Editar archivo en `prompts/base/`
3. Usar `load_prompt()` de `utils/prompts.py`
4. Añadir test de regresión verificando output del LLM

### ¿Cómo debuggeo un fallo en el grafo?
1. Habilitar `debug=True` en `graph.compile()`
2. Revisar logs en `logs/langgraph.log`
3. Inspeccionar checkpoints en SQLite
4. Añadir test de regresión

### ¿Cuándo usar RAG vs reglas embebidas?
- **Reglas embebidas**: Conocimiento core que SIEMPRE se necesita (actual)
- **RAG**: Consultas esporádicas a documentación extensa (futuro, ver Doc 03 Sección 7)

---

## 🤝 Código de Conducta

- **Respeto**: Comentarios constructivos en code reviews
- **Transparencia**: Documentar decisiones de diseño
- **Calidad**: No comprometer tests ni cobertura
- **Colaboración**: Pedir ayuda si estás bloqueado >2 horas

---

**Última actualización**: 2025-12-29  
**Versión**: 1.0.0