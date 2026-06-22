"""LangGraph orchestrator — wires the four agents into a sequential pipeline.

Pipeline: START → parser → classifier → risk_analyzer → report_generator → END
"""

from langgraph.graph import StateGraph, END
from agents.state import PipelineState
from agents.parser_agent import parser_agent
from agents.classifier_agent import classifier_agent
from agents.risk_agent import risk_agent
from agents.report_agent import report_agent


def build_pipeline() -> StateGraph:
    """Construct and compile the multi-agent LangGraph pipeline."""

    workflow = StateGraph(PipelineState)

    # Register agent nodes
    workflow.add_node("parser", parser_agent)
    workflow.add_node("classifier", classifier_agent)
    workflow.add_node("risk_analyzer", risk_agent)
    workflow.add_node("report_generator", report_agent)

    # Define the sequential flow
    workflow.set_entry_point("parser")
    workflow.add_edge("parser", "classifier")
    workflow.add_edge("classifier", "risk_analyzer")
    workflow.add_edge("risk_analyzer", "report_generator")
    workflow.add_edge("report_generator", END)

    return workflow.compile()


# Pre-compiled pipeline singleton
pipeline = build_pipeline()


def run_pipeline(file_path: str, status_callback=None) -> dict:
    """
    Execute the full contract review pipeline on a PDF file.

    Returns the final PipelineState dict containing:
      - final_report: the structured ContractReport
      - status: 'complete' or an error status
      - errors: list of any non-fatal errors encountered
    """
    print(f"\n{'='*60}")
    print(f"  MULTI-AGENT CONTRACT REVIEW PIPELINE")
    print(f"  File: {file_path}")
    print(f"{'='*60}")

    initial_state: PipelineState = {
        "file_path": file_path,
        "raw_text": "",
        "cleaned_pages": [],
        "page_count": 0,
        "identified_clauses": [],
        "risk_assessments": [],
        "overall_risk_score": 0.0,
        "final_report": {},
        "status": "starting",
        "errors": [],
    }

    current_state = dict(initial_state)

    # Use pipeline.stream to get updates after each node executes
    for update in pipeline.stream(initial_state, stream_mode="updates"):
        node_name = list(update.keys())[0]
        node_output = update[node_name]
        
        # Merge changes into our tracking state
        for k, v in node_output.items():
            current_state[k] = v
            
        if status_callback:
            try:
                status_callback(node_name, current_state)
            except Exception as e:
                print(f"  [Callback Warning] Error in pipeline status callback: {e}")

    print(f"\n{'='*60}")
    print(f"  PIPELINE COMPLETE — Status: {current_state.get('status', 'unknown')}")
    if current_state.get("errors"):
        print(f"  Warnings/Errors: {len(current_state['errors'])}")
        for err in current_state["errors"]:
            print(f"    - {err}")
    print(f"{'='*60}\n")

    return current_state
