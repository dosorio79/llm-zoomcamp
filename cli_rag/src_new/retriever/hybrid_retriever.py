"""
Takes resuls from the vector retriever and the text retriever and combines them into a single list of results.
"""

class HybridRetriever:
    """
    A class to combine results from a vector retriever and a text retriever.
    """

    def __init__(self, vector_retriever, text_retriever):
        """
        Initialize the HybridRetriever with a vector retriever and a text retriever.

        Args:
            vector_retriever: An instance of a vector retriever.
            text_retriever: An instance of a text retriever.
        """
        self.vector_retriever = vector_retriever
        self.text_retriever = text_retriever

    def search(self, query, top_k=5):
        """
        Retrieve results from both the vector retriever and the text retriever.

        Args:
            query: The search query string.
            top_k: Maximum number of results to return from each retriever.

        Returns:
            A combined list of results from both retrievers.
        """
        vector_results = self.vector_retriever.search(query, top_k)
        text_results = self.text_retriever.search(query, top_k)

        # Combine results and remove duplicates based on unique identifiers (e.g., document ID)
        combined_results = {result['id']: result for result in vector_results + text_results}
        
        # Return the combined results as a list
        return list(combined_results.values())

    def retrieve(self, query, top_k=5):
        """Backward-compatible alias for search."""
        return self.search(query=query, top_k=top_k)
    
    def rrf(self, query, top_k=5, k=60):
        """
        Retrieve results from both the vector retriever and the text retriever using Reciprocal Rank Fusion (RRF).

        Args:
            query: The search query string.
            top_k: Maximum number of results to return from each retriever.
            k: The RRF parameter that controls the influence of rank.

        Returns:
            A combined list of results from both retrievers ranked using RRF.
        """
        vector_results = self.vector_retriever.search(query, top_k)
        text_results = self.text_retriever.search(query, top_k)

        # Combine results and calculate RRF scores
        combined_results = {}
        result_objects = {}
        
        for rank, result in enumerate(vector_results):
            doc_id = result['id']
            combined_results[doc_id] = combined_results.get(doc_id, 0) + 1 / (k + rank + 1)
            result_objects[doc_id] = result
        
        for rank, result in enumerate(text_results):
            doc_id = result['id']
            combined_results[doc_id] = combined_results.get(doc_id, 0) + 1 / (k + rank + 1)
            if doc_id not in result_objects:
                result_objects[doc_id] = result

        # Sort results by RRF score in descending order
        sorted_results = sorted(combined_results.items(), key=lambda item: item[1], reverse=True)

        # Return the sorted results with full objects and RRF scores
        return [{'doc': result_objects[doc_id], 'score': score} for doc_id, score in sorted_results]
