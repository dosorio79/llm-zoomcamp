from prompts import INSTRUCTIONS, USER_PROMPT_TEMPLATE
from typing import Any

class RAGBase:
    def __init__(self, 
                 index: Any, 
                 llm_client: Any, 
                 instructions: str = INSTRUCTIONS,
                 user_prompt_template: str = USER_PROMPT_TEMPLATE,
                 model: str = "gpt-5.4-mini"):
        """
        Initialize the RAG helper.

        Args:
            index (Any): The search index object.
            llm_client (Any): The LLM client object.
            instructions (str): System instructions for the LLM.
            user_prompt_template (str): Template for user prompts.
            model (str): The model name. Default is "gpt-5.4-mini".
        """
        print("[INIT] Initializing RAGBase")
        self.index = index
        self.llm_client = llm_client
        self.instructions = instructions
        self.user_prompt_template = user_prompt_template
        self.model = model
        print(f"[INIT] RAGBase initialized with model: {model}")

    def search(self, query: str, num_results: int = 5, boost_dict: dict | None = None, filter_dict: dict | None = None) -> list:
        """
        Search the index for a given query.

        Args:
            query (str): The search query.
            num_results (int): The number of results to return. Default is 5.
            boost_dict (dict): A dictionary of fields to boost in the search. Default is None.
            filter_dict (dict): A dictionary of filters to apply to the search. Default is None.

        Returns:
            list: A list of search results.
        """
        print(f"[SEARCH] Query: {query}, Num Results: {num_results}, Boost: {boost_dict}, Filter: {filter_dict}")
        results = self.index.search(
            query,
            boost_dict=boost_dict,
            filter_dict=filter_dict,
            num_results=num_results
        )
        print(f"[SEARCH] Found {len(results)} results")
        return results

    def build_context(self, search_results: list) -> str:
        """
        Build a context string from the search results.

        Args:
            search_results (list): A list of search results.

        Returns:
            str: A formatted context string for the LLM.
        """
        print(f"[BUILD_CONTEXT] Building context from {len(search_results)} search results")
        lines = []

        for doc in search_results:
            lines.append(doc["filename"])
            lines.append("Content: " + doc["content"])
            lines.append("")

        context = "\n".join(lines).strip()
        print(f"[BUILD_CONTEXT] Context built with length: {len(context)}")
        return context

    def build_prompt(self, question: str, search_results: list) -> str:
        """
        Build a prompt from a question and search results.

        Args:
            question (str): The user's question.
            search_results (list): A list of search results.

        Returns:
            str: The formatted prompt for the LLM.
        """
        context = self.build_context(search_results)
        return self.user_prompt_template.format(question=question, context=context).strip()

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response from the LLM for the given prompt.

        Args:
            prompt (str): The user prompt.

        Returns:
            str: The generated response text from the LLM.
        """
        messages = [
            {"role": "developer", "content": self.instructions},
            {"role": "user", "content": prompt},
        ]

        return self.llm_client.responses.create(
            model=self.model,
            input=messages,
        )

    def rag(self, query: str) -> tuple[str, dict]:
        """
        Execute the RAG pipeline: search, build prompt, and generate response.

        Args:
            query (str): The user's query.

        Returns:
            tuple[str, dict]: The generated response from the LLM and usage data.
        """
        search_results = self.search(query)
        prompt = self.build_prompt(query, search_results)

        response = self.generate_response(prompt)

        answer = self._get_response_text(response)
        usage = self._get_response_usage(response)

        return answer, usage

    def _get_response_text(self, response) -> str:
        """
        Extract text output from an OpenAI Responses API response.
        """
        texts = []

        for output_item in response.output:
            if output_item.type != "message":
                continue

            for content_item in output_item.content:
                if content_item.type == "output_text":
                    texts.append(content_item.text)

        return "\n".join(texts)

    def _get_response_usage(self, response) -> dict:
        """
        Extract token usage from an OpenAI Responses API response.
        """
        if response.usage is None:
            return {}

        return {
            "input_tokens": response.usage.input_tokens,
            "cached_tokens": response.usage.input_tokens_details.cached_tokens,
            "output_tokens": response.usage.output_tokens,
            "reasoning_tokens": response.usage.output_tokens_details.reasoning_tokens,
            "total_tokens": response.usage.total_tokens,
        }