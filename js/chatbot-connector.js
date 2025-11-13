/**
 * Crane Intelligence - Frontend Chatbot Connector
 * Connects frontend UI to GPT chatbot backend
 */

class CraneIntelligenceChatbot {
    constructor(apiBaseUrl = '/api/v1/chatbot') {
        // Use relative path for production compatibility
        this.apiBaseUrl = apiBaseUrl;
        this.conversationId = null;
        this.userId = this.getUserId();
        this.isOpen = false;
        this.platformVersion = 'v2.0-optimized';
        console.log(`🤖 Crane Intelligence Chatbot ${this.platformVersion} initialized`);
    }

    /**
     * Get or create user ID (stored in localStorage)
     */
    getUserId() {
        let userId = localStorage.getItem('crane_chatbot_user_id');
        if (!userId) {
            userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('crane_chatbot_user_id', userId);
        }
        return userId;
    }

    /**
     * Initialize a new conversation
     */
    async initializeConversation() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/conversation/new`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.userId
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.conversationId = data.conversation_id;
                console.log('✅ Chatbot conversation initialized:', this.conversationId);
                return true;
            } else {
                console.error('❌ Failed to initialize conversation:', data.error);
                return false;
            }
        } catch (error) {
            console.error('❌ Error initializing conversation:', error);
            return false;
        }
    }

    /**
     * Send a message to the chatbot
     * @param {string} message - User's message
     * @param {object} context - Optional context (crane data, etc.)
     */
    async sendMessage(message, context = null) {
        // Initialize conversation if not already done
        if (!this.conversationId) {
            await this.initializeConversation();
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    conversation_id: this.conversationId,
                    message: message,
                    context: context
                })
            });

            const data = await response.json();
            
            if (data.success) {
                return {
                    success: true,
                    message: data.message,
                    timestamp: data.timestamp,
                    tokensUsed: data.tokens_used
                };
            } else {
                return {
                    success: false,
                    error: data.error
                };
            }
        } catch (error) {
            console.error('❌ Error sending message:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Ask about a specific crane with full context
     * @param {string} query - User's question
     * @param {object} craneData - Crane details
     */
    async askAboutCrane(query, craneData) {
        if (!this.conversationId) {
            await this.initializeConversation();
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/crane-query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    conversation_id: this.conversationId,
                    query: query,
                    crane_data: craneData
                })
            });

            const data = await response.json();
            
            if (data.success) {
                return {
                    success: true,
                    message: data.message,
                    timestamp: data.timestamp
                };
            } else {
                return {
                    success: false,
                    error: data.error
                };
            }
        } catch (error) {
            console.error('❌ Error asking about crane:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Get quick responses without API call
     */
    async getQuickResponses() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/quick-responses`);
            const data = await response.json();
            
            if (data.success) {
                return data.quick_responses;
            }
            return null;
        } catch (error) {
            console.error('❌ Error getting quick responses:', error);
            return null;
        }
    }

    /**
     * Create and display chatbot UI
     */
    createChatbotUI() {
        // Check if UI already exists
        if (document.getElementById('crane-chatbot-container')) {
            return;
        }

        const chatbotHTML = `
            <div id="crane-chatbot-container" class="chatbot-container ${this.isOpen ? 'open' : ''}">
                <!-- Chatbot Toggle Button -->
                <button class="chatbot-toggle" id="chatbot-toggle" onclick="craneChatbot.toggleChat()">
                    <img src="/images/logos/favicon.ico" alt="Chat" class="chatbot-icon-img">
                    <span class="chatbot-badge" id="chatbot-badge" style="display: none;">1</span>
                </button>

                <!-- Chatbot Window -->
                <div class="chatbot-window" id="chatbot-window">
                    <!-- Header -->
                    <div class="chatbot-header">
                        <div class="chatbot-header-info">
                            <div class="chatbot-avatar">
                                <img src="/images/logos/favicon.ico" alt="Crane Intelligence" style="width: 100%; height: 100%; object-fit: contain;">
                            </div>
                            <div>
                                <div class="chatbot-title">Crane Intelligence AI</div>
                                <div class="chatbot-status">
                                    <span class="status-dot"></span> Online
                                </div>
                            </div>
                        </div>
                        <button class="chatbot-close" onclick="craneChatbot.toggleChat()">×</button>
                    </div>

                    <!-- Quick Actions -->
                    <div class="chatbot-quick-actions" id="quick-actions">
                        <button class="quick-action-btn" onclick="craneChatbot.quickAsk('What is the standard rental rate?')">
                            📊 Rental Rates
                        </button>
                        <button class="quick-action-btn" onclick="craneChatbot.quickAsk('What crane types do you evaluate?')">
                            🏗️ Crane Types
                        </button>
                        <button class="quick-action-btn" onclick="craneChatbot.quickAsk('How does boom configuration affect value?')">
                            📈 Boom Packages
                        </button>
                    </div>

                    <!-- Messages -->
                    <div class="chatbot-messages" id="chatbot-messages">
                        <div class="chatbot-message bot-message">
                            <div class="message-avatar">
                                <img src="/images/logos/favicon.ico" alt="Bot" style="width: 100%; height: 100%; object-fit: contain;">
                            </div>
                            <div class="message-content">
                                <div class="message-text">
                                    Hi! I'm your Crane Intelligence AI assistant. I can help you with:
                                    <br><br>
                                    • Crane valuations and rental rates<br>
                                    • Market analysis and comparables<br>
                                    • Equipment specifications<br>
                                    • Purchase vs rental decisions<br>
                                    <br>
                                    How can I assist you today?
                                </div>
                                <div class="message-time">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</div>
                            </div>
                        </div>
                    </div>

                    <!-- Input -->
                    <div class="chatbot-input-container">
                        <textarea 
                            class="chatbot-input" 
                            id="chatbot-input" 
                            placeholder="Ask me anything about crane valuations..."
                            rows="1"
                            onkeypress="if(event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); craneChatbot.sendUserMessage(); }"
                        ></textarea>
                        <button class="chatbot-send" id="chatbot-send" onclick="craneChatbot.sendUserMessage()">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                                <path d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </button>
                    </div>

                    <!-- Typing Indicator -->
                    <div class="typing-indicator" id="typing-indicator" style="display: none;">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            </div>
        `;

        // Inject HTML
        document.body.insertAdjacentHTML('beforeend', chatbotHTML);

        // Inject CSS
        this.injectStyles();
    }

    /**
     * Inject chatbot styles
     */
    injectStyles() {
        if (document.getElementById('chatbot-styles')) {
            return;
        }

        const styles = `
            <style id="chatbot-styles">
                .chatbot-container {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    z-index: 9999;
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                }

                .chatbot-toggle {
                    position: relative;
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #00FF88 0%, #00CC6A 100%);
                    border: none;
                    cursor: pointer;
                    box-shadow: 0 4px 20px rgba(0, 255, 136, 0.4);
                    transition: all 0.3s ease;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }

                .chatbot-toggle:hover {
                    transform: scale(1.1);
                    box-shadow: 0 6px 30px rgba(0, 255, 136, 0.6);
                }

                .chatbot-icon {
                    font-size: 28px;
                }

                .chatbot-icon-img {
                    width: 32px;
                    height: 32px;
                    object-fit: contain;
                    filter: brightness(0) invert(1);
                }

                .chatbot-badge {
                    position: absolute;
                    top: -5px;
                    right: -5px;
                    background: #FF4444;
                    color: white;
                    width: 24px;
                    height: 24px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 12px;
                    font-weight: 600;
                }

                .chatbot-window {
                    position: absolute;
                    bottom: 80px;
                    right: 0;
                    width: 400px;
                    height: 600px;
                    background: #1A1A1A;
                    border-radius: 16px;
                    box-shadow: 0 8px 40px rgba(0, 0, 0, 0.6);
                    display: none;
                    flex-direction: column;
                    overflow: hidden;
                    border: 1px solid #404040;
                }

                .chatbot-container.open .chatbot-window {
                    display: flex;
                }

                .chatbot-header {
                    background: linear-gradient(135deg, #2A2A2A 0%, #1A1A1A 100%);
                    padding: 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border-bottom: 1px solid #404040;
                }

                .chatbot-header-info {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }

                .chatbot-avatar {
                    width: 40px;
                    height: 40px;
                    background: #00FF88;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-shrink: 0;
                    font-size: 20px;
                    padding: 6px;
                }

                .chatbot-title {
                    color: #FFFFFF;
                    font-weight: 600;
                    font-size: 16px;
                }

                .chatbot-status {
                    color: #888;
                    font-size: 12px;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                }

                .status-dot {
                    width: 8px;
                    height: 8px;
                    background: #00FF88;
                    border-radius: 50%;
                    animation: pulse 2s infinite;
                }

                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }

                .chatbot-close {
                    background: none;
                    border: none;
                    color: #888;
                    font-size: 32px;
                    cursor: pointer;
                    line-height: 1;
                    padding: 0;
                    width: 32px;
                    height: 32px;
                    transition: color 0.3s ease;
                }

                .chatbot-close:hover {
                    color: #FFFFFF;
                }

                .chatbot-quick-actions {
                    padding: 15px;
                    display: flex;
                    gap: 8px;
                    flex-wrap: wrap;
                    background: #0F0F0F;
                    border-bottom: 1px solid #404040;
                }

                .quick-action-btn {
                    background: #2A2A2A;
                    color: #FFFFFF;
                    border: 1px solid #404040;
                    padding: 8px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }

                .quick-action-btn:hover {
                    background: #00FF88;
                    color: #000000;
                    border-color: #00FF88;
                }

                .chatbot-messages {
                    flex: 1;
                    overflow-y: auto;
                    padding: 20px;
                    display: flex;
                    flex-direction: column;
                    gap: 16px;
                }

                .chatbot-message {
                    display: flex;
                    gap: 12px;
                    animation: fadeIn 0.3s ease;
                }

                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }

                .bot-message {
                    align-self: flex-start;
                }

                .user-message {
                    align-self: flex-end;
                    flex-direction: row-reverse;
                }

                .message-avatar {
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                    background: #00FF88;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-shrink: 0;
                    font-size: 16px;
                    padding: 5px;
                }

                .user-message .message-avatar {
                    background: #2A2A2A;
                }

                .message-content {
                    max-width: 70%;
                }

                .message-text {
                    background: #2A2A2A;
                    padding: 12px 16px;
                    border-radius: 12px;
                    color: #FFFFFF;
                    font-size: 14px;
                    line-height: 1.5;
                }

                .user-message .message-text {
                    background: #00FF88;
                    color: #000000;
                }

                .message-time {
                    font-size: 11px;
                    color: #666;
                    margin-top: 4px;
                    padding: 0 4px;
                }

                .chatbot-input-container {
                    padding: 20px;
                    background: #2A2A2A;
                    border-top: 1px solid #404040;
                    display: flex;
                    gap: 12px;
                    align-items: flex-end;
                }

                .chatbot-input {
                    flex: 1;
                    background: #1A1A1A;
                    border: 1px solid #404040;
                    border-radius: 8px;
                    padding: 12px;
                    color: #FFFFFF;
                    font-size: 14px;
                    resize: none;
                    font-family: inherit;
                    max-height: 120px;
                }

                .chatbot-input:focus {
                    outline: none;
                    border-color: #00FF88;
                }

                .chatbot-send {
                    background: #00FF88;
                    border: none;
                    width: 44px;
                    height: 44px;
                    border-radius: 8px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: #000000;
                    transition: all 0.3s ease;
                }

                .chatbot-send:hover {
                    background: #00E67A;
                    transform: translateY(-2px);
                }

                .chatbot-send:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }

                .typing-indicator {
                    display: flex;
                    gap: 6px;
                    padding: 12px 20px;
                }

                .typing-indicator span {
                    width: 8px;
                    height: 8px;
                    background: #888;
                    border-radius: 50%;
                    animation: typing 1.4s infinite;
                }

                .typing-indicator span:nth-child(2) {
                    animation-delay: 0.2s;
                }

                .typing-indicator span:nth-child(3) {
                    animation-delay: 0.4s;
                }

                @keyframes typing {
                    0%, 60%, 100% { transform: translateY(0); }
                    30% { transform: translateY(-10px); }
                }

                @media (max-width: 768px) {
                    .chatbot-window {
                        width: calc(100vw - 40px);
                        height: calc(100vh - 100px);
                    }
                }
            </style>
        `;

        document.head.insertAdjacentHTML('beforeend', styles);
    }

    /**
     * Toggle chatbot open/close
     */
    toggleChat() {
        this.isOpen = !this.isOpen;
        const container = document.getElementById('crane-chatbot-container');
        if (container) {
            container.classList.toggle('open');
        }
    }

    /**
     * Send user message
     */
    async sendUserMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();

        if (!message) return;

        // Clear input
        input.value = '';
        input.style.height = 'auto';

        // Add user message to UI
        this.addMessageToUI(message, 'user');

        // Show typing indicator
        document.getElementById('typing-indicator').style.display = 'flex';

        // Send to backend
        const response = await this.sendMessage(message);

        // Hide typing indicator
        document.getElementById('typing-indicator').style.display = 'none';

        // Add bot response to UI
        if (response.success) {
            this.addMessageToUI(response.message, 'bot');
        } else {
            this.addMessageToUI('Sorry, I encountered an error. Please try again.', 'bot');
        }
    }

    /**
     * Quick ask preset question
     */
    async quickAsk(question) {
        // Add question to UI as user message
        this.addMessageToUI(question, 'user');

        // Show typing indicator
        document.getElementById('typing-indicator').style.display = 'flex';

        // Send to backend
        const response = await this.sendMessage(question);

        // Hide typing indicator
        document.getElementById('typing-indicator').style.display = 'none';

        // Add bot response
        if (response.success) {
            this.addMessageToUI(response.message, 'bot');
        }
    }

    /**
     * Add message to UI
     */
    addMessageToUI(text, type) {
        const messagesContainer = document.getElementById('chatbot-messages');
        const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        const avatarContent = type === 'bot' 
            ? '<img src="/images/logos/favicon.ico" alt="Bot" style="width: 100%; height: 100%; object-fit: contain;">'
            : '👤';
        
        const messageHTML = `
            <div class="chatbot-message ${type}-message">
                <div class="message-avatar">${avatarContent}</div>
                <div class="message-content">
                    <div class="message-text">${text}</div>
                    <div class="message-time">${time}</div>
                </div>
            </div>
        `;

        messagesContainer.insertAdjacentHTML('beforeend', messageHTML);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

// Initialize global chatbot instance
let craneChatbot;

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname.includes('valuation_terminal.html')) {
        console.log('🤖 Chatbot disabled on valuation terminal');
        return;
    }
    // Initialize chatbot with your backend URL
    // Auto-detect if we're in production or local development
    const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
    const API_BASE_URL = isProduction 
        ? '/api/chatbot'  // Production: use relative URL through nginx proxy
        : 'http://localhost:5001/api/chatbot';     // Local development
    
    craneChatbot = new CraneIntelligenceChatbot(API_BASE_URL);
    
    // Create UI
    craneChatbot.createChatbotUI();
    
    console.log('🤖 Crane Intelligence Chatbot initialized');
    console.log('📡 API URL:', API_BASE_URL);
});

