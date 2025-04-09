document.addEventListener("DOMContentLoaded", function () {
  const chatToggle = document.getElementById("chat-toggle");
  const chatbotWidget = document.getElementById("chatbot-widget");
  const closeChat = document.getElementById("close-chat");
  const minimizeChat = document.getElementById("minimize-chat");
  const newChat = document.getElementById("new-chat");
  const chatForm = document.getElementById("chat-form");
  const userInput = document.getElementById("user-input");
  const chatMessages = document.getElementById("chat-messages");
  const sendBtn = document.getElementById("send-btn");
  const modelSelector = document.getElementById("model-selector");

  let conversation = [];
  let currentModel = { provider: "deepseek", model: "deepseek-chat" };

  // Initialize model selector with the current model
  fetch("/api/get_model")
    .then((response) => response.json())
    .then((data) => {
      currentModel = data;
      const selectValue = `${data.provider}:${data.model}`;

      // Just set the value, don't add new options
      if (modelSelector.querySelector(`option[value="${selectValue}"]`)) {
        modelSelector.value = selectValue;
      }
      // If the model isn't in our predefined options, just use the first option

      // Display current model in chat
      if (chatMessages.children.length === 0) {
        addMessage(
          `Using ${data.model_name || `${data.provider} (${data.model})`}`,
          "ai"
        );
      }
    })
    .catch((error) => {
      console.error("Error getting current model:", error);
    });

  // Model selection change
  modelSelector.addEventListener("change", function () {
    const [provider, model] = this.value.split(":");

    // Show typing indicator during model change
    showTypingIndicator();

    fetch("/api/change_model", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        provider: provider,
        model: model,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        removeTypingIndicator();
        if (data.success) {
          currentModel = { provider: data.provider, model: data.model };
          if (data.provider == "deepseek") {
            addMessage(
              `Model changed to ${
                data.model_name || `Deepseek (${data.model})`
              }`,
              "ai"
            );
          } else if (data.provider == "openai") {
            addMessage(
              `Model changed to ${data.model_name || `OpenAI (${data.model})`}`,
              "ai"
            );
          }
        } else {
          addMessage(`Failed to change model: ${data.message}`, "ai");
        }
      })
      .catch((error) => {
        console.error("Error changing model:", error);
        removeTypingIndicator();
        addMessage("Có lỗi khi thay đổi model. Vui lòng thử lại.", "ai");
      });
  });

  // Toggle chat widget
  chatToggle.addEventListener("click", function () {
    chatbotWidget.classList.toggle("active");
    chatToggle.classList.toggle("hidden");

    if (chatbotWidget.classList.contains("active")) {
      loadSavedShapes();
    }
  });

  // Close chat
  closeChat.addEventListener("click", function () {
    chatbotWidget.classList.remove("active");
    chatToggle.classList.remove("hidden");
  });

  // Minimize chat
  minimizeChat.addEventListener("click", function () {
    chatbotWidget.classList.remove("active");
    chatToggle.classList.remove("hidden");
  });

  // New chat
  newChat.addEventListener("click", function () {
    // Clear all messages
    chatMessages.innerHTML = "";

    // Show typing indicator while starting new chat
    showTypingIndicator();

    // Call API to start new chat
    fetch("/api/new_chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}),
    })
      .then((response) => response.json())
      .then((data) => {
        // Remove typing indicator
        removeTypingIndicator();

        // Update conversation history with fresh system prompt
        conversation = data.conversation;

        // Add welcome message
        addMessage(data.message, "ai");
      })
      .catch((error) => {
        console.error("Error:", error);
        removeTypingIndicator();
        addMessage(
          "Xin lỗi, có lỗi xảy ra khi khởi tạo cuộc trò chuyện mới.",
          "ai"
        );
      });
  });

  // Form submission
  chatForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const message = userInput.value.trim();

    if (message) {
      // Add user message
      addMessage(message, "user");
      userInput.value = "";
      sendBtn.disabled = true;

      // Show typing indicator
      showTypingIndicator();

      // Send request to API
      fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: message,
          conversation: conversation,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          // Remove typing indicator
          removeTypingIndicator();

          // Update conversation history
          conversation = data.conversation;

          // Add AI response
          addMessage(data.message, "ai");

          sendBtn.disabled = false;
        })
        .catch((error) => {
          console.error("Error:", error);
          removeTypingIndicator();
          addMessage("Xin lỗi, có lỗi xảy ra khi kết nối với máy chủ.", "ai");
          sendBtn.disabled = false;
        });
    }
  });

  // Enable/disable send button based on input
  userInput.addEventListener("input", function () {
    sendBtn.disabled = this.value.trim() === "";
  });

  // Add message to chat
  function addMessage(text, sender) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message flex space-x-2 ${
      sender === "user" ? "justify-end" : ""
    }`;

    const delay = document.querySelectorAll(".message").length * 0.1;
    messageDiv.style.animationDelay = `${delay}s`;

    if (sender === "ai") {
      messageDiv.innerHTML = `
                <div class="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-100 flex items-center justify-center">
                    <i class="fas fa-robot text-indigo-600 text-xs"></i>
                </div>
                <div class="bg-gray-100 p-3 rounded-lg max-w-[80%]">
                    <p class="text-gray-800 text-sm">${text}</p>
                </div>
            `;
    } else {
      messageDiv.innerHTML = `
                <div class="bg-indigo-600 p-3 rounded-lg max-w-[80%]">
                    <p class="text-white text-sm">${text}</p>
                </div>
                <div class="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-600 flex items-center justify-center">
                    <i class="fas fa-user text-white text-xs"></i>
                </div>
            `;
    }

    chatMessages.appendChild(messageDiv);
    messageDiv.scrollIntoView({ behavior: "smooth" });
  }

  // Show typing indicator
  function showTypingIndicator() {
    const typingDiv = document.createElement("div");
    typingDiv.className = "message flex space-x-2";
    typingDiv.id = "typing-indicator";
    typingDiv.innerHTML = `
            <div class="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-100 flex items-center justify-center">
                <i class="fas fa-robot text-indigo-600 text-xs"></i>
            </div>
            <div class="bg-gray-100 p-2 rounded-lg max-w-[80%]">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;

    chatMessages.appendChild(typingDiv);
    typingDiv.scrollIntoView({ behavior: "smooth" });
  }

  // Remove typing indicator
  function removeTypingIndicator() {
    const typingIndicator = document.getElementById("typing-indicator");
    if (typingIndicator) {
      typingIndicator.remove();
    }
  }

  // Load saved shapes
  function loadSavedShapes() {
    fetch("/api/shapes")
      .then((response) => response.json())
      .then((data) => {
        const savedShapesContainer = document.getElementById("saved-shapes");
        savedShapesContainer.innerHTML = "";

        data.shapes.forEach((shape) => {
          const shapeDiv = document.createElement("div");
          shapeDiv.className =
            "bg-white p-2 rounded border border-gray-200 text-sm";

          const paramsText = Object.entries(shape.parameters)
            .map(([key, value]) => `${key}: ${value}`)
            .join(", ");

          shapeDiv.innerHTML = `
            <div class="flex justify-between items-center">
              <span class="font-medium">${shape.shape_name}</span>
              <span class="text-gray-500 text-xs">${new Date(
                shape.timestamp
              ).toLocaleString()}</span>
            </div>
            <div class="text-gray-600 mt-1">${paramsText}</div>
          `;

          savedShapesContainer.appendChild(shapeDiv);
        });
      })
      .catch((error) => {
        console.error("Error loading saved shapes:", error);
      });
  }

  // Toggle saved shapes visibility
  document
    .getElementById("toggle-saved-shapes")
    .addEventListener("click", function () {
      const savedShapes = document.getElementById("saved-shapes");
      const icon = this.querySelector("i");

      savedShapes.classList.toggle("hidden");
      icon.classList.toggle("fa-chevron-up");
      icon.classList.toggle("fa-chevron-down");

      if (!savedShapes.classList.contains("hidden")) {
        loadSavedShapes();
      }
    });
});
