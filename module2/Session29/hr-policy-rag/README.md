# HR Policy RAG Assistant

This project builds a simple HR Policy Assistant for InnoTech Solutions using ChromaDB, Sentence Transformers, and Gemini.  
Employee questions are converted into embeddings, matched against HR policy documents, and answered using retrieved policy context instead of guesswork.  
The script also compares normal LLM responses with RAG-grounded responses.

## Run

Install dependencies: `pip install chromadb sentence-transformers google-genai`  
Set your Gemini API key: `set GEMINI_API_KEY=your_api_key` (Windows)  
Run the project: `python hr_policy_rag.py`