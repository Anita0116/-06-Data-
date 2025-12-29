from langgraph.graph import StateGraph, START, END
from state import ReportState
from agents.understand_data import data_understanding_node
from agents.plan_analytics import analytics_planning_node
from agents.code_execution_agent import code_execution_node
from agents.content_planning_agent import content_planning_node
from agents.report_generation import report_generation_node
from IPython.display import Image, display


def build_workflow(state):
    """Builds the workflow for the Agentic AI Data Analyst."""
    
    # Build the LangGraph
    workflow = StateGraph(dict)

    workflow.add_node("data_understanding", data_understanding_node)
    workflow.add_node("analytics_planning", analytics_planning_node)
    workflow.add_node("code_execution", code_execution_node)
    workflow.add_node("content_planning", content_planning_node)
    workflow.add_node("report_generation", report_generation_node)


    workflow.add_edge(START, "data_understanding")
    workflow.add_edge("data_understanding", "analytics_planning")
    workflow.add_edge("analytics_planning", "code_execution")
    workflow.add_edge("code_execution", "content_planning")
    workflow.add_edge("content_planning", "report_generation")
    workflow.add_edge("report_generation", END)
    
    # img = workflow.compile().get_graph(xray=True).draw_mermaid_png()
    # with open('graph.png', 'wb') as f:
    #     f.write(img)
    
    return workflow.compile()
