from app.core.prompt_store import DEFAULT_SYSTEM_PROMPT, PromptStore


class TestPromptStore:
    def test_default_prompt(self, prompt_store: PromptStore) -> None:
        assert prompt_store.get_prompt() == DEFAULT_SYSTEM_PROMPT

    def test_set_prompt(self, prompt_store: PromptStore) -> None:
        prompt_store.set_prompt("Custom prompt")
        assert prompt_store.get_prompt() == "Custom prompt"

    def test_reset_prompt(self, prompt_store: PromptStore) -> None:
        prompt_store.set_prompt("Something else")
        prompt_store.reset()
        assert prompt_store.get_prompt() == DEFAULT_SYSTEM_PROMPT
