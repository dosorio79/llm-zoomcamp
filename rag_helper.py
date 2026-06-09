from prompts import INSTRUCTIONS, USER_PROMPT_TEMPLATE
from typing import Any

class RAGBase:
    def __init__(self, index: Any, 
                 llm_client: Any, 
                 instructions: str = INSTRUCTIONS,
                 user_prompt_template: str = USER_PROMPT_TEMPLATE,
                 course: str = "llm-zoomcamp",
                 model: str = "gpt-5.4-mini"):
        """
        Initialize the RAG helper.

        Args:
            index (Any): The search index object.
            llm_client (Any): The LLM client object.
            instructions (str): System instructions for the LLM.
            user_prompt_template (str): Template for user prompts.
            course (str): The course name. Default is "llm-zoomcamp".
            model (str): The model name. Default is "gpt-5.4-mini".
        """
        print("[INIT] Initializing RAGBase")
        self.index = index
        self.llm_client = llm_client
        self.instructions = instructions
        self.user_prompt_template = user_prompt_template
        self.course = course
        self.model = model
        print(f"[INIT] RAGBase initialized with model: {model}")

    def search(self, query: str, num_results: int = 5) -> list:
        """
        Search the index for a given query.

        Args:
            query (str): The search query.
            num_results (int): The number of results to return. Default is 5.

        Returns:
            list: A list of search results.
        """
        print(f"[SEARCH] Query: {query}, Course: {self.course}, Num Results: {num_results}")
        results = self.index.search(
            query,
            boost_dict={"question": 3.0, "section": 0.5, "answer": 1.0},
            filter_dict={"course": self.course},
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
            lines.append(doc["section"])
            lines.append("Q: " + doc["question"])
            lines.append("A: " + doc["answer"])
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
        ).output_text
        
    def rag(self, query: str) -> str:
        """
        Execute the RAG pipeline: search, build prompt, and generate response.

        Args:
            query (str): The user's query.

        Returns:
            str: The generated response from the LLM.
        """
        search_results = self.search(query)
        prompt = self.build_prompt(query, search_results)
        return self.generate_response(prompt)