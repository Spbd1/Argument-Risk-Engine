class LLMClient:
    def classify(self, prompt: str) -> dict[str, str]:
        return {"provider": "deterministic", "response": "LLM providers are optional in the MVP."}
