from toyaikit.tools import Tools

from .rag_pipeline import RetrieverMode, RAGPipeline
from .retrieval import SearchResult


def get_tools(
    default_retriever_mode: RetrieverMode = "text",
    default_rerank: bool = False,
):
    """
    Register and return tools available to the agent.
    """
    def search(
        query: str,
        top_k: int = 5,
        retriever_mode: RetrieverMode = default_retriever_mode,
        rerank: bool = default_rerank,
    ) -> list[SearchResult]:
        """
        Search documents using text, vector, or hybrid retrieval.
        Set rerank to true to apply cross-encoder reranking after retrieval.
        """
        pipeline = RAGPipeline(retriever_mode=retriever_mode, rerank=rerank)
        return pipeline.retrieve(query=query, top_k=top_k)

    agent_tools = Tools()
    agent_tools.add_tool(search)

    return agent_tools
