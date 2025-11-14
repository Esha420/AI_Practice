from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    response_format={"type": "json_object"},
    messages=[
        {"role": "user", "content": "Give me a JSON summary of: Hello world, this is a test."}
    ]
)

print("Raw JSON Response:\n")
print(response.choices[0].message["content"])
