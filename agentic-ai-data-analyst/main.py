from utils.load_data import load_data
from utils.preprocess_data import preprocess_tables
from workflow import build_workflow
from dotenv import load_dotenv
import os
from utils.load_llm import LLMLoader
from state import ReportState


def agentic_ai_data_analyst_main(input_files, schema_files, data_path, schema_path, data_type="csv"):
    
    """ Main function to run the Agentic AI Data Analyst.
    Args:
        input_files (list): List of input files to process.
        data_path (str): Path to the data directory.
    """
    
    try :
        # Load the data
        tables = load_data(input_files,
        schema_files,
        data_path,
        schema_path,
        data_type)
    except Exception as e:
        print(f"Error loading data: {e}")
        return None
    print("\tData loaded successfully.")
    
    try:
        # Preprocess the data
        processed_tables = preprocess_tables(tables)
    except Exception as e:
        print(f"Error preprocessing data: {e}")
        return None
    print("\tData preprocessed successfully.")
    
    try:
        # Load environment variables
        load_dotenv()
        DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
        loader = LLMLoader(deepseek_api_key=DEEPSEEK_API_KEY)
        llm = loader.load_google_model_flash2(temperature=0)
    except Exception as e:
        print(f"Error loading LLM: {e}")
        return None
    
    
    # Run Agentic workflow
    input_context = {
        "llm_model": llm,
        "processed_tables": processed_tables,
        "pdf_path": "output/"
    }
    
    # State
    state = ReportState(input_context)
    state = state.to_dict()
    
    try:
        # Build the workflow
        graph = build_workflow(state)
    except Exception as e:
        print(f"Error building workflow: {e}")  
        return None
    
    try:
        # Run the workflow
        final_state = graph.invoke(state)
    except Exception as e:
        print(f"Error running workflow: {e}")
        
        return None
    

if __name__ == "__main__":

    #修改为本地数据名
    input_files = ["NSCLC_data"]
    schema_files = ["NSCLC_data_schema"]
    data_path = "data/df/"
    schema_path = "data/schema/"

    agentic_ai_data_analyst_main(input_files, schema_files, data_path, schema_path, data_type="csv")
    # Run the main function
        