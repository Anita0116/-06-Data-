from state import ReportState
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import pandas as pd
import matplotlib.pyplot as plt
import os
import re
import matplotlib.pyplot as plt
import matplotlib as mpl

#添加中文字体配置代码
plt.rcParams['font.sans-serif'] = ['SimHei']  
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示为方块的问题
mpl.rcParams['font.family'] = 'sans-serif'    # 确认字体家族


with open("prompts/plotting_prompt_template.txt", "r",encoding='utf-8') as f:
        plotting_prompt_template = f.read()
        
with open("prompts/interpretation_prompt_template.txt", "r",encoding='utf-8') as f:
        interpretation_prompt_template = f.read()
        

def clean_python_code(code_string: str) -> str:
    """
    Cleans a string to ensure it's valid Python code by removing markdown fences
    and other non-code text.
    """
    # Remove markdown code blocks
    code_string = re.sub(r'```python\n', '', code_string)
    code_string = re.sub(r'```', '', code_string)
    
    # Strip leading/trailing whitespace
    return code_string.strip()

def execute_plot_code(code: str, df: pd.DataFrame, file_path: str):
    """
    Executes plotting code in a controlled environment.
    """
    try:
        # The generated code expects 'df' and 'plt' to be available.
        local_scope = {'df': df, 'plt': plt}
        exec(code, globals(), local_scope)
        plt.savefig(file_path)
        plt.close() # Close the plot to free up memory
        print(f"Plot saved to {file_path}")
        return file_path
    except Exception as e:
        print(f"Error executing plot code: {e}")
        return None

def content_planning_node(state: ReportState) -> dict:
    """
    Generates plots from DataFrames and creates narrative summaries for all results.
    """
    print("\n==========================================")
    print("I am in the content planning node ... ")
    print("============================================")

    llm_model = state['llm_model']
    query_results = state['query_results']
    
    # Make sure the 'plots' directory exists
    os.makedirs("plots", exist_ok=True)

    plotting_prompt = PromptTemplate(
        input_variables=["analysis_name", "df_columns", "df_head"],
        template=plotting_prompt_template
    )
    plotting_chain = plotting_prompt | llm_model | StrOutputParser()

    interpretation_prompt = PromptTemplate(
        input_variables=["analysis_name", "analysis_result"],
        template=interpretation_prompt_template
    )
    interpretation_chain = interpretation_prompt | llm_model | StrOutputParser()

    report_content = []

    for idx, result in enumerate(query_results):
        analysis_name = result['analysis_name']
        analysis_result = result['result']
        
        narrative_input = ""
        final_result_for_report = analysis_result

        if isinstance(analysis_result, pd.DataFrame):
            print(f"Result for '{analysis_name}' is a DataFrame. Generating plot...")
            
            # Generate plotting code
            plot_code_raw = plotting_chain.invoke({
                "analysis_name": analysis_name,
                "df_columns": list(analysis_result.columns),
                "df_head": analysis_result.head().to_string()
            })
            plot_code = clean_python_code(plot_code_raw)
            
            # Execute plotting code
            plot_file_path = f"plots/plot_{idx}.png"
            execute_plot_code(plot_code, analysis_result, plot_file_path)
            
            # The result for the report is now the plot file path
            final_result_for_report = plot_file_path
            narrative_input = f"The analysis produced a plot saved at '{plot_file_path}'. The plot visualizes the results of the analysis titled: '{analysis_name}'. Your task is to explain what this plot shows."

        else:
            narrative_input = str(analysis_result)

        print(f"Generating summary for: {analysis_name}")
        narrative = interpretation_chain.invoke({
            "analysis_name": analysis_name,
            "analysis_result": narrative_input
        })
        
        report_content.append({
            "analysis_name": analysis_name,
            "narrative": narrative,
            "original_result": final_result_for_report
        })
        print("Generated Narrative:")
        print(narrative)
        print("-----------------------------------")

    state['report_content'] = report_content
    return state
