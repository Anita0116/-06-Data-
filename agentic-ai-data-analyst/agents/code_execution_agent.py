import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from lifelines import KaplanMeierFitter
import io
import sys
from state import ReportState
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import re

# =========================
# 新增：双生物标志物更直观画法
# =========================
def plot_dual_biomarker_scatter(df, tmb_cutoff, pdl1_cutoff, save_path):
    """
    TMB / PD-L1 双生物标志物散点 + 阈值分割图
    用于替代“只有两个点”的最优阈值图
    """

    plt.figure(figsize=(7, 6))

    plt.scatter(
        df["TMB"],
        df["PDL1_TPS"],
        alpha=0.6
    )

    plt.axvline(tmb_cutoff, linestyle="--", linewidth=1)
    plt.axhline(pdl1_cutoff, linestyle="--", linewidth=1)

    plt.xlabel("Tumor Mutational Burden (TMB)")
    plt.ylabel("PD-L1 TPS (%)")
    plt.title("TMB and PD-L1 Dual Biomarker Risk Stratification")

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


# =========================
# 读取 Prompt 模板
# =========================
with open("prompts/code_correction_prompt_template.txt", "r", encoding="utf-8") as f:
    code_correction_prompt_template = f.read()


def clean_python_code(code_string: str) -> str:
    """
    Cleans a string to ensure it's valid Python code by removing markdown fences
    and other non-code text.
    """
    code_string = re.sub(r'```python\n', '', code_string)
    code_string = re.sub(r'```', '', code_string)
    return code_string.strip()


def inject_missing_imports(code: str) -> str:
    """
    自动检测代码中使用的模块，补全缺失的导入语句，
    并添加 Matplotlib 中文字体配置
    """
    import_map = {
        "np.": "import numpy as np\n",
        "pd.": "import pandas as pd\n",
        "plt.": "import matplotlib.pyplot as plt\n",
        "stats.": "from scipy import stats\n",
        "KaplanMeierFitter": "from lifelines import KaplanMeierFitter\n",
        "kmf.": "from lifelines import KaplanMeierFitter\n"
    }

    imports_to_add = []
    added_imports = set()
    for pattern, import_stmt in import_map.items():
        if pattern in code and import_stmt not in added_imports:
            imports_to_add.append(import_stmt)
            added_imports.add(import_stmt)

    font_config = """
# 解决 Matplotlib 中文显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
""" if "plt." in code else ""

    final_code = "".join(imports_to_add) + font_config + code

    lines = final_code.split("\n")
    unique_lines = []
    seen_imports = set()
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith(("import ", "from ")):
            if stripped_line in seen_imports:
                continue
            seen_imports.add(stripped_line)
        unique_lines.append(line)

    return "\n".join(unique_lines)


def code_execution_node(state: ReportState) -> dict:
    """
    Executes the generated python code for each analytic.
    If an error occurs, it attempts to correct the code and rerun it.
    """
    print("\n==========================================")
    print("I am in the code execution node ... ")
    print("============================================")

    llm_model = state['llm_model']
    analytics_code = state['analytics_code']
    processed_tables = state['processed_tables']
    query_results = []

    code_correction_prompt = PromptTemplate(
        input_variables=["code", "error"],
        template=code_correction_prompt_template
    )

    correction_chain = code_correction_prompt | llm_model | StrOutputParser()

    for idx, analytic in enumerate(analytics_code):
        code_to_execute = clean_python_code(analytic['code'])
        code_to_execute = inject_missing_imports(code_to_execute)

        analysis_name = analytic['analysis_name']
        max_retries = 4

        for attempt in range(max_retries):
            print(f"Executing code for '{analysis_name}' (Attempt {attempt + 1}/{max_retries})")

            try:
                table_name = state['analytics_plan']['analytics_suggested'][idx]['table_name']
                df = processed_tables[table_name].df.copy()

                local_scope = {
                    'df': df,
                    'pd': pd,
                    'np': np,
                    'stats': stats,
                    'KaplanMeierFitter': KaplanMeierFitter,
                    'plt': plt,
                    'plot_dual_biomarker_scatter': plot_dual_biomarker_scatter
                }

                exec(code_to_execute, globals(), local_scope)
                result = local_scope['analyze_data'](df)

                query_results.append({
                    "analysis_name": analysis_name,
                    "result": result
                })

                print(f"Successfully executed code for: {analysis_name}")
                break

            except Exception as e:
                error_message = str(e)
                print(f"Error executing code for {analysis_name}: {error_message}")

                if attempt < max_retries - 1:
                    print("Attempting to correct the code...")
                    corrected_code_raw = correction_chain.invoke({
                        "code": code_to_execute,
                        "error": error_message
                    })
                    code_to_execute = clean_python_code(corrected_code_raw)
                    code_to_execute = inject_missing_imports(code_to_execute)
                    state['analytics_code'][idx]['code'] = code_to_execute
                else:
                    query_results.append({
                        "analysis_name": analysis_name,
                        "result": f"Error after {max_retries} attempts: {error_message}"
                    })

    state['query_results'] = query_results
    return state
