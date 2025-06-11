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

---

## 🧠 Features

- Chat interface that maintains multi-turn conversation.
- Accepts both text queries and image uploads.
- Returns product recommendations based on query semantics or image similarity.
- Dynamically displays product cards with names, images, and descriptions.
- Tracks conversation using session ID in localStorage.

---


## Implementation Considerations

POST /chat
This endpoint accepts a user query and/or image input and returns a chatbot-generated response along with relevant product recommendations.

Request Parameters
Name	Type	Location	Required	Description
session_id	string	form	Yes	Unique identifier for the user session (used to maintain conversation history).
user_query	string	form	Yes	Text query from the user (ignored if an image is submitted).
image_url	string	form	No	Optional URL to an image for product search.
image	UploadFile	file	No	Optional uploaded image file for product search.

Note: Either user_query or one of image / image_url must be provided.

Behavior
If an image or image_url is provided, the image is used to search for similar products.

The user_query is internally replaced with a fixed prompt to contextualize the response.

If no image is provided, the user_query is used to perform a semantic search.

A prompt is generated combining the user input and search results.

The chatbot generates a response based on the prompt.

The response and filtered product recommendations are returned.

Response
Returns a JSON object with:

Field	    Type	  Description
response	string	LLM-generated reply to the user’s query.
products	list	  List of product dictionaries relevant to the conversation context.

Each product in products contains fields like name, image_url, description, etc., depending on the structure returned by the search_products function.

Example Request (Form Data)
```makefile
POST /chat
Content-Type: multipart/form-data
session_id=abc123
user_query=Show me red sneakers
image=<uploaded file>
```
Example Response
```json
{
  "response": "Here are some great red sneakers you might like.",
  "products": [
    {
      "name": "Red Classic Sneaker",
      "image_url": "https://example.com/sneaker1.jpg",
      "description": "Stylish and comfortable."
    },
    ...
  ]
}
```

---
