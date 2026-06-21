from toyaikit.tools import Tools

from .rag_pipeline import RetrieverMode, RAGPipeline


def search(
    query: str,
    top_k: int = 5,
    retriever_mode: RetrieverMode = "text",
) -> list[dict]:
    """
    Search documents using the selected retriever mode.
    """
    pipeline = RAGPipeline(retriever_mode=retriever_mode)
    return pipeline.retrieve(query=query, top_k=top_k)


def get_tools():
    """
    Register and return tools available to the agent.
    """
    agent_tools = Tools()
    agent_tools.add_tool(search)

    return agent_tools
