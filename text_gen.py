from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")

prompt = "Artificial Intelligence will change the future because"
output = generator(prompt, max_length=50, num_return_sequences=1)

print(output[0]['generated_text'])
