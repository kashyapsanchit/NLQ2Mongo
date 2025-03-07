from src.ai.agents.generation import ContextDetectionAgent,QueryGenerationAgent,ImprovementAgent
from src.ai.state import GenerationState
from langgraph.graph import StateGraph, END
from src.backend.db import MongoEngine
# from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles



class GraphBuilder:
    def __init__(self):
        """Build the state graph for stock analysis."""
        self.engine = MongoEngine()

        # Initialize nodes
        self.context_detection_agent = ContextDetectionAgent()
        self.query_generation_agent = QueryGenerationAgent()
        self.improvement_agent = ImprovementAgent()

        self.workflow = StateGraph(GenerationState)

        # Add nodes to the graph
        self.workflow.add_node("detect_context", self.context_detection_agent.context_detection)
        self.workflow.add_node("generate", self.query_generation_agent.query_generator)
        self.workflow.add_node("execute", self.engine.execute_query)
        self.workflow.add_node("improve", self.improvement_agent.improve_query)

        # Define workflow sequence
        self.workflow.set_entry_point("detect_context")
        self.workflow.add_edge("detect_context", "generate")
        self.workflow.add_edge("generate", "execute")
        self.workflow.add_conditional_edges("execute", self.check_retry_limit)
        self.workflow.add_edge("improve", "execute")

        self.app = self.workflow.compile()

    def create_workflow(self):
        return self.app
    

    def check_retry_limit(self,state):
        if state.get("execution_status"):
            return END
        elif state.get("retry_count", 0) >= 1:
            return END  
        else:
            state["retry_count"] = state.get("retry_count", 0) + 1
            return "improve"





    

    