from typing import TypedDict, Dict, Any, List
import pandas as pd

class ReportState:
    """
    This class represents the state of the report generation process.
    It contains all the necessary information to generate a report.
    """
    
    def __init__(self, input_context):
        self.llm_model = input_context["llm_model"]
        self.processed_tables = input_context["processed_tables"]
        self.pdf_path = input_context["pdf_path"]
        self.analytics_plan = []
        self.query_results = []
        self.visualizations = []
        self.report_content = ""
        self.pdf_path = ""
        self.analytics_code = []
        self.report_content = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the ReportState to a dictionary."""
        return {
            "llm_model": self.llm_model,
            "processed_tables": self.processed_tables,
            "analytics_plan": self.analytics_plan,
            "query_results": self.query_results,
            "visualizations": self.visualizations,
            "report_content": self.report_content,
            "pdf_path": self.pdf_path
        }
    
    
    