import ollama


class OllamaChatClient:
    """Generic reusable client for interacting with a local chat model service."""

    def __init__(self, model_name="llama3.2"):
        self.model_name = model_name
        self.history = []

    def send(self, prompt):
        """Send a prompt to the model and return the assistant's reply text."""
        if prompt is None or not str(prompt).strip():
            raise ValueError("Prompt cannot be empty.")

        user_message = {"role": "user", "content": str(prompt).strip()}
        self.history.append(user_message)

        try:
            response = ollama.chat(model=self.model_name, messages=self.history)
            content = self._extract_content(response)
        except Exception as error:
            # Roll back the user message so history only holds complete exchanges.
            self.history.pop()
            raise RuntimeError(f"AI service request failed: {error}") from error

        self.history.append({"role": "assistant", "content": content})
        return content

    def _extract_content(self, response):
        """Pull the reply text out of a dict-style or object-style response."""
        if isinstance(response, dict):
            message = response.get("message")
        else:
            message = getattr(response, "message", None)

        if isinstance(message, dict):
            content = message.get("content")
        else:
            content = getattr(message, "content", None)

        if not isinstance(content, str) or not content.strip():
            raise ValueError("Response did not include usable assistant content.")

        return content

    def reset(self):
        self.history = []

    def message_count(self):
        return len(self.history)

    def get_transcript(self):
        return [message.copy() for message in self.history]