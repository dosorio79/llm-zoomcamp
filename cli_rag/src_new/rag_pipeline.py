"""RAG retrieval pipeline orchestration."""

from typing import Any, Literal

from openai import OpenAI

from .prompts import INSTRUCTIONS, USER_PROMPT_TEMPLATE
from .retriever import (
    BaseRetriever,
    HybridRetriever,
    SearchResult,
    TextRetriever,
    VectorRetriever,
)
from .utils import calculate_openai_price


RetrieverMode = Literal["text", "vector", "hybrid"]


class RAGPipeline:
    """Coordinate retriever selection, prompt building, and generation."""

    def __init__(
        self,
        retriever_mode: RetrieverMode = "text",
        llm_client: Any | None = None,
        instructions: str = INSTRUCTIONS,
        user_prompt_template: str = USER_PROMPT_TEMPLATE,
        model: str = "gpt-5.4-mini",
    ) -> None:
        self.retriever_mode = retriever_mode
        self.retriever = self.build_retriever(retriever_mode)
        self.llm_client = llm_client
        self.instructions = instructions
        self.user_prompt_template = user_prompt_template
        self.model = model

    def build_retriever(self, mode: RetrieverMode) -> BaseRetriever:
        if mode == "text":
            return TextRetriever()

        if mode == "vector":
            return VectorRetriever()

        if mode == "hybrid":
            return HybridRetriever()

        raise ValueError(f"Unknown retriever mode: {mode}")

    def retrieve(self, query: str, top_k: int = 5) -> list[SearchResult]:
        if not query or not query.strip():
            return []

        return self.retriever.search(query=query, top_k=top_k)

    def build_context(self, search_results: list[SearchResult]) -> str:
        lines = []

        for doc in search_results:
            lines.append(f"Filename: {doc['filename']}")
            lines.append(f"Content: {doc['content']}")
            lines.append("")

        return "\n".join(lines).strip()

    def build_prompt(
        self,
        question: str,
        search_results: list[SearchResult],
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

        llm_client = self.llm_client or OpenAI()

        return llm_client.responses.create(
            model=self.model,
            input=messages,
        )

    def run(self, query: str, top_k: int = 5) -> dict[str, Any]:
        search_results = self.retrieve(query=query, top_k=top_k)
        prompt = self.build_prompt(query, search_results)
        response = self.generate_response(prompt)

        usage = self._get_response_usage(response)

        return {
            "answer": self._get_response_text(response),
            "usage": usage,
            "cost": calculate_openai_price(
                model=self.model,
                input_tokens=usage.get("input_tokens", 0),
                output_tokens=usage.get("output_tokens", 0),
            ),
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

def ask_rag(
    question: str,
    top_k: int = 5,
    retriever_mode: RetrieverMode = "text",
) -> dict[str, Any]:
    """Ask the RAG pipeline a question."""
    pipeline = RAGPipeline(retriever_mode=retriever_mode)
    return pipeline.run(query=question, top_k=top_k)
