from .graph_builder import GraphBuilder


async def execute_workflow(state):
    """Execute the graph step-by-step."""

    try:
        workflow = GraphBuilder().create_workflow()
        result = await workflow.ainvoke(state)
        return result
    except Exception as e:
        raise Exception(f"Error during graph execution: {str(e)}")