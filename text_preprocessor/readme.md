
# Text Preprocessing Pipeline for RAG System

This repository contains a modular text preprocessing pipeline used to prepare raw data for **Retrieval-Augmented Generation (RAG)** systems.  
The goal is to clean, chunk, and format documents into a structured JSONL format suitable for embedding generation and vector database ingestion.

---
##  Overview

The preprocessing pipeline consists of four main scripts:

| Script | Purpose |
|--------|----------|
| **data_cleaning.py** | Cleans and normalizes raw text (HTML removal, lowercasing, stopword removal, etc.) |
| **data_chunking.py** | Splits cleaned text into overlapping sentence-based chunks |
| **format_for_embeddings.py** | Converts chunked text into JSONL format with IDs and metadata for embeddings |
| **preprocess.py** | All-in-one automation that performs cleaning, chunking, and formatting across multiple files |

---
## 1. `data_cleaning.py`
## **Purpose**
Removes noise and normalizes text for better downstream processing.

### **Features**
- Removes HTML tags using BeautifulSoup  
- Removes special characters, symbols, and extra whitespace  
- Converts text to lowercase  
- Removes common stopwords (via NLTK)  
- Handles missing or null text entries gracefully 
--- 

## 2.  `data_chunking.py`
## **Purpose**
- Splits cleaned text into manageable, overlapping chunks to preserve semantic continuity during embedding.

### How It Works
- Uses spaCy for sentence segmentation.
- Uses tiktoken to count tokens accurately.
- Creates overlapping context windows to avoid information loss between chunks.

### Key Parameters
- max_tokens: Maximum tokens per chunk (default 800)
- overlap: Number of overlapping tokens between chunks (default 100)

## 2. `format_for_embeddings.py`
### Purpose
- Converts chunked JSON data into JSONL format, which can be easily consumed by embedding models or vector databases.

### How It Works
- Each chunk is written as one JSON line.
- Includes metadata like source filename and chunk index.
- Adds unique id for each record.

## 3. `preprocess.py`
### Purpose
- A full automation script that combines the cleaning, chunking, and formatting steps into one streamlined process.

### How It Works
- Reads all supported files from an input folder (.txt, .pdf, .docx, .json).
- Cleans the text using HTML stripping, regex cleanup, and stopword removal.
- Splits text into overlapping chunks based on token length.
- Saves the final structured output in .jsonl format.

## Data Flow Summary

| Step | Script | Input | Output |
|------|---------|--------|---------|
| 1 | `data_cleaning.py` | raw_data.txt | cleaned_data.json |
| 2 | `data_chunking.py` | cleaned_data.json | chunked_data.json |
| 3 | `format_for_embeddings.py` | chunked_data.json | embeddings_ready.jsonl |
| 4 | `preprocess.py` | raw_data.txt | processed.jsonl |


