# Documento 0
## Documento de Inicio y Marco de Requisitos del Proyecto

### Sistema Automatizado para la Clarificación, Formalización y Modelado de Procesos conforme a BPMN

---

## Control del documento

- **Versión:** 1.3 (Definitiva)
- **Estado:** Aprobado – Línea base del proyecto
- **Tipo:** Documento de inicio / Marco de referencia
- **Dependencias:** Ninguna
- **Documentos derivados:**
  - 01_Requisitos_Funcionales_y_No_Funcionales.md
  - Documentos de diseño (Arquitectura LangGraph / Modelos de Datos)
  - Especificación de Prompts y Orquestación

---

## 1. Propósito del documento

El presente documento establece el marco conceptual, metodológico y de referencia del proyecto de software orientado a la clarificación, definición y modelado de procesos de negocio conforme al estándar BPMN 2.0, utilizando modelos de lenguaje (LLMs) como motor de razonamiento y LangGraph como orquestador de estado.

Su propósito es definir:
- El alcance conceptual del sistema.
- Los principios rectores y límites del análisis.
- El rol del sistema como asistente experto.
- La estructura de datos fundamental que sustenta el modelado.

Este documento define el **qué** y el **para qué**. No incluye detalles de implementación de bajo nivel, salvo aquellos estructurales necesarios para la arquitectura (como el formato del artefacto).

---

## 2. Contexto y motivación

### 2.1 Situación de partida
En entornos reales, la definición de procesos presenta habitualmente:
- Descripciones informales, incompletas o ambiguas.
- Conocimiento implícito no documentado ("tribal knowledge").
- Variabilidad operativa según la persona que ejecuta el proceso.
- Dificultad para traducir la realidad operativa a la rigidez formal del BPMN.

El uso directo de LLMs para generar código BPMN (XML) sin una metodología intermedia introduce alucinaciones, errores de sintaxis y falta de trazabilidad.

### 2.2 Necesidad identificada
Se requiere un sistema que:
- **Clarifique** antes de modelar, actuando como un analista experto.
- **Mantenga el contexto** (memoria) a largo plazo durante la entrevista.
- **Estructure** la información en un formato intermedio agnóstico.
- **Formalice** el resultado en un BPMN 2.0 válido y trazable.

---

## 3. Objetivo general del proyecto

Diseñar y construir un sistema de software basado en agentes que permita la clarificación guiada, definición estructurada y posterior modelado de procesos de negocio, garantizando calidad técnica (BPMN válido), coherencia lógica y una experiencia de usuario que reduzca la carga cognitiva.

---

## 4. Marco metodológico y límites

### 4.1 BPMN como marco de referencia y límite del modelado
El estándar BPMN constituye el marco formal para el **modelado** del proceso.

Durante la fase de clarificación, el sistema puede analizar elementos del dominio de negocio (reglas, roles, datos, excepciones) **en la medida necesaria** para:
- Interpretar correctamente el flujo.
- Identificar compuertas (gateways) y condiciones.
- Detectar eventos de inicio, fin y error.

**Límite:** El sistema no realiza consultoría estratégica, financiera ni de optimización de negocio fuera de la lógica del flujo del proceso.

### 4.2 Rol del análisis de procesos
El sistema actúa como un **Analista de Procesos Junior/Mid** supervisado por el usuario:
- Interpreta descripciones ambiguas.
- Detecta "happy paths" vs. flujos de excepción.
- Propone estructuras estándar para resolver situaciones complejas.

---

## 5. Entrada del sistema

- **Input:** Descripción textual del proceso en lenguaje natural (voz o texto).
- **Presunciones:**
  - El usuario conoce su negocio, pero no necesariamente BPMN.
  - La descripción inicial estará incompleta y contendrá ambigüedades.
  - Existen reglas implícitas que deben ser descubiertas.

---

## 6. Fase de clarificación del proceso

### 6.1 Naturaleza de la fase
La clarificación es un bucle interactivo obligatorio. Su objetivo es transformar una descripción informal en una definición estructurada. Es un proceso de **descubrimiento**, no de corrección punitiva.

### 6.2 Estrategia de interacción
El sistema reduce la carga cognitiva mediante:
- Preguntas cerradas o de opción múltiple siempre que sea posible.
- Propuestas de escenarios ("¿Te refieres a A o a B?").
- Uso de lenguaje natural, evitando jerga técnica BPMN en el diálogo (salvo que el usuario la pida).

### 6.3 Clasificación de recomendaciones
Las intervenciones del sistema se clasifican explícitamente:

* **Tipo A: Correcciones de Integridad (Obligatorias):** Necesarias para que el BPMN sea válido (ej. "Todo proceso debe tener un fin", "Esta decisión necesita caminos de salida").
* **Tipo B: Mejoras de Claridad (Sugeridas):** Simplificación de redacción o agrupación de tareas. El usuario puede rechazarlas.
* **Tipo C: Optimizaciones de Flujo (Opcionales):** Cambios en la lógica del negocio para eficiencia. Requieren aprobación explícita y justificada.

### 6.4 Criterio de suficiencia mínima
La clarificación finaliza cuando se cumplen los siguientes criterios (Criterio de Parada):
1.  **Estructural:** Existe al menos un Evento de Inicio y un Evento de Fin alcanzable.
2.  **Continuidad:** Todos los nodos están conectados; no hay "islas" ni caminos muertos.
3.  **Decisión:** Cada Gateway tiene una lógica de decisión clara y salidas definidas.
4.  **Responsabilidad:** Cada tarea tiene un actor/rol asignado (o inferido por defecto).

El sistema no busca la perfección exhaustiva, sino la **consistencia lógica** suficiente para generar un modelo válido.

#### 6.4.1 Implementación Algorítmica de los Criterios

**Criterio 1 - Estructural (Verificación Programática):**
```python
def check_structural(artifact: ProcessArtifact) -> tuple[bool, list[str]]:
    """Verifica que exista al menos un StartEvent y un EndEvent."""
    errors = []
    has_start = any(node.type == "StartEvent" for node in artifact.nodes)
    has_end = any(node.type == "EndEvent" for node in artifact.nodes)
    
    if not has_start:
        errors.append("Falta un Evento de Inicio")
    if not has_end:
        errors.append("Falta un Evento de Fin")
    
    return (len(errors) == 0, errors)
```

**Criterio 2 - Continuidad (Algoritmo de Conectividad de Grafo):**
```python
def check_continuity(artifact: ProcessArtifact) -> tuple[bool, list[str]]:
    """Verifica que todos los nodos sean alcanzables desde el inicio."""
    from collections import deque
    
    # Encontrar nodo de inicio
    start_nodes = [n.id for n in artifact.nodes if n.type == "StartEvent"]
    if not start_nodes:
        return (False, ["No hay nodo de inicio para verificar conectividad"])
    
    # BFS desde el inicio
    visited = set()
    queue = deque(start_nodes)
    
    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        
        # Encontrar nodos conectados
        for edge in artifact.edges:
            if edge.source_id == current and edge.target_id not in visited:
                queue.append(edge.target_id)
    
    # Verificar nodos no visitados
    all_node_ids = {n.id for n in artifact.nodes}
    unreachable = all_node_ids - visited
    
    if unreachable:
        return (False, [f"Nodos no conectados: {', '.join(unreachable)}"])
    return (True, [])
```

**Criterio 3 - Decisión (Validación de Gateways):**
```python
def check_gateways(artifact: ProcessArtifact) -> tuple[bool, list[str]]:
    """Verifica que cada Gateway tenga al menos 2 salidas con condiciones."""
    errors = []
    gateway_ids = {n.id for n in artifact.nodes if n.type == "Gateway"}
    
    for gw_id in gateway_ids:
        outgoing = [e for e in artifact.edges if e.source_id == gw_id]
        if len(outgoing) < 2:
            errors.append(f"Gateway '{gw_id}' tiene menos de 2 salidas")
        elif any(e.condition is None for e in outgoing):
            errors.append(f"Gateway '{gw_id}' tiene salidas sin condición definida")
    
    return (len(errors) == 0, errors)
```

**Criterio 4 - Responsabilidad (Validación de Roles):**
```python
def check_roles(artifact: ProcessArtifact) -> tuple[bool, list[str]]:
    """Verifica que las tareas tengan roles asignados."""
    warnings = []  # No es error crítico, solo advertencia
    
    for node in artifact.nodes:
        if node.type == "Task" and (node.role is None or node.role == "UNKNOWN"):
            warnings.append(f"Tarea '{node.label}' sin rol asignado")
    
    # Permitir hasta 2 tareas sin rol (tolerancia)
    return (len(warnings) <= 2, warnings)
```

Estos algoritmos son ejecutados por el `critic_node` para actualizar los campos `is_sufficient` y `missing_info` en el estado.

---

## 7. Registro de decisiones
Cada aclaración relevante se almacena como una "Decisión Estructural" vinculada a los nodos afectados. Esto garantiza que si el BPMN muestra una ruta específica, el sistema puede explicar *por qué* existe esa ruta basándose en una respuesta del usuario.

---

## 8. Artefacto inicial (Estructura de Datos)

### 8.1 Definición y Propósito
El corazón del sistema no es el XML final, sino un **Artefacto Intermedio Estructurado**. Es una estructura de datos (JSON/Objeto) que representa la lógica del proceso de forma agnóstica a la representación gráfica.

### 8.2 Estructura del Artefacto (Esquema conceptual)
El artefacto debe contener, como mínimo:
- **Metadatos:** ID, Nombre, Descripción.
- **Nodos:** Lista de actividades, eventos y compuertas con sus atributos (Roles, Tipos).
- **Transiciones:** Conexiones lógicas (Origen -> Destino).
- **Registro de Decisiones:** Historial de por qué se creó cada elemento.

*Ejemplo completo (alineado con Doc 02):*
```json
{
  "process_id": "proc_001",
  "process_name": "Validación de Facturas",
  "description": "Proceso de validación y pago de facturas",
  "nodes": [
    {"id": "start_1", "type": "StartEvent", "label": "Inicio"},
    {"id": "t1", "type": "Task", "label": "Validar factura", "role": "Contable"},
    {"id": "end_1", "type": "EndEvent", "label": "Fin"}
  ],
  "edges": [
    {"source_id": "start_1", "target_id": "t1", "condition": null},
    {"source_id": "t1", "target_id": "end_1", "condition": null}
  ],
  "decision_log": [
    {
      "decision_id": "d1",
      "question_asked": "¿Quién realiza la validación de facturas?",
      "user_answer": "El contable revisa la fecha y el importe",
      "impacted_elements": ["t1"]
    }
  ],
  "validation_status": {
    "is_valid": true,
    "validation_errors": []
  }
}
```

### 8.3 Vistas del Artefacto
- Vista Técnica: Para el generador de BPMN (mapeo directo a XML).
- Vista de Usuario: Resumen narrativo ("Primero el Contable valida la factura...") para validación final.

### 9. Generación y Validación BPMN
#### 9.1 Generación Determinista
El BPMN XML se genera mediante reglas deterministas aplicadas sobre el Artefacto Estructurado. Se minimiza el uso de LLM en la escritura directa de XML para evitar errores de sintaxis.

#### 9.2 Niveles de Validación
El sistema aplica tres capas de validación antes de entregar el resultado:
- Sintáctica: El XML cumple con el esquema XSD de BPMN 2.0.
- Estructural: El grafo es válido (sin bucles infinitos no controlados, sin nodos desconectados).
- Semántica (Asistida): Coherencia de los verbos y lógica de negocio (revisada por LLM).

### 10. Iteración y Control
#### 10.1 Tipos de Iteración
- Iteración de Clarificación: Conversación fluida para construir el artefacto.
- Iteración de Corrección Técnica: El sistema intenta auto-corregir errores de sintaxis XML (invisible al usuario, limitado a 3 intentos).
- Iteración de Refinamiento: El usuario solicita cambios sobre el modelo generado ("Cambia esta tarea", "Añade una opción").

#### 10.2 Garantías
Ninguna iteración modifica estados aprobados sin traza. Se evitan bucles infinitos mediante contadores de intentos en los nodos del grafo del sistema.

### 11. Persistencia y Estado (Arquitectura)
- El sistema utiliza un modelo de persistencia robusto (Checkpointers):
- El estado de la conversación y el artefacto se guardan en cada paso.
- El usuario puede pausar y retomar sesiones días después.
- Permite "viajar en el tiempo" (deshacer decisiones) recuperando estados anteriores del grafo.

### 12. Trazabilidad
- Se mantiene una cadena de custodia de la información: Input Usuario -> Diálogo de Clarificación -> Decisión Registrada -> Nodo en Artefacto -> Elemento BPMN XML.
- Cualquier elemento del diagrama final puede rastrearse hasta su origen en la conversación.

### 13. Salidas del Sistema
El sistema entrega los siguientes productos:
- BPMN 2.0 XML (.bpmn): Archivo estándar importable en Camunda, Bizagi, etc.
- Imagen del Diagrama (.svg/.png): Para visualización rápida y documentación.
- Resumen del Proceso (.md/.pdf): Narrativa textual del flujo y reglas.
- Artefacto JSON (Opcional): Para integraciones o depuración.

### 14. Exclusiones del alcance
- Desarrollo de un editor gráfico "drag-and-drop" (se asume uso de herramientas externas para edición visual fina).
- Ejecución del proceso (Workflow Engine).
- Integración con APIs de terceros en tiempo real durante la entrevista.

### 15. Principios Rectores Técnicos
- Separación de Responsabilidades: El Agente de Entrevista no genera XML; el Generador de XML no toma decisiones de negocio.
- Gestión de Contexto: Se implementan estrategias para resumir y podar el historial del chat, evitando desbordar la ventana de contexto del LLM.
- Fail-Safe: Si el sistema no puede modelar algo, lo marca como "Tarea Genérica" o "Anotación" para revisión manual, nunca inventa.

### 16. Cierre del documento
- Este documento define la arquitectura lógica y funcional del proyecto. Cualquier requisito técnico detallado en fases posteriores debe alinearse con estos principios.

### 17. Próximo paso
Elaboración del documento: 01_Requisitos_Funcionales_y_No_Funcionales.md