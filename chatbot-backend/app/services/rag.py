import os
import json
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import pdfplumber
from docx import Document

from sentence_transformers import SentenceTransformer
import faiss

import openai
from app.core.config import settings
from app.models.file import File
from app.models.message import Message

_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _embedding_model

openai.api_key = settings.OPENAI_API_KEY


async def process_uploaded_file(file_record: File, user_id: int, db: AsyncSession):
    text = extract_text_from_file(file_record.filepath, file_record.file_type)
    chunks = chunk_text(text, chunk_size=settings.CHUNK_SIZE, overlap=settings.CHUNK_OVERLAP)
    embeddings = generate_embeddings(chunks)
    
    index_dir = Path(settings.UPLOAD_DIR) / str(user_id)
    index_path = index_dir / "faiss_index.bin"
    metadata_path = index_dir / "metadata.json"
    
    if index_path.exists():
        index = faiss.read_index(str(index_path))
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
    else:
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        metadata = []
    
    start_id = len(metadata)
    index.add(embeddings)
    
    for i, chunk in enumerate(chunks):
        metadata.append({
            "id": start_id + i,
            "file_id": file_record.id,
            "filename": file_record.filename,
            "text": chunk,
            "chunk_index": i
        })
    
    faiss.write_index(index, str(index_path))
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f)
    
    file_record.index_path = str(metadata_path)
    await db.commit()


def extract_text_from_file(filepath: str, file_type: str) -> str:
    if file_type == "pdf":
        text = ""
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    
    elif file_type == "docx":
        doc = Document(filepath)
        return "\n".join([para.text for para in doc.paragraphs])
    
    elif file_type == "txt":
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    
    return chunks


def generate_embeddings(texts: List[str]) -> np.ndarray:
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings.astype('float32')


async def retrieve_and_query(
    query: str,
    user_id: int,
    file_ids: Optional[List[int]],
    db: AsyncSession
) -> Tuple[str, List[dict]]:
    index_dir = Path(settings.UPLOAD_DIR) / str(user_id)
    index_path = index_dir / "faiss_index.bin"
    metadata_path = index_dir / "metadata.json"
    
    if not index_path.exists():
        return "No documents uploaded yet. Please upload a document first.", []
    
    index = faiss.read_index(str(index_path))
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    if file_ids:
        metadata = [m for m in metadata if m["file_id"] in file_ids]
    
    query_embedding = generate_embeddings([query])
    
    k = min(settings.TOP_K_RETRIEVAL, len(metadata))
    distances, indices = index.search(query_embedding, k)
    
    relevant_chunks = []
    sources = []
    for idx in indices[0]:
        if idx < len(metadata):
            chunk_meta = metadata[idx]
            relevant_chunks.append(chunk_meta["text"])
            sources.append({
                "filename": chunk_meta["filename"],
                "chunk": chunk_meta["chunk_index"],
                "text": chunk_meta["text"][:200] + "..."
            })
    
    context = "\n\n".join(relevant_chunks)
    prompt = f"""Answer the question based on the following context. If the answer is not in the context, say "I don't have enough information to answer that."

Context:
{context}

Question: {query}

Answer:"""
    
    try:
        response = openai.ChatCompletion.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on provided documents."},
                {"role": "user", "content": prompt}
            ],
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.MAX_TOKENS
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"Error querying LLM: {str(e)}"
    
    return answer, sources


async def stream_rag_query(query: str, user_id: int, chat_id: int, db: AsyncSession):
    index_dir = Path(settings.UPLOAD_DIR) / str(user_id)
    index_path = index_dir / "faiss_index.bin"
    metadata_path = index_dir / "metadata.json"
    
    if not index_path.exists():
        yield f"data: {json.dumps({'token': 'No documents uploaded yet.'})}

"
        yield "data: [DONE]

"
        return
    
    index = faiss.read_index(str(index_path))
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    query_embedding = generate_embeddings([query])
    k = min(settings.TOP_K_RETRIEVAL, len(metadata))
    distances, indices = index.search(query_embedding, k)
    
    relevant_chunks = []
    sources = []
    for idx in indices[0]:
        if idx < len(metadata):
            chunk_meta = metadata[idx]
            relevant_chunks.append(chunk_meta["text"])
            sources.append({
                "filename": chunk_meta["filename"],
                "chunk": chunk_meta["chunk_index"]
            })
    
    context = "\n\n".join(relevant_chunks)
    prompt = f"""Answer based on context. If not in context, say "I don't know."

Context:
{context}

Question: {query}

Answer:"""
    
    full_response = ""
    try:
        response = openai.ChatCompletion.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
            stream=True
        )
        
        for chunk in response:
            if chunk.choices[0].delta.get("content"):
                token = chunk.choices[0].delta.content
                full_response += token
                yield f"data: {json.dumps({'token': token})}

"
        
        yield f"data: {json.dumps({'sources': sources})}

"
        yield "data: [DONE]

"
        
        assistant_message = Message(
            chat_id=chat_id,
            role="assistant",
            content=full_response,
            sources=sources
        )
        db.add(assistant_message)
        await db.commit()
        
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}

"
        yield "data: [DONE]

"
