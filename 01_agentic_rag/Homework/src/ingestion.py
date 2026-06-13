import requests
from typing import List, Any
from minsearch import Index


def load_faq_data(docs_url: str = "https://datatalks.club/faq/json/courses.json", url_prefix: str = "https://datatalks.club/faq/") -> List[Any]:
    """
    Load FAQ data from DataTalks.club courses endpoint.
    
    Fetches the list of courses and their FAQ content from the DataTalks.club
    FAQ JSON API, aggregating all documents into a single list.
    
    Each document contains:
        - id: Unique identifier for the FAQ entry
        - course: Course name (e.g., 'llm-zoomcamp')
        - section: Topic section (e.g., 'General Course-Related Questions')
        - question: The FAQ question
        - answer: The FAQ answer
    
    Args:
        docs_url: URL to the courses JSON endpoint.
        url_prefix: URL prefix for individual course FAQ endpoints.
    
    Returns:
        List[Any]: A list of FAQ documents aggregated from all courses.
    """
    response = requests.get(docs_url)
    response.raise_for_status()
    courses_raw = response.json()
    print(f"Loaded {len(courses_raw)} courses")
    documents: List[Any] = []

    for course in courses_raw:
        course_url = f"{url_prefix}{course['path']}"
        print(f"Fetching: {course_url}")
        course_response = requests.get(course_url)
        course_response.raise_for_status()
        course_content = course_response.json()
        documents.extend(course_content)
        print(f"Added {len(course_content)} documents from {course['course_name']} (course: {course['course']})")
    print(f"Total documents loaded: {len(documents)}")
    return documents


def build_index(documents: List[Any], text_fields: List[str]= ["question", "section", "answer"], keyword_fields: List[str]= ["course"]) -> Any:
    """
    Create and fit an Index with the provided documents.
    
    Args:
        documents: List of documents to fit the index with.
        text_fields: List of field names to use as text fields in the index.
        keyword_fields: List of field names to use as keyword fields in the index.
    
    Returns:
        Any: The fitted Index object.
    """
    print(f"Building index with {len(documents)} documents")
    print(f"Text fields: {text_fields}")
    print(f"Keyword fields: {keyword_fields}")
    index = Index(
        text_fields=text_fields,
        keyword_fields=keyword_fields)
    index.fit(documents)
    print("Index built successfully")
    return index
