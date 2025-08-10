const chatLog = document.getElementById('chat-log');
const questionOptions = document.getElementById('question-options');
const botAvatar = 'https://cdn-icons-png.flaticon.com/512/4712/4712035.png';

const questions = {
  start: {
    prompt: "Please choose one of the following:",
    options: [
      { text: "🛒 Orders & Deliveries", next: "orderDelivery" },
      { text: "🥬 Product Information", next: "productInfo" },
      { text: "💳 Payment Options", next: "paymentInfo" },
      { text: "📣 File a Complaint", next: "complaintStart" }
    ]
  },
  orderDelivery: {
    prompt: "Questions about your order or delivery:",
    options: [
      { text: "Where is my order?", next: "trackOrder" },
      { text: "What areas do you deliver to?", next: "deliveryArea" },
      { text: "Back 🔙", next: "start" }
    ]
  },
  productInfo: {
    prompt: "Product-related questions:",
    options: [
      { text: "Are your products organic?", next: "organicAnswer" },
      { text: "Where do your products come from?", next: "productSource" },
      { text: "Back 🔙", next: "start" }
    ]
  },
  paymentInfo: {
    prompt: "Payment-related options:",
    options: [
      { text: "Do you offer Cash on Delivery?", next: "cod" },
      { text: "Do you support online payment?", next: "noOnline" },
      { text: "Back 🔙", next: "start" }
    ]
  }
};

const responses = {
  trackOrder: "📦 You can check your order status on the order monitoring page.",
  deliveryArea: "🚚 We currently deliver within Antipolo City, Rizal.",
  organicAnswer: "🌱 Yes! All our products are organic.",
  productSource: "👨‍🌾 Our products are proudly sourced from local farmers.",
  cod: "💵 Yes, we offer Cash on Delivery (COD).",
  noOnline: "⚠️ We currently do not offer online payment options."
};

const fallbackOptions = [
  { text: "🔙 Back to Main Menu", next: "start" }
];

function showComplaintInput() {
  questionOptions.innerHTML = '';

  const instruction = document.createElement('div');
  instruction.className = 'bot-text-input';
  instruction.innerText = "Please type your complaint below:";

  const input = document.createElement('textarea');
  input.className = 'complaint-input';
  input.rows = 3;
  input.placeholder = "Type your complaint...";

  const buttonContainer = document.createElement('div');
  buttonContainer.style.display = 'flex';
  buttonContainer.style.gap = '10px';
  buttonContainer.style.marginTop = '10px';

  const submitBtn = document.createElement('button');
  submitBtn.className = 'option-button';
  submitBtn.innerText = "Submit Complaint";

  const backBtn = document.createElement('button');
  backBtn.className = 'option-button';
  backBtn.innerText = "Back";

  submitBtn.onclick = async () => {
    const complaint = input.value.trim();
    if (complaint === '') return;

    submitBtn.disabled = true;
    backBtn.disabled = true;
    submitBtn.innerText = "Submitting...";

    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    addMessage("user", complaint, time);
    saveChatToSession("user", complaint, time);

    try {
      const res = await fetch('/chatbot/submit-complaint/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ complaint })
      });

      addMessage("bot", "Thank you! Your complaint has been submitted to our support team.", time);
      saveChatToSession("bot", "Thank you! Your complaint has been submitted to our support team.", time);
    } catch (error) {
      console.error("Error submitting complaint:", error);
      addMessage("bot", "Sorry, something went wrong. Please try again later.", time);
    }

    showDynamicOptions(fallbackOptions);
  };

  backBtn.onclick = () => {
    showDynamicOptions(fallbackOptions);
  };

  buttonContainer.appendChild(submitBtn);
  buttonContainer.appendChild(backBtn);

  questionOptions.appendChild(instruction);
  questionOptions.appendChild(input);
  questionOptions.appendChild(buttonContainer);
}

function addMessage(sender, text, time = null) {
  const wrapper = document.createElement('div');
  wrapper.className = `${sender} message-row`;

  const bubble = document.createElement('div');
  bubble.className = `message-content ${sender}`;
  bubble.innerText = text;

  const timestamp = document.createElement('div');
  timestamp.className = 'timestamp';
  timestamp.innerText = time || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  bubble.appendChild(timestamp);

  if (sender === 'bot') {
    const avatar = document.createElement('img');
    avatar.src = botAvatar;
    avatar.className = 'avatar';
    wrapper.appendChild(avatar);
    wrapper.appendChild(bubble);
  } else {
    wrapper.appendChild(bubble);
  }

  chatLog.appendChild(wrapper);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function showTypingIndicator() {
  const typing = document.createElement('div');
  typing.className = 'typing-indicator';
  typing.id = 'typing';
  typing.innerText = 'FreshMart is typing...';
  chatLog.appendChild(typing);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function removeTypingIndicator() {
  const typing = document.getElementById('typing');
  if (typing) typing.remove();
}

function showOptions(key) {
  questionOptions.innerHTML = '';
  const group = questions[key];
  if (!group) return;

  // Add prompt message only when navigating normally (not restore)
  const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  addMessage("bot", group.prompt, time);
  saveChatToSession("bot", group.prompt, time);

  group.options.forEach(option => {
    const btn = document.createElement('button');
    btn.className = 'option-button';
    btn.innerText = option.text;
    btn.onclick = () => handleUserChoice(option);
    questionOptions.appendChild(btn);
  });

  sessionStorage.setItem('chatFlowKey', key);
}

function showButtonsOnly(key) {
  questionOptions.innerHTML = '';
  const group = questions[key];
  if (!group) return;

  group.options.forEach(option => {
    const btn = document.createElement('button');
    btn.className = 'option-button';
    btn.innerText = option.text;
    btn.onclick = () => handleUserChoice(option);
    questionOptions.appendChild(btn);
  });
}

function showDynamicOptions(options) {
  questionOptions.innerHTML = '';
  options.forEach(option => {
    const btn = document.createElement('button');
    btn.className = 'option-button';
    btn.innerText = option.text;
    btn.onclick = () => handleUserChoice(option);
    questionOptions.appendChild(btn);
  });
}

function handleUserChoice(option) {
  const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  addMessage("user", option.text, time);
  saveChatToSession("user", option.text, time);

  questionOptions.innerHTML = '';
  showTypingIndicator();

  setTimeout(() => {
    removeTypingIndicator();

    if (option.next === 'complaintStart') {
      showComplaintInput();
      return;
    }

    if (responses[option.next]) {
      addMessage("bot", responses[option.next], time);
      saveChatToSession("bot", responses[option.next], time);
      showDynamicOptions(fallbackOptions);
    } else if (questions[option.next]) {
      showOptions(option.next);
    } else {
      showOptions("start");
    }
  }, 800);
}

function saveChatToSession(sender, text, time) {
  const existing = JSON.parse(sessionStorage.getItem('chatHistory') || '[]');
  existing.push({ sender, text, time });
  sessionStorage.setItem('chatHistory', JSON.stringify(existing));
}

function restoreChat() {
  const history = JSON.parse(sessionStorage.getItem('chatHistory') || '[]');
  history.forEach(msg => {
    addMessage(msg.sender, msg.text, msg.time);
  });

  const flowKey = sessionStorage.getItem('chatFlowKey') || 'start';
  showButtonsOnly(flowKey);
}

function startChat() {
  const greeting = "Hi there! How can I help you today?";
  const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  addMessage("bot", greeting, time);
  saveChatToSession("bot", greeting, time);
  showOptions("start");
}

window.onload = () => {
  const history = JSON.parse(sessionStorage.getItem('chatHistory') || '[]');
  if (history.length > 0) {
    restoreChat();
  } else {
    startChat();
  }
};

document.addEventListener("DOMContentLoaded", function () {
  const chatIcon = document.getElementById("chat-icon");
  const chatContainer = document.getElementById("chatbot-container");
  const closeBtn = document.getElementById("close-chat");

chatIcon.addEventListener("click", function () {
  chatContainer.style.display = "flex";  // Use flex to keep layout intact
  chatIcon.style.display = "none";
});

closeBtn.addEventListener("click", function () {
  chatContainer.style.display = "none";
  chatIcon.style.display = "flex";  // Use flex here so icon shows nicely
});
});
