import json
import pickle
import faiss
from sentence_transformers import SentenceTransformer
import requests
import os
from typing import Dict, List
from PIL import Image
from io import BytesIO
import torch
from transformers import CLIPProcessor, CLIPModel

# Load env vars for API key etc.
from dotenv import load_dotenv
load_dotenv()

from fastapi import APIRouter, File, UploadFile, Form
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    query: str

# Paths
CATALOG_PATH = "data/catalog.json"
TEXT_INDEX_PATH = "data/faiss_text.index"
IMAGE_INDEX_PATH = "data/faiss_image.index"
PRODUCTS_PICKLE = "data/products.pkl"

session_histories: Dict[str, List[Dict[str, str]]] = {}

# Load product metadata
with open(PRODUCTS_PICKLE, "rb") as f:
    products = pickle.load(f)

# Load FAISS index
text_index = faiss.read_index(TEXT_INDEX_PATH)
image_index = faiss.read_index(IMAGE_INDEX_PATH)

# Load embedding model
text_model = SentenceTransformer("all-MiniLM-L6-v2")
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Groq API config
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


async def search_products(query, top_k=5, typ='text'):
    # Search index
    if typ == 'text':
      # Embed query
      query_emb = text_model.encode([query])
      D, I = text_index.search(query_emb, top_k)
    else:
      try:
        if isinstance(query, str):
          # Load image from URL
          response = requests.get(query)
          response.raise_for_status()
          image_file = response.content
        else:
          image_file = await query.read()
        image = Image.open(BytesIO(image_file)).convert("RGB")

        # Compute image embedding
        inputs = clip_processor(images=image, return_tensors="pt")
        with torch.no_grad():
            image_emb = clip_model.get_image_features(**inputs).cpu().numpy()

        # Search FAISS image index
        D, I = image_index.search(image_emb, top_k)
      except Exception as e:
        print(f"❌ Image search failed: {e}")
        return []
    # Get product info for top results
    results = [products[i] for i in I[0]]
    return results


def generate_prompt(session_id, query, search_results):
    product_snippets = "\n".join(
        [f"- {p['name']}: {p['description']}, category: {p['category']}, price: {p['price']}" for p in search_results]
    )
    if len(session_histories) >= 100:
        session_histories = {}
    prompt = (
        f"""You are an AI assistant helping a user find products.
        Conversation summary so far:
          {session_histories[session_id] if session_id in session_histories else "(No prior summary)"}
        User query: {query}
        Here are some relevant products:\n{product_snippets}
        Answer the user's question using the product info above, it may be that there is no exact product in which case you can recommend related products.
        
        1. Reply to the user's message, using the relevant products using exact product names.
        2. Update the summary of the conversation so far to include this message and your response. Keep this Concise.

        Respond in this format:
        [Response]: <your reply>
        [Updated Summary]: <updated summary>
        including the square brackets"""
    )
    return prompt


def get_llm_response(session_id, prompt: str):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": 'llama3-70b-8192',
        "messages": [{'role': 'user', 'content': prompt}],
    }

    response = requests.post(GROQ_API_URL, json=payload, headers=headers)
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]

    idx = content.find("[Updated Summary]:")
    if idx != -1:
      session_histories[session_id] = content[idx+len("[Updated Summary]:"):]
      content = content[:idx]
    idx = content.find("[Response]:")
    if idx != -1:
      content = content[idx+len("[Response]:"):]
    return content

@router.post("/chat")
async def chat_endpoint(session_id: str = Form(...), user_query: str = Form(...), image_url: str = Form(None), image: UploadFile = File(None)):
    if image is not None or image_url is not None:
      search_results = await search_products(image if image is not None else image_url, typ='image')
      user_query = "{Image was submitted to find similar products, respond with recommendation for the relevant products}"
    else:
      search_results = await search_products(user_query)
    prompt = generate_prompt(session_id, user_query, search_results)
    response = get_llm_response(session_id, prompt)
    return {"response": response, "products": [x for x in search_results if x['name'] in response]}
