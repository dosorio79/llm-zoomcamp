from toyaikit.tools import Tools
from .retrieval import search


def get_tools():
    """
    Register and return tools available to the agent.
    """
    agent_tools = Tools()
    agent_tools.add_tool(search)

    return agent_tools
