[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Agentic AI Data Analyst

A Python-based agentic analytics framework that autonomously ingests, explores, analyzes, and reports on tabular datasets using LangGraph, LangChain, and modern LLMs.

## 📝 Overview

This project implements a multi-agent system that acts as an autonomous data analyst. The workflow is orchestrated using LangGraph, where each step is a specialized agent responsible for a specific part of the analysis pipeline.

  * **Data Understanding:** Automated profiling and summary of input tables based on provided schemas.
  * **Analytics Planning:** Dynamically generates a high-level plan of insightful analyses to perform on the data.
  * **Code Generation:** Writes Python (Pandas) code to execute each step of the analysis plan.
  * **Self-Correcting Execution:** Executes the generated code, catches errors, and uses an LLM to correct the code, retrying up to three times.
  * **Content & Visualization Planning:** Interprets the raw results (DataFrames, numbers) and generates insightful narratives. If the result is a DataFrame, it generates and saves a relevant plot.
  * **PDF Report Generation:** Compiles the generated narratives and plots into a polished, professional PDF report.

## 🤖 Agentic Workflow

The core of the project is a graph-based workflow that defines how the agents collaborate:

`START` -\> `data_understanding` -\> `analytics_planning` -\> `code_execution` -\> `content_planning` -\> `report_generation` -\> `END`

## 🚀 Quick Start

1.  **Clone the repo**

    ```bash
    git clone https://github.com/udaybhookya/agentic-ai-data-analyst.git
    cd agentic-ai-data-analyst
    ```

2.  **Create & activate a virtual environment**

    ```bash
    python3 -m venv myenv
    source myenv/bin/activate
    ```

3.  **Install dependencies**

    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

4.  **Configure environment variables**

    Create a `.env` file in the root directory and add your API key:

    ```bash
    GOOGLE_API_KEY="YOUR_API_KEY_HERE"
    ```

5.  **Run the project**

    ```bash
    python main.py
    ```

    The final PDF report will be saved in the `output/` directory.

## 📂 Project Structure

Of course. Here is the updated project structure based on your screenshot.

```
.
├── agents/
│   ├── __pycache__/
│   ├── code_execution_agent.py   # Executes and self-corrects code
│   ├── content_planning_agent.py # Creates plots and narrative summaries
│   ├── plan_analytics.py         # Generates Python code for analyses
│   ├── report_generation.py      # Compiles the final PDF report
│   └── understand_data.py        # Profiles data and suggests analyses
├── data/
│   ├── df/                       # Raw CSV datasets
│   └── schema/                   # Schema descriptions for the data
├── myenv/                        # Python virtual environment
├── output/                       # Generated Reports
├── plots/                        # Saved plots and charts from analysis
├── prompts/
│   ├── code_correction_prompt_template.txt
│   ├── code_generation_prompt_template.txt
│   ├── data_understanding_prompt.txt
│   ├── interpretation_prompt.txt
│   └── plotting_prompt_template.txt
├── utils/
│   ├── __pycache__/
│   ├── load_data.py              # Loads data and schemas
│   ├── load_llm.py               # Initializes the LLM
│   └── preprocess_data.py        # Prepares data for analysis
├── .env                          # API keys and secrets (gitignored)
├── .gitignore
├── main.py                       # Entry-point script to run the agent
├── README.md
├── requirements.txt
├── state.py                      # Defines the shared state object for the workflow
└── workflow.py                   # Builds and compiles the LangGraph workflow
```

## 🤝 Contributing

1.  Fork the repository
2.  Create a feature branch: `git checkout -b feature/my-new-feature`
3.  Commit your changes: `git commit -m "Add my new feature"`
4.  Push to your branch: `git push origin feature/my-new-feature`
5.  Open a Pull Request and describe your changes.

## 📜 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
