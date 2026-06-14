from typing import Any

from openai import OpenAI

from .prompts import INSTRUCTIONS, USER_PROMPT_TEMPLATE
from .retrival import search


class RAGBase:
    def __init__(
        self,
        llm_client: Any | None = None,
        instructions: str = INSTRUCTIONS,
        user_prompt_template: str = USER_PROMPT_TEMPLATE,
        model: str = "gpt-5.4-mini",
    ):
        self.llm_client = llm_client or OpenAI()
        self.instructions = instructions
        self.user_prompt_template = user_prompt_template
        self.model = model

    def build_context(self, search_results: list[dict[str, Any]]) -> str:
        lines = []

        for doc in search_results:
            lines.append(f"Filename: {doc['filename']}")
            lines.append(f"Content: {doc['content']}")
            lines.append("")

        return "\n".join(lines).strip()

    def build_prompt(
        self,
        question: str,
        search_results: list[dict[str, Any]],
    ) -> str:
        context = self.build_context(search_results)

        return self.user_prompt_template.format(
            question=question,
            context=context,
        ).strip()

    def generate_response(self, prompt: str):
        messages = [
            {"role": "developer", "content": self.instructions},
            {"role": "user", "content": prompt},
        ]

        return self.llm_client.responses.create(
            model=self.model,
            input=messages,
        )

    def rag(self, query: str, top_k: int = 5) -> dict[str, Any]:
        search_results = search(query=query, top_k=top_k)
        prompt = self.build_prompt(query, search_results)
        response = self.generate_response(prompt)

        return {
            "answer": self._get_response_text(response),
            "usage": self._get_response_usage(response),
            "sources": search_results,
        }

    def _get_response_text(self, response) -> str:
        texts = []

        for output_item in response.output:
            if output_item.type != "message":
                continue

            for content_item in output_item.content:
                if content_item.type == "output_text":
                    texts.append(content_item.text)

        return "\n".join(texts)

    def _get_response_usage(self, response) -> dict[str, int]:
        if response.usage is None:
            return {}

        return {
            "model": self.model,
            "input_tokens": response.usage.input_tokens,
            "cached_tokens": response.usage.input_tokens_details.cached_tokens,
            "output_tokens": response.usage.output_tokens,
            "reasoning_tokens": response.usage.output_tokens_details.reasoning_tokens,
            "total_tokens": response.usage.total_tokens,
        }


def ask_rag(question: str, top_k: int = 5) -> dict[str, Any]:
    assistant = RAGBase()
    return assistant.rag(query=question, top_k=top_k)
