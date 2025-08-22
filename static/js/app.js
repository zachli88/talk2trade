// Global variables
let currentConversationId = "default";
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

// Initialize the app
document.addEventListener("DOMContentLoaded", function () {
  initializeApp();
});

function initializeApp() {
  // Load existing conversations
  loadConversations();

  // Add event listeners
  document
    .getElementById("messageInput")
    .addEventListener("keydown", handleKeyDown);

  // Focus on input
  document.getElementById("messageInput").focus();
}

// Handle Enter key in textarea
function handleKeyDown(event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
}

// Auto-resize textarea
function autoResize(textarea) {
  textarea.style.height = "auto";
  textarea.style.height = Math.min(textarea.scrollHeight, 120) + "px";
}

// Send text message
async function sendMessage() {
  const messageInput = document.getElementById("messageInput");
  const message = messageInput.value.trim();

  if (!message) return;

  // Check for special commands
  if (message.toLowerCase() === "/markets") {
    addMessageToChat("user", message);
    messageInput.value = "";
    messageInput.style.height = "auto";
    await displayMarketData();
    return;
  }

  if (message.toLowerCase() === "/categories") {
    addMessageToChat("user", message);
    messageInput.value = "";
    messageInput.style.height = "auto";
    await displayEventCategories();
    return;
  }

  // Add user message to chat
  addMessageToChat("user", message);

  // Clear input and reset height
  messageInput.value = "";
  messageInput.style.height = "auto";

  // Show typing indicator
  showTypingIndicator();

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: message,
        conversation_id: currentConversationId,
        refresh_markets: true, // Always get fresh market data for trading queries
      }),
    });

    const data = await response.json();

    // Hide typing indicator
    hideTypingIndicator();

    // Add assistant response to chat
    addMessageToChat("assistant", data.response);

    // Update conversation history
    updateConversationHistory();
  } catch (error) {
    console.error("Error sending message:", error);
    hideTypingIndicator();
    addMessageToChat(
      "assistant",
      "Sorry, I encountered an error. Please try again."
    );
  }
}

// Add message to chat interface
function addMessageToChat(role, content) {
  const chatContainer = document.getElementById("chatContainer");
  const welcomeMessage = document.getElementById("welcomeMessage");

  // Hide welcome message if it's the first message
  if (welcomeMessage && welcomeMessage.style.display !== "none") {
    welcomeMessage.style.display = "none";
  }

  // Create message element
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${role}`;

  const messageContent = document.createElement("div");
  messageContent.className = "message-content";
  messageContent.textContent = content;

  const messageTime = document.createElement("div");
  messageTime.className = "message-time";
  messageTime.textContent = new Date().toLocaleTimeString();

  messageDiv.appendChild(messageContent);
  messageDiv.appendChild(messageTime);

  // Add to chat container
  chatContainer.appendChild(messageDiv);

  // Scroll to bottom
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Show typing indicator
function showTypingIndicator() {
  const chatContainer = document.getElementById("chatContainer");

  const typingDiv = document.createElement("div");
  typingDiv.className = "message assistant";
  typingDiv.id = "typingIndicator";

  const typingContent = document.createElement("div");
  typingContent.className = "message-content";
  typingContent.innerHTML =
    '<div class="typing-dots"><span></span><span></span><span></span></div>';

  typingDiv.appendChild(typingContent);
  chatContainer.appendChild(typingDiv);

  chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Hide typing indicator
function hideTypingIndicator() {
  const typingIndicator = document.getElementById("typingIndicator");
  if (typingIndicator) {
    typingIndicator.remove();
  }
}

// Audio recording functions
function toggleAudioRecording() {
  if (isRecording) {
    stopAudioRecording();
  } else {
    startAudioRecording();
  }
}

async function startAudioRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
      await sendAudioMessage(audioBlob);

      // Stop all tracks
      stream.getTracks().forEach((track) => track.stop());
    };

    mediaRecorder.start();
    isRecording = true;

    // Update UI
    document.getElementById("audioRecording").style.display = "flex";
    document.getElementById("audioIcon").className = "fas fa-stop";
    document.getElementById("audioBtn").style.color = "#dc2626";
  } catch (error) {
    console.error("Error starting audio recording:", error);
    alert("Unable to access microphone. Please check permissions.");
  }
}

function stopAudioRecording() {
  if (mediaRecorder && isRecording) {
    mediaRecorder.stop();
    isRecording = false;

    // Update UI
    document.getElementById("audioRecording").style.display = "none";
    document.getElementById("audioIcon").className = "fas fa-microphone";
    document.getElementById("audioBtn").style.color = "#6e6e80";
  }
}

// Send audio message
async function sendAudioMessage(audioBlob) {
  // Show audio message in chat

  // Show typing indicator
  showTypingIndicator();

  try {
    const formData = new FormData();
    formData.append("audio", audioBlob, "recording.wav");
    formData.append("conversation_id", currentConversationId);

    const response = await fetch("/api/audio", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    // Hide typing indicator
    hideTypingIndicator();
    addMessageToChat("user", data.transcribed_text);
    // Add assistant response to chat
    addMessageToChat("assistant", data.response);

    // Update conversation history
    updateConversationHistory();
  } catch (error) {
    console.error("Error sending audio:", error);
    hideTypingIndicator();
    addMessageToChat(
      "assistant",
      "Sorry, I encountered an error processing your audio. Please try again."
    );
  }
}

// Start new chat
function startNewChat() {
  // Generate new conversation ID
  currentConversationId = "chat_" + Date.now();

  // Clear chat container
  const chatContainer = document.getElementById("chatContainer");
  chatContainer.innerHTML = "";

  // Show welcome message
  const welcomeMessage = document.getElementById("welcomeMessage");
  if (welcomeMessage) {
    welcomeMessage.style.display = "block";
  }

  // Update conversation history
  updateConversationHistory();

  // Focus on input
  document.getElementById("messageInput").focus();
}

// Load conversations
async function loadConversations() {
  try {
    const response = await fetch(`/api/conversations/${currentConversationId}`);
    const conversations = await response.json();

    if (conversations.length > 0) {
      // Hide welcome message
      const welcomeMessage = document.getElementById("welcomeMessage");
      if (welcomeMessage) {
        welcomeMessage.style.display = "none";
      }

      // Load messages
      conversations.forEach((msg) => {
        addMessageToChat(msg.role, msg.content);
      });
    }
  } catch (error) {
    console.error("Error loading conversations:", error);
  }
}

// Update conversation history in sidebar
function updateConversationHistory() {
  // This would typically update the sidebar with conversation history
  // For now, we'll just log it
  console.log("Conversation updated:", currentConversationId);
}

// Refresh market data
async function refreshMarketData() {
  try {
    const response = await fetch("/api/markets/refresh", {
      method: "POST",
    });

    const data = await response.json();

    if (data.success) {
      console.log("Market data refreshed:", data.message);
      // Optionally show a success message to the user
      showMarketStatus();
    } else {
      console.error("Failed to refresh market data:", data.message);
    }
  } catch (error) {
    console.error("Error refreshing market data:", error);
  }
}

// Show market status
async function showMarketStatus() {
  try {
    const response = await fetch("/api/markets/status");
    const data = await response.json();

    console.log("Market Status:", data);

    // You can display this information in the UI if desired
    // For now, we'll just log it to the console
  } catch (error) {
    console.error("Error getting market status:", error);
  }
}

// Display market data in chat
async function displayMarketData() {
  try {
    const response = await fetch("/api/markets/status");
    const data = await response.json();

    if (data.status === "Data available") {
      let marketInfo = `📊 **Current Market Status**\n\n`;
      marketInfo += `Active Markets: ${data.markets_count}\n`;
      marketInfo += `Last Updated: ${new Date(
        data.last_updated
      ).toLocaleString()}\n\n`;

      if (data.sample_markets && data.sample_markets.length > 0) {
        marketInfo += `**Sample Markets:**\n`;
        data.sample_markets.forEach((market) => {
          marketInfo += `• ${market.title}\n`;
          marketInfo += `  Status: ${market.status} | Price: ${market.last_price} | Volume: ${market.volume}\n\n`;
        });
      }

      addMessageToChat("assistant", marketInfo);
    } else {
      addMessageToChat(
        "assistant",
        "No market data available. Try refreshing the markets."
      );
    }
  } catch (error) {
    console.error("Error displaying market data:", error);
    addMessageToChat(
      "assistant",
      "Error fetching market data. Please try again."
    );
  }
}

// Display event categories in chat
async function displayEventCategories() {
  try {
    const response = await fetch("/api/events/categories");
    const data = await response.json();

    if (data.success) {
      let categoriesInfo = `📋 **Kalshi Event Categories**\n\n`;
      categoriesInfo += `Total Events: ${data.total_events}\n`;
      categoriesInfo += `Unique Categories: ${data.categories_count}\n`;
      categoriesInfo += `Last Updated: ${new Date(
        data.timestamp
      ).toLocaleString()}\n\n`;

      if (data.categories && data.categories.length > 0) {
        categoriesInfo += `**Available Categories:**\n`;
        // Group categories by first letter
        const categoriesByLetter = {};
        data.categories.forEach((category) => {
          const firstLetter = category[0]?.toUpperCase() || "Other";
          if (!categoriesByLetter[firstLetter]) {
            categoriesByLetter[firstLetter] = [];
          }
          categoriesByLetter[firstLetter].push(category);
        });

        // Display categories alphabetically
        Object.keys(categoriesByLetter)
          .sort()
          .forEach((letter) => {
            categoriesInfo += `${letter}:\n`;
            categoriesByLetter[letter].sort().forEach((category) => {
              categoriesInfo += `  • ${category}\n`;
            });
            categoriesInfo += "\n";
          });
      }

      addMessageToChat("assistant", categoriesInfo);
    } else {
      addMessageToChat(
        "assistant",
        "Failed to fetch event categories. Please try again."
      );
    }
  } catch (error) {
    console.error("Error displaying event categories:", error);
    addMessageToChat(
      "assistant",
      "Error fetching event categories. Please try again."
    );
  }
}

// Add typing dots animation CSS
const style = document.createElement("style");
style.textContent = `
    .typing-dots {
        display: flex;
        gap: 4px;
        align-items: center;
    }
    
    .typing-dots span {
        width: 8px;
        height: 8px;
        background: #10a37f;
        border-radius: 50%;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
    .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes typing {
        0%, 80%, 100% {
            transform: scale(0);
            opacity: 0.5;
        }
        40% {
            transform: scale(1);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);
