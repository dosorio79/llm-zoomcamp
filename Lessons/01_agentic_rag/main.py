from openai import OpenAI
from dotenv import load_dotenv

try:
    from .ingestion import load_faq_data, build_index
    from .rag_helper import RAGBase
except ImportError:
    from ingestion import load_faq_data, build_index
    from rag_helper import RAGBase

load_dotenv()

def main():
    # Load data and build index
    documents = load_faq_data()
    index = build_index(documents)
    
    # Initialize RAG helper with the index and OpenAI client
    openai_client = OpenAI()

    assistant = RAGBase(
        index=index,
        llm_client=openai_client,
    )
    # Get user question and generate response
    question = input("Please enter your question: ")   
    answer = assistant.rag(question)
    print(answer)

if __name__ == "__main__":
    main()
