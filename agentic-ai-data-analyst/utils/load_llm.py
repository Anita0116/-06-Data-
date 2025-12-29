from langchain_openai import ChatOpenAI
from typing import Any

class LLMLoader:
    def __init__(self, deepseek_api_key: str):
         self.deepseek_api_key = deepseek_api_key

    def load_google_model_pro(self, temperature=0):
        """_summary_

        Args:
            temperature (int, optional): _description_. Defaults to 0.

        Returns:
            _type_: _description_
        """
        return ChatOpenAI(
            model_name="deepseek-chat",  # DeepSeek 通用对话/代码模型，可替换为 deepseek-coder-v2
            api_key=self.deepseek_api_key,
            base_url="https://api.deepseek.com/v1",  # DeepSeek API 固定基础地址
            temperature=temperature,
            max_tokens=None,
            timeout=None,
            max_retries=2
        )

    def load_google_model_flash2(self, temperature=0):
        """_summary_

        Args:
            temperature (int, optional): _description_. Defaults to 0.

        Returns:
            _type_: _description_
        """
        
        return ChatOpenAI(
            model_name="deepseek-chat",  # 若有轻量版可替换，无则沿用主力模型
            api_key=self.deepseek_api_key,
            base_url="https://api.deepseek.com/v1",
            temperature=temperature,
            max_tokens=None,
            timeout=None,
            max_retries=2
        )