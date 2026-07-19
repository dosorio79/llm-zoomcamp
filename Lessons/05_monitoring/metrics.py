import time
from dataclasses import dataclass, field
from datetime import datetime
import sys
sys.path.append("../01_agentic_rag")
from rag_helper import RAGBase
from utils import calculate_openai_price

@dataclass
class LLMCallRecord:
    model: str
    prompt: str
    instructions: str
    answer: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    response_time: float
    cost: float
    timestamp: datetime = field(default_factory=datetime.now)
    
class RAGWithMetrics(RAGBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_call: LLMCallRecord = None

    def llm(self, prompt):
        start_time = time.time()
        response = self._call_llm(prompt)
        response_time = time.time() - start_time
        self._log_response(prompt, response, response_time)
        return response.output_text
    
        def _call_llm(self, prompt):
            input_messages = [
                {"role": "developer", "content": self.instructions},
                {"role": "user", "content": prompt}
            ]
            response = self.llm_client.responses.create(
                model=self.model,
                input=input_messages
            )
            return response
    
        