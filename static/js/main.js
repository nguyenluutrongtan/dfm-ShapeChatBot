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

  let conversation = [];

  // Toggle chat widget
  chatToggle.addEventListener("click", function () {
    chatbotWidget.classList.toggle("active");
    chatToggle.classList.toggle("hidden");
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

          // If conversation is completed, reset for a new conversation
          if (data.completed) {
            conversation = [];
          }

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
});
