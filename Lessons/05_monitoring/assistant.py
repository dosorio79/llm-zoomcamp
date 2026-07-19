import sys

from dotenv import load_dotenv
load_dotenv()

sys.path.append("../01_agentic_rag")
from ingestion import load_faq_data, build_index
from metrics import RAGWithMetrics
from openai import OpenAI

def create_assistant():
    load_dotenv()

    documents = load_faq_data()
    index = build_index(documents)

    return RAGWithMetrics(
        index=index,
        llm_client=OpenAI(),
    )
    
if __name__ == "__main__":
    assistant = create_assistant()

    query = "How do I join the course?"
    if len(sys.argv) > 1:
        query = sys.argv[1]

    answer = assistant.rag(query)
    print(answer)