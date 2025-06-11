let sessionId = localStorage.getItem("session_id");
if (!sessionId) {
  sessionId = crypto.randomUUID();  // Generate unique ID
  localStorage.setItem("session_id", sessionId);
}

const chatForm = document.getElementById("chat-form");
const chatHistory = document.getElementById("chat-history");

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const query = document.getElementById("query").value.trim();
  const image = document.getElementById("image").files[0];
  if (!query && !image) return;

  const formData = new FormData();
  formData.append("session_id", sessionId);
  formData.append("user_query", query);
  if (image) {
    formData.append("image", image);
    const preview = document.createElement("img");
    preview.src = URL.createObjectURL(image);
    preview.alt = "Uploaded";
    preview.className = "uploaded-preview";
    chatHistory.appendChild(preview);
  }

  // Display user message
  if (query) {
    const userMsg = document.createElement("div");
    userMsg.className = "message user-message";
    userMsg.textContent = query;
    chatHistory.appendChild(userMsg);
  }
  
  // Send to backend
  try {
    const res = await fetch("https://friendly-zabaione-cfba40.netlify.app/chat", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();

    // Display assistant message
    const assistantMsg = document.createElement("div");
    assistantMsg.className = "message assistant-message";

    const text = document.createElement("p");
    text.textContent = data.response || "(No response)";
    assistantMsg.appendChild(text);

    // Add product cards if any
    if (data.products && data.products.length > 0) {
      const grid = document.createElement("div");
      grid.className = "products-grid";

      data.products.forEach((p) => {
        const card = document.createElement("div");
        card.className = "product-card";
        card.innerHTML = `
          <img src="${p.image_url}" alt="${p.name}" />
          <h3>${p.name}</h3>
          <p>${p.description}</p>
        `;
        grid.appendChild(card);
      });

      assistantMsg.appendChild(grid);
    }

    chatHistory.appendChild(assistantMsg);
    chatHistory.scrollTop = chatHistory.scrollHeight;
  } catch (err) {
    alert("Error: " + err.message);
  }

  // Clear form
  document.getElementById("query").value = "";
  document.getElementById("image").value = null;
});
