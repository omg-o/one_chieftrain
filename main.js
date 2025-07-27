let selectedHotel = null;
let isTyping = false;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Add event listener for Enter key on message input
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
});

// Select hotel function
async function selectHotel(hotelId) {
    try {
        showLoadingScreen();
        
        const response = await fetch('/select_hotel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ hotel_id: hotelId })
        });
        
        const data = await response.json();
        
        if (data.success) {
            selectedHotel = data.hotel;
            showChatInterface();
            addMessage(data.message, 'bot');
        } else {
            alert('Error selecting hotel: ' + (data.error || 'Unknown error'));
            showHotelSelection();
        }
    } catch (error) {
        console.error('Error selecting hotel:', error);
        alert('Failed to connect to hotel. Please try again.');
        showHotelSelection();
    }
}

// Send message function
async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const message = messageInput.value.trim();
    
    if (!message || isTyping) return;
    
    // Disable input and button
    messageInput.disabled = true;
    sendBtn.disabled = true;
    isTyping = true;
    
    // Add user message to chat
    addMessage(message, 'user');
    messageInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        // Hide typing indicator
        hideTypingIndicator();
        
        if (data.response) {
            addMessage(data.response, 'bot');
        } else {
            addMessage('I apologize, but I encountered an error. Please try again.', 'bot');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        hideTypingIndicator();
        addMessage('I\'m sorry, but I\'m having trouble connecting right now. Please try again in a moment.', 'bot');
    } finally {
        // Re-enable input and button
        messageInput.disabled = false;
        sendBtn.disabled = false;
        isTyping = false;
        messageInput.focus();
    }
}

// Add message to chat
function addMessage(text, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-bubble">
            ${formatMessage(text)}
        </div>
        <div class="message-time">${currentTime}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Format message text (handle line breaks, etc.)
function formatMessage(text) {
    return text
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>');
}

// Show typing indicator
function showTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.style.display = 'flex';
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Hide typing indicator
function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.style.display = 'none';
    }
}

// Show hotel selection screen
function showHotelSelection() {
    document.getElementById('hotelSelection').style.display = 'block';
    document.getElementById('chatInterface').style.display = 'none';
    document.getElementById('loadingScreen').style.display = 'none';
}

// Show chat interface
function showChatInterface() {
    if (selectedHotel) {
        document.getElementById('selectedHotelName').textContent = selectedHotel.name;
        document.getElementById('selectedHotelLocation').textContent = '📍 ' + selectedHotel.location;
    }
    
    document.getElementById('hotelSelection').style.display = 'none';
    document.getElementById('chatInterface').style.display = 'flex';
    document.getElementById('loadingScreen').style.display = 'none';
    
    // Focus on message input
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.focus();
    }
}

// Show loading screen
function showLoadingScreen() {
    document.getElementById('hotelSelection').style.display = 'none';
    document.getElementById('chatInterface').style.display = 'none';
    document.getElementById('loadingScreen').style.display = 'flex';
}

// Change hotel function
async function changeHotel() {
    if (confirm('Are you sure you want to change hotels? Your current conversation will be lost.')) {
        try {
            await fetch('/reset_session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            // Clear chat messages
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = '';
            
            // Reset selected hotel
            selectedHotel = null;
            
            // Show hotel selection
            showHotelSelection();
        } catch (error) {
            console.error('Error resetting session:', error);
            alert('Failed to reset session. Please refresh the page.');
        }
    }
}

// Get conversation history (optional feature)
async function getHistory() {
    try {
        const response = await fetch('/history');
        const data = await response.json();
        
        if (data.bookings || data.tasks) {
            console.log('Booking History:', data.bookings);
            console.log('Task History:', data.tasks);
            // You can implement a modal or sidebar to display this information
        }
    } catch (error) {
        console.error('Error fetching history:', error);
    }
}

// Handle connection errors gracefully
window.addEventListener('online', function() {
    const messageInput = document.getElementById('messageInput');
    if (messageInput && messageInput.disabled) {
        messageInput.disabled = false;
        messageInput.placeholder = 'How may I assist you today?';
    }
});

window.addEventListener('offline', function() {
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.disabled = true;
        messageInput.placeholder = 'Connection lost. Please check your internet.';
    }
});

// Auto-resize textarea functionality (if needed)
function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}