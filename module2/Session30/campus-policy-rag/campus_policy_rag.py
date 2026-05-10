import os
import re
from pathlib import Path

import chromadb
from pypdf import PdfReader
from google import genai

# -----------------------------
# CONFIG
# -----------------------------
PROJECT_DIR = Path(__file__).parent
PDF_DIR = PROJECT_DIR / "policy_documents"
CHROMA_DIR = PROJECT_DIR / "chroma_db"
COLLECTION_NAME = "campus_policies"

CHUNK_SIZE = 140
CHUNK_OVERLAP = 20


# -----------------------------
# GEMINI SETUP
# -----------------------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY not found. Set it in your terminal before running."
    )

client = genai.Client(api_key=GOOGLE_API_KEY)


# -----------------------------
# POLICY TYPE INFERENCE
# -----------------------------
def infer_policy_type(filename: str) -> str:
    name = filename.lower()

    if "hostel" in name:
        return "hostel"
    elif "refund" in name:
        return "refund"
    elif "library" in name:
        return "library"
    elif "withdraw" in name:
        return "withdrawal"

    return "general"


# -----------------------------
# TEXT CLEANING
# -----------------------------
def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# -----------------------------
# PDF LOADING
# -----------------------------
def load_pdfs():
    pages = []

    for pdf_file in PDF_DIR.glob("*.pdf"):
        reader = PdfReader(str(pdf_file))
        print(f"Loaded {len(reader.pages)} pages from: {pdf_file.name}")

        policy_type = infer_policy_type(pdf_file.name)

        for page_num, page in enumerate(reader.pages, start=1):
            raw_text = page.extract_text() or ""
            text = clean_text(raw_text)

            if text:
                pages.append(
                    {
                        "text": text,
                        "source": pdf_file.name,
                        "page": page_num,
                        "policy_type": policy_type,
                    }
                )

    return pages


# -----------------------------
# CHUNKING
# -----------------------------
def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])

        if chunk:
            chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks


# -----------------------------
# EMBEDDING
# -----------------------------
def get_embedding(text: str):
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )

    return response.embeddings[0].values


# -----------------------------
# CHROMADB
# -----------------------------
def get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    return collection


# -----------------------------
# BUILD KNOWLEDGE BASE
# -----------------------------
def build_knowledge_base():
    collection = get_collection()

    if collection.count() > 0:
        print(f"Vector DB ready. Collection: {COLLECTION_NAME}")
        print(f"Existing chunks: {collection.count()}")
        return collection

    pages = load_pdfs()

    all_chunks = []
    all_embeddings = []
    all_ids = []
    all_metadatas = []

    chunk_counter = 0

    for page in pages:
        chunks = chunk_text(page["text"])

        for chunk in chunks:
            chunk_id = f"{page['source']}_{page['page']}_{chunk_counter}"

            embedding = get_embedding(chunk)

            all_chunks.append(chunk)
            all_embeddings.append(embedding)
            all_ids.append(chunk_id)

            all_metadatas.append(
                {
                    "source": page["source"],
                    "page": page["page"],
                    "policy_type": page["policy_type"],
                }
            )

            chunk_counter += 1

    print(f"Total chunks created: {len(all_chunks)}")

    if all_chunks:
        collection.add(
            ids=all_ids,
            documents=all_chunks,
            embeddings=all_embeddings,
            metadatas=all_metadatas,
        )

    print(
        f"Successfully stored {len(all_chunks)} chunks in vector database."
    )

    return collection


# -----------------------------
# RETRIEVAL
# -----------------------------
def retrieve_context(query: str, top_k=3):
    collection = get_collection()

    query_embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    print(f"Retrieved {len(documents)} relevant chunks.")

    return documents, metadatas


# -----------------------------
# PROMPT BUILDING
# -----------------------------
def build_prompt(query: str, contexts):
    context_text = "\n\n".join(contexts)

    prompt = f"""
You are a campus policy assistant.

Answer ONLY using the policy context below.

If the answer is not available in the context, say exactly:
I don't have that information.

Keep the answer simple and student-friendly.

Policy Context:
{context_text}

Student Question:
{query}
"""

    return prompt.strip()


# -----------------------------
# GENERATION
# -----------------------------
def generate_answer(prompt: str, contexts=None):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text.strip()

    except Exception:
        if contexts:
            return (
                "Gemini generation quota unavailable. "
                "Based on retrieved policy context: "
                + contexts[0]
            )

        return "I don't have that information."
# -----------------------------
# END-TO-END QA
# -----------------------------
def answer_question(query: str):
    contexts, metadata = retrieve_context(query)

    prompt = build_prompt(query, contexts)

    answer = generate_answer(prompt, contexts)

    return answer, metadata

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    build_knowledge_base()

    test_queries = [
        "Can I get a refund after dropping a course?",
        "What is the deadline for returning a library book?",
        "Are hostel visitors allowed on weekends?"
    ]

    for query in test_queries:
        print("\n" + "=" * 60)
        print(f"User Query: {query}")

        answer, metadata = answer_question(query)

        print(f"Answer: {answer}")

        print("Sources:")
        for m in metadata:
            print(
                f"  - file={m['source']}, "
                f"page={m['page']}, "
                f"policy={m['policy_type']}"
            )