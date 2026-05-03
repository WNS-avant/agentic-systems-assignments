# Python version: 3.14.x
# pip install commands:
#   pip install chromadb
#   pip install sentence-transformers
#   pip install google-generativeai
#
# How to run:
#   1. Set your Gemini API key
#      PowerShell:
#      $env:GEMINI_API_KEY="your_api_key_here"
#
#   2. Run:
#      python hr_policy_rag.py

import os
import chromadb
from google import genai
from sentence_transformers import SentenceTransformer

# --------------------------------------------------
# Global embedding model
# --------------------------------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# --------------------------------------------------
# Gemini setup
# --------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Please set GEMINI_API_KEY as an environment variable.")

client = genai.Client(api_key=GEMINI_API_KEY)
# --------------------------------------------------
# Step 1: HR policy documents
# --------------------------------------------------
POLICY_DOCUMENTS = [
    {
        "id": "leave_policy",
        "text": (
            "Employees are entitled to 18 annual leave days per calendar year. "
            "Up to 6 unused leave days may be carried forward to the next year. "
            "Sick leave of up to 8 days per year may be taken without affecting annual leave balance. "
            "Leave requests longer than 3 consecutive days require manager approval."
        ),
        "metadata": {
            "category": "leave",
            "source": "Leave Policy"
        }
    },
    {
        "id": "wfh_policy",
        "text": (
            "Full-time employees may work from home up to 2 days per week. "
            "Employees must complete at least 3 months of service before becoming eligible. "
            "Work-from-home requests should be submitted one day in advance. "
            "Manager approval is required for every work-from-home request."
        ),
        "metadata": {
            "category": "wfh",
            "source": "Work From Home Policy"
        }
    },
    {
        "id": "appraisal_policy",
        "text": (
            "The annual appraisal cycle is conducted every April. "
            "Employee performance is rated on a 5-point scale. "
            "Salary increments are linked to both individual ratings and company performance. "
            "Employees rated 4 or above are considered for above-average increment revisions."
        ),
        "metadata": {
            "category": "appraisal",
            "source": "Appraisal Policy"
        }
    },
    {
        "id": "conduct_policy",
        "text": (
            "Employees must maintain professional behavior in all workplace interactions. "
            "Confidential company and customer data must not be shared outside authorized channels. "
            "Any conflict of interest must be disclosed to HR immediately. "
            "Violation of data privacy rules may lead to disciplinary action."
        ),
        "metadata": {
            "category": "conduct",
            "source": "Code of Conduct"
        }
    },
]

# --------------------------------------------------
# Step 2: Functions
# --------------------------------------------------
def create_embeddings(texts):
    return model.encode(texts).tolist()


def setup_vector_database():
    client = chromadb.PersistentClient(path="./hr_chromastore")

    existing = [c.name for c in client.list_collections()]
    if "hr_policy_collection" in existing:
        client.delete_collection("hr_policy_collection")

    collection = client.create_collection(
        name="hr_policy_collection",
        embedding_function=None,
        metadata={"hnsw:space": "cosine"}
    )

    return collection


def index_hr_documents(collection):
    ids = [doc["id"] for doc in POLICY_DOCUMENTS]
    texts = [doc["text"] for doc in POLICY_DOCUMENTS]
    metadatas = [doc["metadata"] for doc in POLICY_DOCUMENTS]
    embeddings = create_embeddings(texts)

    collection.upsert(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings
    )


def retrieve_hr_content(collection, query, top_k=3):
    query_embedding = create_embeddings([query])

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    chunks = []
    for i in range(len(results["ids"][0])):
        chunks.append({
            "id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        })

    return chunks


def build_grounded_prompt(query, chunks):
    context = "\n\n".join(
        [f"Source: {c['metadata']['source']}\n{c['text']}" for c in chunks]
    )

    prompt = f"""
You are an HR policy assistant for InnoTech Solutions.

Use only the policy context below to answer the employee's question.

If the answer is not clearly present in the policy context, reply exactly:
"I do not have enough policy information to answer that."

Policy Context:
{context}

Employee Question:
{query}

Answer clearly and briefly.
"""
    return prompt


def generate_answer(query, chunks):
    prompt = build_grounded_prompt(query, chunks)

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        if response.text:
            return response.text.strip()

    except Exception as e:
        if chunks:
            source = chunks[0]["metadata"]["source"]
            text = chunks[0]["text"]
            return (
                f"[Gemini unavailable: {str(e).splitlines()[0]}]\n"
                f"Fallback grounded answer from {source}: {text}"
            )

    return "I do not have enough policy information to answer that."
def answer_with_rag(collection, query, top_k=3):
    print("\n" + "=" * 60)
    print("QUERY:", query)

    chunks = retrieve_hr_content(collection, query, top_k=top_k)

    print("\nRetrieved Chunks:")
    for idx, chunk in enumerate(chunks, start=1):
        print(f"\nRank {idx}")
        print("Source   :", chunk["metadata"]["source"])
        print("Distance :", round(chunk["distance"], 4))
        print("Text     :", chunk["text"][:180] + "...")

    answer = generate_answer(query, chunks)

    print("\nRAG ANSWER:")
    print(answer)

    return answer


# --------------------------------------------------
# Without retrieval
# --------------------------------------------------
def generate_answer_without_retrieval(query):
    prompt = f"""
You are an HR assistant.

Answer the employee question from general knowledge only.
Do not use any company-specific policy context.

Employee Question:
{query}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        if response.text:
            return response.text.strip()

    except Exception:
        return (
            "Generic AI answer (fallback): policies vary by company. "
            "Please check HR for exact details."
        )

    return "No answer generated."
# --------------------------------------------------
# Main execution
# --------------------------------------------------
if __name__ == "__main__":
    collection = setup_vector_database()
    index_hr_documents(collection)

    print("Indexed documents:", collection.count())

    # Step 3: Test with at least 3 employee queries
    queries = [
        "How many days of annual leave am I entitled to per year?",
        "Do I need manager approval before working from home?",
        "When is the appraisal cycle conducted and how is the increment decided?"
    ]

    for q in queries:
        answer_with_rag(collection, q)

    # Step 4: Side-by-side comparison
    comparison_query = "Do I need manager approval before working from home?"

    print("\n" + "=" * 60)
    print("SIDE-BY-SIDE COMPARISON")
    print("=" * 60)

    print("\nWITHOUT RAG:")
    print(generate_answer_without_retrieval(comparison_query))

    print("\nWITH RAG:")
    answer_with_rag(collection, comparison_query)