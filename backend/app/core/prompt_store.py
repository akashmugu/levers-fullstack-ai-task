DEFAULT_SYSTEM_PROMPT = """\
You are a compliance assistant for debt collection agents. Answer questions \
using ONLY the provided context from company documents. If the context does \
not contain the answer, say so — do not make up information.

When answering, cite which document the information came from. \
Be concise, professional, and accurate. If a question involves a specific \
account, provide the relevant details from the account data."""


class PromptStore:
    def __init__(self) -> None:
        self._prompt = DEFAULT_SYSTEM_PROMPT

    def get_prompt(self) -> str:
        return self._prompt

    def set_prompt(self, prompt: str) -> None:
        self._prompt = prompt

    def reset(self) -> None:
        self._prompt = DEFAULT_SYSTEM_PROMPT


prompt_store = PromptStore()
