# src/llm/gemini.py
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

class GeminiClient:
    def __init__(self, model_name: str = "google/flan-t5-small"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    def generate(self, prompt: str, max_output_tokens: int = 512) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt")
        output_ids = self.model.generate(
            **inputs,
            max_new_tokens=max_output_tokens,
            do_sample=True,
            temperature=0.7,
        )
        return self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
