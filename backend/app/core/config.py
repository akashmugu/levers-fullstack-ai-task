from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openrouter_api_key: str = ""
    llm_base_url: str = "https://openrouter.ai/api/v1"
    thinking_model: str = "deepseek/deepseek-r1"
    non_thinking_model: str = "openai/gpt-4o-mini"
    data_dir: str = "./data"

    model_config = {"env_file": ".env"}


settings = Settings()
