"""Main entry point for the BPMN Generator CLI.

This script runs the LangGraph workflow in an interactive loop, handling
user inputs and interruptions for clarification.
"""

import sys
import uuid
from typing import Any

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from bpmn_generator.graph.workflow import create_graph
from bpmn_generator.models.schema import ProcessArtifact


def main() -> None:
    """Run the BPMN generator CLI."""
    print("🚀 BPMN Generator Agent (ISO 19510) initialized")
    print("-----------------------------------------------")

    # Initialize graph
    app = create_graph()
    
    # Thread ID for persistence
    thread_id = str(uuid.uuid4())
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

    # Initial user input
    user_input = input("\nDescribe tu proceso de negocio: ")
    
    # Initial state
    initial_artifact = ProcessArtifact(
        process_id="process_1",
        process_name="Generated Process"
    )
    
    current_state = {
        "messages": [HumanMessage(content=user_input)],
        "process_artifact": initial_artifact,
        "current_phase": "planning",
        "revision_count": 0,
        "is_sufficient": False,
        "user_approved": False,
        "missing_info": [],
        "last_update": None,
    }

    # Run loop
    try:
        # First run
        print("\n⏳ Analizando requerimientos y generando modelo...")
        for event in app.stream(current_state, config=config):
            _print_event(event)

        # Interaction loop
        while True:
            # Check status
            snapshot = app.get_state(config)
            
            if not snapshot.next:
                # Execution finished
                result = snapshot.values
                if "bpmn_xml" in result:
                    _save_xml(result["bpmn_xml"])
                else:
                    print("\n❌ El proceso terminó sin generar XML.")
                break
            
            # If we are here, we are likely interrupted at 'chat' node
            # The 'chat' node has executed and added a question to messages
            # We need to get that question and ask the user
            
            last_message = snapshot.values["messages"][-1]
            print(f"\n🤖 Agente: {last_message.content}")
            
            # Get user response
            user_response = input("\n👤 Tú: ")
            
            if user_response.lower() in ["salir", "exit", "quit"]:
                print("👋 Saliendo...")
                break
                
            # Update state with user response
            # We need to add a HumanMessage
            new_message = HumanMessage(content=user_response)
            app.update_state(config, {"messages": [new_message]})
            
            # Resume execution
            print("\n⏳ Procesando respuesta...")
            for event in app.stream(None, config=config):
                 _print_event(event)

    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()


def _print_event(event: dict[str, Any]) -> None:
    """Print workflow events nicely."""
    for node, values in event.items():
        if node == "analyst":
            print("  ✓ Analista ha revisado el modelo")
            if "last_update" in values and values["last_update"]:
                print(f"    (Confianza: {values['last_update'].confidence_score:.0%})")
        elif node == "critic":
            print("  ✓ Crítico ha validado el modelo")
            if values.get("missing_info"):
                print(f"    ⚠️ Información faltante detectada ({len(values['missing_info'])} items)")
        elif node == "generator":
            print("  ✓ Generador ha creado el XML BPMN")


def _save_xml(xml_content: str) -> None:
    """Save the generated XML to a file."""
    filename = "process.bpmn"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(xml_content)
    
    print(f"\n✨ ¡Éxito! Archivo generado: {filename}")
    print(f"📂 Puedes abrirlo en Cawemo o Camunda Modeler.")


if __name__ == "__main__":
    main()
