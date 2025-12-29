# Plan: Implementar Funciones de Utilidad

**Issue**: #2  
**Status**: Draft  
**Assignee**: AI Agent  
**Branch**: `feature/2-implement-utilities`

## Análisis de Impacto

### Archivos a crear
- `src/bpmn_generator/utils/prompts.py` - Carga de prompts
- `src/bpmn_generator/utils/layout.py` - Manhattan Grid DI
- `src/bpmn_generator/utils/bpmn_validator.py` - Validación XSD
- `prompts/base/analyst_rules.txt` - Reglas ISO 19510
- `tests/unit/utils/test_prompts.py`
- `tests/unit/utils/test_layout.py`
- `tests/unit/utils/test_bpmn_validator.py`

### Nuevas dependencias
- `lxml` (ya en pyproject.toml)

### Breaking changes
- Ninguno

---

## Diseño Propuesto

### 1. Prompts (`prompts.py`)

```python
def load_prompt(prompt_name: str, base_dir: str = "prompts/base") -> str:
    """Load prompt from file."""
    
def inject_artifact_json(prompt: str, artifact: ProcessArtifact) -> str:
    """Inject artifact JSON into prompt template."""
```

### 2. Layout (`layout.py`)

```python
# Constantes
GRID_START_X = 200
GRID_START_Y = 200
HORIZONTAL_STEP = 180
VERTICAL_BRANCH_OFFSET = 150

def calculate_node_positions(artifact: ProcessArtifact) -> dict[str, tuple[int, int]]:
    """Calculate DI coordinates for all nodes using Manhattan Grid."""
    
def calculate_waypoints(source_pos, target_pos) -> list[tuple[int, int]]:
    """Calculate orthogonal waypoints between two nodes."""
```

### 3. Validator (`bpmn_validator.py`)

```python
def validate_bpmn_xml(xml_string: str) -> tuple[bool, list[str]]:
    """Validate BPMN XML against XSD schema."""
```

---

## Orden de Implementación

1. **prompts.py**: Carga de archivos de texto
2. **prompts/base/analyst_rules.txt**: Extraer reglas de Doc 04
3. **layout.py**: Manhattan Grid algorithm
4. **bpmn_validator.py**: XSD validation (básico)
5. Tests unitarios

---

## Verificación

```bash
pytest tests/unit/utils/ -v --cov=src/bpmn_generator/utils
```

**Criterios de Aceptación**:
- [ ] load_prompt() carga archivos correctamente
- [ ] Manhattan Grid genera coordenadas válidas
- [ ] Waypoints son ortogonales (90°)
- [ ] Tests pasan con 80%+ coverage
- [ ] Mypy y Ruff sin errores

**Referencia**: Doc 03 Sección 2.5.1, Doc 04 Sección 3
