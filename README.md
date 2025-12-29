# BPMN Generator - AI-Powered Process Modeling

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-latest-green.svg)](https://github.com/langchain-ai/langgraph)
[![ISO/IEC 19510](https://img.shields.io/badge/BPMN-ISO%2019510-orange.svg)](https://www.omg.org/spec/BPMN/2.0/)

Sistema automatizado basado en agentes LLM que convierte descripciones de procesos en lenguaje natural a diagramas BPMN 2.0 profesionales compatibles con ISO/IEC 19510.

## 🎯 Características

- **Clarificación Interactiva**: Conversación guiada para descubrir información faltante
- **Tipado Semántico**: UserTask, ServiceTask, ScriptTask (no tareas genéricas)
- **Arquitectura de Datos**: DataObjects y DataAssociations automáticos
- **Manejo de Errores**: BoundaryEvents en lugar de Gateways
- **Layout Profesional**: Algoritmo Manhattan Grid para diagramas sin superposiciones
- **Trazabilidad Completa**: Cada elemento BPMN rastreable hasta la conversación original
- **Human-in-the-Loop**: Aprobación explícita antes de generar
- **Persistencia**: Pausar y retomar sesiones días después
- **🔒 Privacy-First**: Soporte para LLMs locales (Ollama, LMStudio) y cloud (OpenAI)
  - **Ollama**: 100% local, sin envío de datos a internet
  - **OpenAI**: Máxima calidad, requiere API key
  - **Switch flexible**: Cambiar entre proveedores según necesidad

## 🏗️ Arquitectura

```
src/bpmn_generator/
├── models/          # Pydantic models (ISO 19510 compliant)
├── agents/          # LLM agents (analyst, critic, chat)
├── graph/           # LangGraph workflow definition
└── utils/           # BPMN validation, XML generation

docs/
├── architecture/    # 5 documentos de especificación técnica
└── references/      # PDFs ISO 19510, guías BPMN

prompts/
├── base/            # Reglas core ISO 19510
└── knowledge/       # Extractos de documentación (RAG futuro)
```

## 🚀 Inicio Rápido

### Requisitos Previos

- Python 3.11+
- OpenAI API Key (o compatible)

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/diversifica/bpmn-generator.git
cd bpmn-generator

# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -e ".[dev]"

# Para soporte local (Ollama)
pip install -e ".[local]"

# Configurar variables de entorno
copy .env.example .env
# Editar .env con configuración de LLM
```

### Configuración de LLM

**Opción 1: OpenAI (Cloud)**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o
```

**Opción 2: Ollama (Local/Privacy) ✅ Recomendado para datos sensibles**
```bash
# 1. Instalar Ollama: https://ollama.ai/download
# 2. Descargar modelo
ollama pull qwen2.5:32b

# 3. Configurar .env
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:32b
```

Ver [docs/LLM_PROVIDERS.md](docs/LLM_PROVIDERS.md) para más detalles.

### Uso Básico

```python
from bpmn_generator import BPMNGenerator

# Inicializar generador
generator = BPMNGenerator()

# Describir proceso en lenguaje natural
description = """
El administrativo recibe una factura y comprueba si es válida.
Si lo es, la paga. Si no, la rechaza y notifica al proveedor.
"""

# Generar BPMN (conversación interactiva)
bpmn_xml = generator.generate(description)

# Guardar archivo
with open("proceso.bpmn", "w", encoding="utf-8") as f:
    f.write(bpmn_xml)
```

## 📚 Documentación

- **[00_Marco_Inicio_Proyecto](docs/architecture/00_Marco_Inicio_Proyecto.md)**: Visión y alcance
- **[01_Requisitos](docs/architecture/01_Requisitos_funcionales_y_no_funcionales.md)**: Requisitos funcionales y no funcionales
- **[02_Modelo_Datos](docs/architecture/02_Modelo_datos_y_estado.md)**: Modelos Pydantic y estado del grafo
- **[03_Arquitectura](docs/architecture/03_arquitectura_y_flujo.md)**: Diseño del grafo LangGraph
- **[04_Prompts](docs/architecture/04_Especificación_de_Prompts_y_Orquestación.md)**: Ingeniería de prompts

## 🤝 Contribuir

Lee [CONTRIBUTING.md](CONTRIBUTING.md) para conocer la metodología de desarrollo orientada a agentes.

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- Basado en [LangGraph](https://github.com/langchain-ai/langgraph) de LangChain
- Cumple con [ISO/IEC 19510:2013](https://www.omg.org/spec/BPMN/2.0/) (BPMN 2.0)
- Compatible con [Camunda](https://camunda.com/), [bpmn.io](https://bpmn.io/), [Bizagi](https://www.bizagi.com/)
