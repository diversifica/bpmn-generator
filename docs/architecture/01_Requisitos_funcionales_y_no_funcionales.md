# Documento 01
Especificación de Requisitos Funcionales y No Funcionales
Sistema Automatizado para la Clarificación y Modelado BPMN
Control del documento
- **Versión**: 1.0
- **Estado**: Borrador inicial para aprobación
- **Tipo**: Especificación de Requisitos de Software (SRS)
- **Documento Fuente**: Documento 0 (Marco de Inicio v1.3)
- **Dependencias**:
    - Arquitectura: LangGraph
    - Motor: LLMs (Modelos de Lenguaje)

## 1. Introducción y Alcance
Este documento define los comportamientos obligatorios (funcionales) y los atributos de calidad (no funcionales) del sistema.

El sistema se define como una máquina de estados basada en grafos (LangGraph) que orquesta la interacción entre un usuario humano y múltiples agentes especializados (Analista, Validador, Generador) para producir un archivo BPMN válido.

## 2. Requisitos Funcionales (FR)
### 2.1 Módulo de Interacción y Clarificación (Agente Analista)
Este módulo gestiona la conversación y la extracción de información.

- FR-01 Captura de Intención: El sistema debe aceptar entradas en lenguaje natural (texto) que describan procesos de negocio, sin importar su nivel de estructuración inicial.

- FR-02 Detección de Ambigüedad: El sistema debe identificar activamente:
    - Pasos faltantes entre actividades.
    - Sujetos (roles) no definidos.
    - Condiciones de decisión (gateways) vagas (ej: "si todo va bien").

- FR-03 Estrategia de Interrogación:
    - El sistema priorizará preguntas cerradas (Sí/No) o de selección múltiple.
    - El sistema no debe formular más de 3 preguntas en un solo turno de conversación.

- FR-04 Gestión de Recomendaciones: El sistema debe etiquetar sus sugerencias según la clasificación del Doc 0 (Corrección, Mejora, Optimización) y respetar la decisión final del usuario.

- FR-05 Criterio de Parada (Suficiencia): El sistema debe evaluar internamente tras cada interacción si el Artefacto Inicial cumple los criterios de suficiencia mínima (Inicio, Fin, Continuidad, Responsabilidad). Si se cumplen, debe proponer pasar a la generación.

### 2.2 Módulo de Gestión del Artefacto (Estado del Grafo)
Este es el núcleo lógico que mantiene la "verdad" del proceso.

- FR-06 Creación del Artefacto Estructurado: El sistema debe mantener una estructura de datos JSON (el Artefacto) separada del historial del chat.

- FR-07 Actualización Incremental: Cada respuesta del usuario que aporte información nueva debe actualizar el Artefacto inmediatamente (añadir nodo, definir rol, concretar condición).

- FR-08 Registro de Decisiones: El sistema debe almacenar un log de "Decisiones Estructurales" vinculado a los elementos del artefacto (ej: "Gateway G1 creado porque el usuario indicó validación manual").

- FR-09 Versionado en Memoria: El sistema debe permitir deshacer el último cambio en el artefacto si el usuario rectifica una respuesta anterior.

### 2.3 Módulo de Generación y Validación (Agente Ingeniero)
Este módulo traduce el JSON a XML y asegura la calidad.

- FR-10 Generación Determinista: La transformación de Artefacto JSON a BPMN XML debe realizarse mediante reglas de mapeo fijas, minimizando la intervención creativa del LLM para evitar alucinaciones sintácticas.

- FR-11 Validación Sintáctica: El sistema debe validar el XML resultante contra el esquema XSD oficial de BPMN 2.0.

- FR-12 Validación Estructural (Grafo): El sistema debe verificar matemáticamente:

    - Que no existen nodos sin conexión (islas).
    - Que no existen bucles infinitos sin condición de salida.
    - Que todos los flujos desembocan en un evento de Fin.

- FR-13 Auto-corrección Técnica: Si la generación XML falla la validación sintáctica, el sistema debe intentar corregir el error automáticamente hasta 3 veces antes de reportar error al usuario.

### 2.4 Salidas y Exportación
- FR-14 Formatos de Exportación: El sistema debe permitir descargar:

    - Archivo .bpmn (XML estándar).
    - Imagen .svg (Visualización).
    - Archivo .json (El Artefacto intermedio).

- FR-15 Detección de Confirmación del Usuario: El sistema debe detectar cuando el usuario aprueba proceder a la generación (ej: "sí, genera", "adelante", "ok") y actualizar el flag `user_approved` en el estado.

- FR-16 Soporte para Deshacer Cambios: El sistema debe permitir al usuario deshacer la última modificación al artefacto mediante el mecanismo de checkpoints de LangGraph (`get_state_history()`).

- FR-17 Soporte Multi-Gateway: El sistema debe soportar los tres tipos principales de Gateways BPMN:
    - **Exclusive (XOR)**: Solo un camino se activa.
    - **Parallel (AND)**: Todos los caminos se activan simultáneamente.
    - **Inclusive (OR)**: Uno o más caminos se activan según condiciones.

## 3. Requisitos No Funcionales (NFR)
### 3.1 Persistencia y Estado (LangGraph Checkpointing)
- NFR-01 Persistencia de Sesión: El sistema debe utilizar Checkpointers de LangGraph para guardar el estado completo del grafo (memoria conversacional + artefacto) en cada paso.

- NFR-02 Continuidad: El usuario debe poder cerrar el navegador y retomar la sesión exactamente donde la dejó días después.

### 3.2 Gestión de Contexto (LLM Constraints)
- NFR-03 Optimización de Contexto: El sistema no debe enviar el historial completo de la conversación al LLM en interacciones largas. Debe implementar una estrategia de resumen o ventana deslizante, manteniendo siempre el Artefacto Actual completo en el contexto.

### 3.3 Usabilidad y Experiencia
- NFR-04 Lenguaje Natural: El sistema evitará terminología técnica BPMN (como "Gateway Exclusivo Basado en Datos") en la conversación con el usuario, sustituyéndola por lenguaje funcional ("Punto de decisión").

- NFR-05 Latencia Percibida: Para operaciones de generación (que pueden tardar >10s), el sistema debe mostrar indicadores de estado claros ("Analizando estructura...", "Generando XML...").

### 3.4 Fiabilidad
- NFR-06 Determinismo en Estructura: Ante la misma entrada de usuario y las mismas decisiones registradas, el sistema debe generar siempre la misma estructura lógica de proceso.

## 4. Estructura de Datos (El Artefacto)
Para cumplir el FR-06, se define preliminarmente el esquema JSON del Artefacto. Este esquema será la propiedad principal del AgentState en LangGraph.

```json
{
  "process_id": "string",
  "process_name": "string",
  "description": "string (optional)",
  "nodes": [
    {
      "id": "uuid",
      "type": "StartEvent | EndEvent | Task | Gateway",
      "label": "string",
      "role": "string (optional)",
      "gateway_type": "Exclusive | Parallel | Inclusive (optional, only for Gateways)"
    }
  ],
  "edges": [
    {
      "source_id": "uuid",
      "target_id": "uuid",
      "condition": "string (optional)"
    }
  ],
  "decision_log": [
    {
      "decision_id": "uuid",
      "question_asked": "string",
      "user_answer": "string",
      "impacted_elements": ["uuid_list"]
    }
  ],
  "validation_status": {
    "is_valid": "boolean",
    "validation_errors": ["list_of_error_strings"]
  }
}
```

### 5. Arquitectura del Grafo (LangGraph High Level)
Esta sección define los requisitos para la orquestación del grafo.
     
- Nodos Requeridos:
    - ChatNode: Procesa input usuario y genera respuestas/preguntas.
    - AnalyzerNode: Analiza el texto y actualiza el JSON del Artefacto.
    - ReviewerNode: Comprueba el criterio de suficiencia y coherencia.
    - GeneratorNode: Transforma JSON a XML.
    - ValidatorNode: Ejecuta validaciones técnicas.

- Aristas (Edges) Críticas:
    - Conditional Edge: De ReviewerNode a ChatNode (si falta info) O a GeneratorNode (si es suficiente).
    - Conditional Edge: De ValidatorNode a GeneratorNode (si hay error sintáctico - retry) O a End (si éxito).

### 6. Glosario y Definiciones Técnicas
- Artefacto: Estructura JSON intermedia que representa el proceso.
- Alucinación: Invención de datos por parte del LLM no presentes en el input ni en la lógica.
- Happy Path: El flujo ideal del proceso sin excepciones ni errores.
- Gateway: Punto de ramificación o unión en el flujo (Decisión).

### 7. Próximos Pasos
- Diseño de la Arquitectura del Grafo (HLD - High Level Design).
- Definición detallada de Prompts para cada Nodo.
- Implementación del esquema Pydantic para el Artefacto.