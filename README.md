# 🛍️ AI Commerce Chat Assistant

A lightweight AI-powered shopping assistant that supports multimodal queries (text and images) for product recommendations. It maintains conversational history, handles image uploads, and integrates product search using vector similarity.\
My primary focus throughout the project was optimizing for efficiency and minimizing latency in both model inference and response delivery.

---

## 🔧 Tech Stack

### 🔙 Backend
- **FastAPI** – Lightweight Python web framework for building APIs.
- **SentenceTransformers** – For encoding user queries and product texts.
- **FAISS** – Efficient similarity search on vector embeddings.
- **CLIP (via HuggingFace)** – Multimodal model to handle image-based queries.
- **Pillow** – For image preprocessing.
- **Uvicorn** – ASGI server for running FastAPI.
- **dotenv** – To manage environment variables securely.

### 🌐 Frontend
- **Vanilla JS + HTML/CSS** – Simple form-based UI for user interaction.
- **Fetch API** – Sends `FormData` to the backend with support for file uploads.
- **LocalStorage** – Maintains session ID across page reloads.

### 🚀 Hosting
- **GitHub Pages** – Hosts static HTML/CSS/JS frontend.

---

## 🧠 Features

- Chat interface that maintains multi-turn conversation.
- Accepts both text queries and image uploads.
- Returns product recommendations based on query semantics or image similarity.
- Dynamically displays product cards with names, images, and descriptions.
- Tracks conversation using session ID in localStorage.

---
