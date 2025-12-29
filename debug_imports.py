try:
    from langgraph.graph import CompiledGraph
    print("Found CompiledGraph in langgraph.graph")
except ImportError:
    print("Not found in langgraph.graph")

try:
    from langgraph.graph.graph import CompiledGraph
    print("Found CompiledGraph in langgraph.graph.graph")
except ImportError:
    print("Not found in langgraph.graph.graph")

try:
    from langgraph.graph.state import CompiledStateGraph
    print("Found CompiledStateGraph in langgraph.graph.state")
except ImportError:
    print("Not found in langgraph.graph.state")

import langgraph
print(f"LangGraph version: {langgraph.__version__ if hasattr(langgraph, '__version__') else 'unknown'}")
