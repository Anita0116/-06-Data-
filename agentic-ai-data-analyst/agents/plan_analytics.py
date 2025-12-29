from state import ReportState
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import pandas as pd

# 添加 encoding='utf-8'，强制用utf-8编码读取文件
with open("prompts/code_generation_prompt_template.txt", "r", encoding="utf-8") as f:
        code_generation_prompt_template = f.read()

def analytics_planning_node(state: ReportState) -> dict:
    """
    This node generates Python code for each analytic suggested in the analytics_plan.
    """
    print("\n==========================================")
    print("I am in the analytics planning node ... ")
    print("============================================")

    llm_model = state['llm_model']
    analytics_plan = state['analytics_plan']['analytics_suggested']
    processed_tables = state['processed_tables']
    
    # For simplicity, we'll assume all analytics are for the first table in the plan.
    table_name = analytics_plan[0]['table_name']
    
    # We need the data to be available for the LLM to understand the context for coding
    # df_string = processed_tables[table_name].data.head().to_string()
    
    tables_list = processed_tables.keys()

    input_table_schema = ""

    for one_table in tables_list:

        one_table_schema = processed_tables[one_table].schema

        input_table_schema += f"Table name: {one_table}\n"
# ------------------- 修改点：删除报错行，替换为手动生成表描述 -------------------
        # 原错误行：input_table_schema += f"Table Description: {one_table_schema['table_description'].unique()[0]}\n\n"
        # 新逻辑：手动生成NSCLC数据的表描述（与understand_data.py保持一致）
        table_desc = "NSCLC患者队列数据，包含14个临床与分子特征字段，涵盖患者的TMB、PD-L1表达、生存状态等关键信息"
        input_table_schema += f"Table Description: {table_desc}\n\n"
        # --------------------------------------------------------------------------------
        input_table_schema += f"Columns description of table {one_table}:\n"

        for idx, one_row in one_table_schema.iterrows():
            input_table_schema += f"Column name: {one_row['column_name']}\n"
            input_table_schema += f"Column description: {one_row['column_description']}\n"
            input_table_schema += f"Column type: {one_row['data_type']}\n\n"

        input_table_schema += "\n\n"

    code_generation_prompt = PromptTemplate(
        input_variables=["input_table_schema", "analytic_description"],
        template=code_generation_prompt_template
    )

    parser = StrOutputParser()
    code_generation_chain = code_generation_prompt | llm_model | parser

    generated_code = []

    for one_analytic in analytics_plan:
        print(f"Generating code for: {one_analytic['analysis_name']}")
        
        analytic_description = one_analytic['description']
        
        # Generate the code
        code = code_generation_chain.invoke({
            "input_table_schema": input_table_schema,
            "analytic_description": analytic_description
        })
        
        generated_code.append({
            "analysis_name": one_analytic['analysis_name'],
            "code": code
        })
        
        print("Generated Code:")
        print(code)
        print("-----------------------------------")

    state['analytics_code'] = generated_code
    
    return state
