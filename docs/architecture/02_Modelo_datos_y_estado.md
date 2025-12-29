# Documento 02
Definición del Modelo de Datos y Estado del Sistema
Sistema Automatizado para la Clarificación y Modelado BPMN
Control del documento
Versión: 1.0

Estado: Propuesta de Diseño de Datos

Tipo: Especificación Técnica de Datos (Data Spec)

Documento Fuente: Doc 01 (Requisitos)

Tecnología Base: Pydantic V2, LangGraph State

## 1. Introducción
Este documento define la estructura rigurosa de la información que fluye a través del sistema. Establece dos pilares fundamentales para la implementación en LangGraph:

- El Modelo de Dominio (Artefacto): Cómo representamos internamente un proceso de negocio, independientemente del XML de salida.
- El Estado del Grafo (GraphState): La memoria compartida que los agentes (nodos) leen y escriben durante la ejecución.

## 2. Modelo de Dominio: El Artefacto de Proceso
El "Artefacto" es la fuente de verdad. No es un XML, es un grafo de objetos. Se implementará mediante modelos Pydantic para garantizar tipado fuerte y validación en tiempo de ejecución.

## 2.1 Entidades Base (Nodos y Conexiones) - ISO/IEC 19510 Compliant

```python
from typing import Literal, Optional, List, Union
from pydantic import BaseModel, Field, Discriminator
from typing_extensions import Annotated

# --- Eventos ---
class StartEventNode(BaseModel):
    """Evento de inicio del proceso."""
    id: str = Field(description="Identificador único (UUID)")
    type: Literal["StartEvent"] = "StartEvent"
    label: str = Field(default="Inicio", description="Etiqueta del evento")

class EndEventNode(BaseModel):
    """Evento de fin del proceso."""
    id: str = Field(description="Identificador único (UUID)")
    type: Literal["EndEvent"] = "EndEvent"
    label: str = Field(default="Fin", description="Etiqueta del evento")

class BoundaryEventNode(BaseModel):
    """Evento de frontera adjunto a una actividad (para manejo de errores/timeouts)."""
    id: str = Field(description="Identificador único (UUID)")
    type: Literal["BoundaryEvent"] = "BoundaryEvent"
    label: str = Field(description="Etiqueta del evento")
    attached_to_ref: str = Field(description="ID de la tarea/subproceso al que está adjunto")
    event_type: Literal["error", "timer", "message"] = Field(description="Tipo de evento de frontera")
    cancel_activity: bool = Field(default=True, description="Si interrumpe la actividad padre")

# --- Tareas (ISO 19510 - Tipado Semántico Obligatorio) ---
class UserTaskNode(BaseModel):
    """Tarea que requiere interacción humana."""
    id: str = Field(description="Identificador único (UUID)")
    type: Literal["UserTask"] = "UserTask"
    label: str = Field(description="Nombre de la tarea")
    role: Optional[str] = Field(default=None, description="Rol o actor responsable")

class ServiceTaskNode(BaseModel):
    """Tarea automatizada (llamada a servicio/API)."""
    id: str = Field(description="Identificador único (UUID)")
    type: Literal["ServiceTask"] = "ServiceTask"
    label: str = Field(description="Nombre de la tarea")
    implementation: Optional[str] = Field(default=None, description="Tipo de implementación (ej: 'webService')")

class ScriptTaskNode(BaseModel):
    """Tarea que ejecuta un script."""
    id: str = Field(description="Identificador único (UUID)")
    type: Literal["ScriptTask"] = "ScriptTask"
    label: str = Field(description="Nombre de la tarea")
    script_format: Optional[str] = Field(default="python", description="Lenguaje del script")

class SendTaskNode(BaseModel):
    """Tarea de envío de mensaje."""
    id: str = Field(description="Identificador único (UUID)")
    type: Literal["SendTask"] = "SendTask"
    label: str = Field(description="Nombre de la tarea")

class ReceiveTaskNode(BaseModel):
    """Tarea de recepción de mensaje."""
    id: str = Field(description="Identificador único (UUID)")
    type: Literal["ReceiveTask"] = "ReceiveTask"
    label: str = Field(description="Nombre de la tarea")

# --- Gateways ---
GatewayType = Literal["Exclusive", "Parallel", "Inclusive"]

class GatewayNode(BaseModel):
    """Compuerta de decisión o convergencia."""
    id: str = Field(description="Identificador único (UUID)")
    type: Literal["Gateway"] = "Gateway"
    label: str = Field(description="Pregunta o condición de decisión")
    gateway_type: GatewayType = Field(description="Tipo de gateway")
    default_flow: Optional[str] = Field(default=None, description="ID del flujo por defecto (camino feliz)")

# --- Subprocesos ---
class SubProcessNode(BaseModel):
    """Subproceso que encapsula lógica compleja o iterativa."""
    id: str = Field(description="Identificador único (UUID)")
    type: Literal["SubProcess"] = "SubProcess"
    label: str = Field(description="Nombre del subproceso")
    is_expanded: bool = Field(default=True, description="Si se muestra expandido en el diagrama")
    loop_characteristics: Optional[Literal["sequential", "parallel"]] = Field(
        default=None, 
        description="Si es multi-instancia (para procesar lotes)"
    )

# --- Data Objects (Arquitectura de Datos ISO 19510) ---
class DataObjectNode(BaseModel):
    """Objeto de datos que representa información procesada."""
    id: str = Field(description="Identificador único (UUID)")
    type: Literal["DataObject"] = "DataObject"
    label: str = Field(description="Nombre del dato (ej: 'Factura', 'Archivo PDF')")
    is_collection: bool = Field(default=False, description="Si representa múltiples items")

class DataObjectReferenceNode(BaseModel):
    """Referencia a un DataObject (para reutilización)."""
    id: str = Field(description="Identificador único (UUID)")
    type: Literal["DataObjectReference"] = "DataObjectReference"
    label: str = Field(description="Nombre de la referencia")
    data_object_ref: str = Field(description="ID del DataObject al que apunta")

# --- Unión Discriminada (Type-Safe) ---
BPMNNode = Annotated[
    Union[
        StartEventNode,
        EndEventNode,
        BoundaryEventNode,
        UserTaskNode,
        ServiceTaskNode,
        ScriptTaskNode,
        SendTaskNode,
        ReceiveTaskNode,
        GatewayNode,
        SubProcessNode,
        DataObjectNode,
        DataObjectReferenceNode,
    ],
    Field(discriminator="type")
]

# --- Aristas (Sequence Flows) ---
class BPMNEdge(BaseModel):
    """Representa el flujo de secuencia (flecha) entre dos nodos."""
    source_id: str = Field(description="ID del nodo origen")
    target_id: str = Field(description="ID del nodo destino")
    condition: Optional[str] = Field(default=None, description="Condición lógica para transitar (etiqueta de la flecha)")
    is_default: bool = Field(default=False, description="Si es el flujo por defecto de un Gateway")

# --- Asociaciones de Datos (Data Associations) ---
class DataAssociation(BaseModel):
    """Asociación entre una tarea y un DataObject (línea punteada)."""
    id: str = Field(description="Identificador único")
    source_ref: str = Field(description="ID del elemento origen (Task o DataObject)")
    target_ref: str = Field(description="ID del elemento destino (Task o DataObject)")
    association_type: Literal["input", "output"] = Field(description="Dirección de la asociación")
```


## 2.2 El Objeto Proceso (El Artefacto Completo)
Este es el objeto que se transformará a XML al final.

```python
from pydantic import model_validator

class ProcessArtifact(BaseModel):
    """El contenedor principal del conocimiento del proceso."""
    process_id: str
    process_name: str
    description: Optional[str] = None
    
    # El Grafo
    nodes: List[BPMNNode] = Field(default_factory=list)
    edges: List[BPMNEdge] = Field(default_factory=list)
    
    # Arquitectura de Datos (ISO 19510)
    data_objects: List[DataObjectNode] = Field(
        default_factory=list, 
        description="Objetos de datos procesados en el flujo"
    )
    data_associations: List[DataAssociation] = Field(
        default_factory=list,
        description="Asociaciones entre tareas y datos (input/output)"
    )
    
    # Metadatos de Calidad
    is_valid: bool = Field(default=False, description="Flag de validación interna")
    validation_errors: List[str] = Field(default_factory=list, description="Lista de errores técnicos actuales")

    # Registro de decisiones (Trazabilidad)
    decision_log: List[dict] = Field(default_factory=list, description="Historial de por qué se creó cada elemento")
    
    @model_validator(mode='after')
    def validate_graph_integrity(self) -> 'ProcessArtifact':
        """Valida la integridad del grafo: todas las aristas deben referenciar nodos existentes."""
        node_ids = {node.id for node in self.nodes}
        errors = []
        
        for edge in self.edges:
            if edge.source_id not in node_ids:
                errors.append(f"Edge references non-existent source node: {edge.source_id}")
            if edge.target_id not in node_ids:
                errors.append(f"Edge references non-existent target node: {edge.target_id}")
        
        # Validar referencias de BoundaryEvents
        for node in self.nodes:
            if hasattr(node, 'attached_to_ref'):  # BoundaryEventNode
                if node.attached_to_ref not in node_ids:
                    errors.append(f"BoundaryEvent '{node.id}' references non-existent task: {node.attached_to_ref}")
        
        # Validar asociaciones de datos
        all_element_ids = node_ids | {do.id for do in self.data_objects}
        for assoc in self.data_associations:
            if assoc.source_ref not in all_element_ids:
                errors.append(f"DataAssociation references non-existent source: {assoc.source_ref}")
            if assoc.target_ref not in all_element_ids:
                errors.append(f"DataAssociation references non-existent target: {assoc.target_ref}")
        
        # Actualizar campos de validación
        self.validation_errors = errors
        self.is_valid = len(errors) == 0
        return self
```


## 3. Estado del Grafo (LangGraph State)
En LangGraph, el estado es lo que se pasa de un nodo a otro. Debe contener no solo el Artefacto, sino también el contexto de la conversación y las banderas de control de flujo.

Definimos AgentState como un TypedDict (o clase Pydantic) que será inyectado en el grafo.

```python
from typing import TypedDict, Annotated, Optional, List
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # --- Memoria Conversacional ---
    # Usamos 'add_messages' para que LangGraph maneje el append automáticamente
    messages: Annotated[list, add_messages]
    
    # --- Estado del Proceso (Core) ---
    # El objeto Artefacto definido en la sección 2.2
    process_artifact: ProcessArtifact
    
    # --- Control de Flujo ---
    # Indica en qué fase lógica estamos
    current_phase: Literal["clarification", "validation", "generation", "completed"]
    
    # Contador para evitar bucles infinitos en auto-correcciones
    revision_count: int
    
    # --- Flags de Routing (Críticos para Conditional Edges) ---
    # Indica si el proceso cumple el criterio de suficiencia mínima
    is_sufficient: bool
    
    # Indica si el usuario ha aprobado proceder a la generación
    user_approved: bool
    
    # Lista de información faltante detectada por el critic_node
    missing_info: List[str]
    
    # --- Contexto para Chat Node ---
    # Última actualización realizada por el analyzer_node (para confirmación al usuario)
    last_update: Optional[ProcessUpdate]
    
    # --- Escalabilidad Futura: RAG (OPCIONAL) ---
    # Contexto recuperado de base de conocimiento (PDFs ISO, guías BPMN)
    # Inicialmente None. Se poblará si se implementa knowledge_retrieval_node
    knowledge_context: Optional[str]
    
    # --- Feedback del Usuario ---
    # Última instrucción explícita del usuario para guiar al siguiente nodo
    user_intent: Optional[Literal["continue_interview", "approve_artifact", "modify_structure", "cancel"]]
```


Explicación de campos clave:
- messages: Mantiene el historial del chat (SystemMessage, HumanMessage, AIMessage). Es vital para que el LLM tenga contexto.
- process_artifact: A diferencia de los mensajes (que son texto), esto es estructura pura. Los nodos Analyzer leerán los mensajes y escribirán en este campo.
- revision_count: Vital para los requisitos de seguridad. Si el generador falla 3 veces, el grafo aborta y pide ayuda humana.
- **is_sufficient**: Flag booleano actualizado por el `critic_node`. Indica si el proceso cumple los 4 criterios de suficiencia mínima (Inicio, Fin, Continuidad, Responsabilidad). Usado por el `after_update_router` para decidir si continuar clarificando o proceder a generación.
- **user_approved**: Flag booleano que indica si el usuario ha dado aprobación explícita para generar el BPMN. Evita generación automática sin confirmación humana.
- **missing_info**: Lista de strings generada por el `critic_node` que describe qué información falta o qué ambigüedades críticas existen. El `chat_node` usa esta lista para formular la siguiente pregunta al usuario.
- **last_update**: Objeto `ProcessUpdate` opcional que contiene la última modificación realizada al artefacto. Permite al `chat_node` confirmar al usuario qué se añadió/modificó (ej: "Entendido, he añadido la tarea 'Validar factura'...").

## 4. Interfaces de Entrada/Salida de LLMs (Structured Outputs)
Para interactuar con el LLM de forma robusta, no le pediremos "texto plano" para actualizar el modelo, sino que le forzaremos a usar herramientas (Tools) o Salidas Estructuradas.

## 4.1 Output del Analista (ProcessUpdate)
Cuando el agente detecta nueva información en el chat, emite esta estructura:

```python
class ProcessUpdate(BaseModel):
    """Estructura que el LLM genera para modificar el proceso."""
    thoughts: str = Field(description="Razonamiento del analista sobre qué ha cambiado")
    
    new_nodes: List[BPMNNode] = Field(default_factory=list)
    new_edges: List[BPMNEdge] = Field(default_factory=list)
    
    # Arquitectura de Datos (ISO 19510)
    new_data_objects: List[DataObjectNode] = Field(
        default_factory=list,
        description="Nuevos objetos de datos identificados"
    )
    new_data_associations: List[DataAssociation] = Field(
        default_factory=list,
        description="Nuevas asociaciones entre tareas y datos"
    )
    
    # Si hay nodos que borrar o modificar
    nodes_to_remove: List[str] = Field(default_factory=list, description="IDs de nodos a eliminar")
    
    # Estado de completitud percibido
    confidence_score: float = Field(description="Del 0 al 1, qué tan completo ve el proceso")
    missing_information: List[str] = Field(description="Qué falta para cerrar el flujo")
```


## 4.2 Output del Entrevistador (NextQuestion)
Cuando el sistema decide preguntar al usuario:

```python

class ClarificationQuestion(BaseModel):
    """Generación de la siguiente intervención del bot."""
    question_text: str = Field(description="La pregunta en lenguaje natural amigable")
    question_type: Literal["confirmation", "selection", "open"] 
    options: Optional[List[str]] = Field(description="Opciones sugeridas si es selección")
    context_reason: str = Field(description="Por qué estoy preguntando esto (para debug)")
```

## 5. Principios de Persistencia (Checkpoints)
Dado que usamos LangGraph, la persistencia no es una base de datos SQL tradicional que diseñamos nosotros, sino el mecanismo de MemorySaver o PostgresSaver de LangGraph.

- Snapshot Key: thread_id (Identificador de la sesión del usuario).
- Contenido guardado: Todo el objeto AgentState descrito en la Sección 3.
- Estrategia: Se guarda un checkpoint después de cada nodo. Esto permite "Time Travel" (viajar al pasado) si el usuario dice "No, espera, lo que te dije hace dos preguntas estaba mal".

## 6. Validación de Coherencia
Reglas que se aplicarán programáticamente sobre el ProcessArtifact:

- Regla de Integridad de IDs: Ningún edge puede apuntar a un source_id o target_id que no exista en la lista nodes.
- Regla de Unicidad: No pueden existir dos nodos con el mismo id.

Regla de Tipado: Un nodo de tipo Gateway debe tener al menos 2 flujos de salida (si es divergente) o 2 de entrada (si es convergente), salvo excepciones controladas.

## 7. Siguiente paso natural
Con los datos definidos, ya podemos dibujar el mapa de cómo se transforman estos datos.