# backend/services/nlp_service.py
from transformers import T5Tokenizer, T5ForConditionalGeneration
from dotenv import load_dotenv
import os
import sys
import torch

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

load_dotenv()


class NLPService:
    def __init__(self):
        self.device = torch.device(
            "mps" if torch.backends.mps.is_available() else "cpu"
        )
        print(f"Using device: {self.device}")

        self.api_key = os.getenv("OPENAI_API_KEY") #TODO openai? never implemented it or got the api key. thought we're using flant5 from huggingface? whats the differnce
        self.tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
        self.model = T5ForConditionalGeneration.from_pretrained(
            "google/flan-t5-base"
        ).to(self.device)

    def generate_response(self, query, context):
        input_text = f"Question: {query}\nContext: {context}\nAnswer:"
        input_ids = self.tokenizer.encode(input_text, return_tensors="pt").to(
            self.device
        )
        outputs = self.model.generate(
            input_ids, max_length=150, num_beams=5, early_stopping=True
        )
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        return response
