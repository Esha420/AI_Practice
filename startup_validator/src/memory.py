# src/memory.py

memory_store = {}

def remember(idea, key, value):
    if idea not in memory_store:
        memory_store[idea] = {}
    memory_store[idea][key] = value

def recall(idea):
    return memory_store.get(idea, {})
