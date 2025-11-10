from transformers import pipeline

# Load a pretrained model for sentiment analysis
nlp = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Test input
text = "I love learning about Generative AI with Hugging Face!"

# Run the model
result = nlp(text)
print(result)

