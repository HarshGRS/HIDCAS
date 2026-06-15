import faiss
import numpy as np
import os
import json
import re
from dotenv import load_dotenv
from groq import Groq
from services.chunking_service import chunk_text
from services.embedding_service import get_embedding

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

vector_stores = {}

class VectorStore:
    def __init__(self, dimension=384):
        self.index = faiss.IndexFlatL2(dimension)
        self.text_chunks = []

    def add(self, embedding, text):
        vector = np.array([embedding]).astype("float32")
        self.index.add(vector)
        self.text_chunks.append(text)

    def search(self, embedding, top_k=3):
        vector = np.array([embedding]).astype("float32")
        distances, indices = self.index.search(vector, top_k)
        results = []
        for idx in indices[0]:
            if idx < len(self.text_chunks):
                results.append(self.text_chunks[idx])
        return results


def build_index(document_id: int, text: str):
    store = VectorStore()
    chunks = chunk_text(text)
    for chunk in chunks:
        embedding = get_embedding(chunk)
        store.add(embedding, chunk)
    vector_stores[document_id] = store


def get_or_rebuild_index(document_id: int, db):
    if document_id not in vector_stores:
        from models import Document
        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc and doc.content:
            build_index(document_id, doc.content)
    return vector_stores.get(document_id)


def query_document(document_id: int, question: str):
    store = vector_stores.get(document_id)
    if not store:
        return []
    query_embedding = get_embedding(question)
    return store.search(query_embedding)


def ask_llm(context: str, question: str) -> str:
    prompt = f"""You are a helpful assistant. Use the context below to answer the question.
Only use information from the context. Be concise and direct.

Context:
{context}

Question: {question}

Answer:"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def extract_project_info(text: str) -> dict:
    prompt = """Extract the following information from the document text below.
Return ONLY a valid JSON object with these exact keys:
{
  "company_name": "",
  "project_name": "",
  "location": "",
  "year": "",
  "budget": "",
  "loan_amount": ""
}

Rules:
- company_name: organization/firm/company jo project kar rahi hai
- project_name: project ka naam
- location: city/state/district jahan project hai
- year: project ka year
- budget: total project cost ya total budget
- loan_amount: loan/finance ki amount
- Agar koi field document mein nahi mili toh empty string "" rakho
- Sirf JSON return karo, koi explanation nahi

Document:
""" + text[:4000]

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content.strip()

    try:
        data = json.loads(raw)
    except:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
            except:
                data = {}
        else:
            data = {}

    # Ensure all keys exist
    default_keys = ["company_name", "project_name", "location", "year", "budget", "loan_amount"]
    for key in default_keys:
        if key not in data:
            data[key] = ""

    return data