# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Multi-provider LLM support (OpenAI, Ollama, LMStudio)
- Privacy-focused switching between cloud and local LLMs
- Comprehensive CONTRIBUTING.md for agent-driven development
- Git Flow workflow with develop branch

## [0.1.0] - 2025-12-29 - "Foundation"

### Added
- Initial project structure with professional Python package layout
- Complete technical documentation (5 architecture documents)
- ISO/IEC 19510 BPMN 2.0 compliance specifications
- Pydantic models for 12 BPMN node types
- Data architecture support (DataObjects, DataAssociations)
- BoundaryEvents for error handling
- Manhattan Grid DI layout algorithm
- LangGraph-based multi-agent architecture design
- Comprehensive test infrastructure (pytest, ruff, mypy)
- Development environment configuration
- MIT License

### Documentation
- 00_Marco_Inicio_Proyecto.md - Project vision and scope
- 01_Requisitos_funcionales_y_no_funcionales.md - Requirements
- 02_Modelo_datos_y_estado.md - Pydantic models and state
- 03_arquitectura_y_flujo.md - LangGraph architecture
- 04_Especificación_de_Prompts_y_Orquestación.md - Prompt engineering
- LLM_PROVIDERS.md - Multi-provider configuration guide
- CONTRIBUTING.md - Development methodology

### Infrastructure
- pyproject.toml with dependencies and tool configs
- .gitignore for Python projects
- .env.example with multi-provider LLM configuration
- GitHub repository: https://github.com/diversifica/bpmn-generator

---

**Note**: Version 0.1.0 is the foundation release. No code implementation yet - this is the complete specification and project setup ready for development.
