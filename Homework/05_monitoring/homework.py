from dotenv import load_dotenv

load_dotenv()

# Configure OpenTelemetry before importing starter.
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from sqlitespanexplorer import SQLiteSpanExporter

provider = TracerProvider()

provider.add_span_processor(
    SimpleSpanProcessor(
        SQLiteSpanExporter("traces.db")
    )
)

trace.set_tracer_provider(provider)

tracer = trace.get_tracer("llm-zoomcamp")


# Import the course starter components only after OTEL is configured.
from rag_helper import RAGBase
from starter import client, index


def calculate_cost(
    input_tokens: int,
    output_tokens: int,
) -> float:
    """Calculate the approximate LLM call cost in USD."""

    input_price_per_million = 0.15
    output_price_per_million = 0.60

    input_cost = (
        input_tokens / 1_000_000
    ) * input_price_per_million

    output_cost = (
        output_tokens / 1_000_000
    ) * output_price_per_million

    return input_cost + output_cost


class RAGTraced(RAGBase):
    """RAG implementation instrumented with OpenTelemetry spans."""

    def search(self, query: str, num_results: int = 5):
        with tracer.start_as_current_span("search") as span:
            span.set_attribute("query", query)
            span.set_attribute("num_results", num_results)

            results = super().search(
                query=query,
                num_results=num_results,
            )

            span.set_attribute(
                "retrieved_documents",
                len(results),
            )

            return results

    def llm(self, prompt: str):
        with tracer.start_as_current_span("llm") as span:
            span.set_attribute("model", self.model)

            response = super().llm(prompt)

            usage = response.usage

            input_tokens = usage.input_tokens
            output_tokens = usage.output_tokens

            cost = calculate_cost(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )

            span.set_attribute(
                "input_tokens",
                input_tokens,
            )

            span.set_attribute(
                "output_tokens",
                output_tokens,
            )

            span.set_attribute(
                "cost",
                cost,
            )

            return response

    def rag(self, query: str) -> str:
        with tracer.start_as_current_span("rag") as span:
            span.set_attribute("query", query)

            search_results = self.search(query)

            prompt = self.build_prompt(
                query=query,
                search_results=search_results,
            )

            response = self.llm(prompt)

            return response.output_text


def main():
    rag = RAGTraced(
        index=index,
        llm_client=client,
    )

    query = (
        "How does the agentic loop keep calling the model until it stops?"
    )

    answer = rag.rag(query)

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(answer)


if __name__ == "__main__":
    main()