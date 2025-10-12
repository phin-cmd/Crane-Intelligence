"""
Crane Intelligence - GPT Chatbot Connector
OpenAI Integration for Customer Support and Crane Analysis
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# OpenAI API Configuration
openai.api_key = os.getenv('OPENAI_API_KEY')  # Store in environment variable

# System prompt for crane intelligence chatbot
CRANE_INTELLIGENCE_SYSTEM_PROMPT = """
You are an expert AI assistant for Crane Intelligence, a professional crane valuation and market analysis platform.

Your expertise includes:
- Crane valuation methodologies
- Market analysis for construction equipment
- Different crane types (crawler, all-terrain, rough terrain, truck-mounted, telescopic crawler)
- Major crane manufacturers (Liebherr, Tadano, Grove, Manitowoc, Link-Belt, Sany, Kobelco, XCMG)
- Rental rates (industry standard: 1.5% of crane value per month)
- Operating costs (maintenance, insurance, storage)
- Boom package configurations and premiums

Your tone is:
- Professional and knowledgeable
- Helpful and conversational
- Data-driven with specific numbers when relevant
- Focused on helping customers make informed decisions

Guidelines:
- Provide accurate crane industry information
- Use industry standard calculations (1.5% rental rate, etc.)
- Recommend using the valuation terminal for specific valuations
- Be concise but comprehensive
- If you don't know specific technical specs, acknowledge it
"""

# Conversation history storage (in production, use Redis or database)
conversation_histories = {}


class GPTChatbotConnector:
    """
    GPT Chatbot Connector for Crane Intelligence Platform
    """
    
    def __init__(self, model: str = "gpt-4", temperature: float = 0.7):
        """
        Initialize the chatbot connector
        
        Args:
            model: OpenAI model to use (gpt-4, gpt-3.5-turbo, etc.)
            temperature: Controls randomness (0=deterministic, 1=creative)
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = 1000
        
    def create_conversation(self, user_id: str) -> str:
        """
        Create a new conversation for a user
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            conversation_id: Unique conversation identifier
        """
        conversation_id = f"{user_id}_{datetime.now().timestamp()}"
        conversation_histories[conversation_id] = [
            {"role": "system", "content": CRANE_INTELLIGENCE_SYSTEM_PROMPT}
        ]
        return conversation_id
    
    def send_message(
        self, 
        conversation_id: str, 
        user_message: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Send a message to GPT and get response
        
        Args:
            conversation_id: ID of the conversation
            user_message: User's message
            context: Optional context (crane data, valuation results, etc.)
            
        Returns:
            Response dictionary with AI message and metadata
        """
        try:
            # Get conversation history
            if conversation_id not in conversation_histories:
                conversation_histories[conversation_id] = [
                    {"role": "system", "content": CRANE_INTELLIGENCE_SYSTEM_PROMPT}
                ]
            
            messages = conversation_histories[conversation_id]
            
            # Add context if provided (e.g., current crane valuation data)
            if context:
                context_message = f"\n\nCurrent Context:\n{json.dumps(context, indent=2)}"
                user_message += context_message
            
            # Add user message to history
            messages.append({"role": "user", "content": user_message})
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract AI response
            ai_message = response.choices[0].message.content
            
            # Add AI response to history
            messages.append({"role": "assistant", "content": ai_message})
            
            # Update conversation history (keep last 20 messages)
            conversation_histories[conversation_id] = messages[-20:]
            
            return {
                "success": True,
                "message": ai_message,
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat(),
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_crane_specific_response(
        self,
        conversation_id: str,
        query: str,
        crane_data: Dict
    ) -> Dict:
        """
        Get AI response with specific crane data context
        
        Args:
            conversation_id: ID of the conversation
            query: User's question
            crane_data: Current crane valuation data
            
        Returns:
            AI response with crane-specific insights
        """
        enhanced_query = f"""
User Question: {query}

Crane Details:
- Manufacturer: {crane_data.get('manufacturer', 'N/A')}
- Model: {crane_data.get('model', 'N/A')}
- Type: {crane_data.get('crane_type', 'N/A')}
- Capacity: {crane_data.get('capacity', 'N/A')} tons
- Year: {crane_data.get('year', 'N/A')}
- Hours: {crane_data.get('hours', 'N/A')}
- Estimated Value: ${crane_data.get('estimated_value', 'N/A'):,}
- Monthly Rental Rate: ${crane_data.get('rental_rate', 'N/A'):,}

Please provide a helpful response considering this specific crane's details.
"""
        return self.send_message(conversation_id, enhanced_query)


# Initialize connector
chatbot = GPTChatbotConnector(model="gpt-4", temperature=0.7)


# ==================== API ROUTES ====================

@app.route('/api/chatbot/conversation/new', methods=['POST'])
def create_new_conversation():
    """
    Create a new chatbot conversation
    
    Request Body:
        {
            "user_id": "user123"
        }
    
    Response:
        {
            "success": true,
            "conversation_id": "user123_1234567890.123",
            "message": "Conversation created successfully"
        }
    """
    data = request.json
    user_id = data.get('user_id', 'anonymous')
    
    conversation_id = chatbot.create_conversation(user_id)
    
    return jsonify({
        "success": True,
        "conversation_id": conversation_id,
        "message": "Conversation created successfully"
    })


@app.route('/api/chatbot/message', methods=['POST'])
def send_chatbot_message():
    """
    Send a message to the chatbot
    
    Request Body:
        {
            "conversation_id": "user123_1234567890.123",
            "message": "What's the average rental rate for a 110 ton crawler crane?",
            "context": {
                "crane_type": "Crawler Crane",
                "capacity": 110
            }
        }
    
    Response:
        {
            "success": true,
            "message": "AI response here...",
            "conversation_id": "...",
            "timestamp": "2025-10-10T12:00:00",
            "tokens_used": 150
        }
    """
    data = request.json
    conversation_id = data.get('conversation_id')
    user_message = data.get('message')
    context = data.get('context')
    
    if not conversation_id or not user_message:
        return jsonify({
            "success": False,
            "error": "conversation_id and message are required"
        }), 400
    
    response = chatbot.send_message(conversation_id, user_message, context)
    
    return jsonify(response)


@app.route('/api/chatbot/crane-query', methods=['POST'])
def crane_specific_query():
    """
    Ask a question about a specific crane with full context
    
    Request Body:
        {
            "conversation_id": "user123_1234567890.123",
            "query": "Is this a good deal?",
            "crane_data": {
                "manufacturer": "Kobelco",
                "model": "CK1100G-2",
                "crane_type": "Crawler Crane",
                "capacity": 110,
                "year": 2018,
                "hours": 5000,
                "estimated_value": 792000,
                "rental_rate": 11880
            }
        }
    
    Response:
        {
            "success": true,
            "message": "Based on this Kobelco CK1100G-2...",
            "conversation_id": "...",
            "timestamp": "2025-10-10T12:00:00"
        }
    """
    data = request.json
    conversation_id = data.get('conversation_id')
    query = data.get('query')
    crane_data = data.get('crane_data')
    
    if not all([conversation_id, query, crane_data]):
        return jsonify({
            "success": False,
            "error": "conversation_id, query, and crane_data are required"
        }), 400
    
    response = chatbot.get_crane_specific_response(
        conversation_id, 
        query, 
        crane_data
    )
    
    return jsonify(response)


@app.route('/api/chatbot/health', methods=['GET'])
def health_check():
    """Check if the chatbot service is running"""
    return jsonify({
        "status": "healthy",
        "service": "Crane Intelligence Chatbot",
        "timestamp": datetime.now().isoformat(),
        "model": chatbot.model
    })


# Quick response templates (for common questions without API calls)
QUICK_RESPONSES = {
    "rental_rate": {
        "question": "What is the standard rental rate?",
        "answer": "The industry standard rental rate for cranes is 1.5% of the crane's estimated value per month. For example, a $1 million crane would typically rent for $15,000 per month."
    },
    "crane_types": {
        "question": "What types of cranes do you evaluate?",
        "answer": "We evaluate 5 main crane types: Crawler Cranes, All-Terrain Cranes, Rough Terrain Cranes, Truck-Mounted Cranes, and Telescopic Crawler Cranes. Each type has specific valuation considerations."
    },
    "manufacturers": {
        "question": "Which manufacturers do you cover?",
        "answer": "We cover all major crane manufacturers including Liebherr, Tadano, Grove, Manitowoc, Link-Belt, Sany, Kobelco, XCMG, Terex, Zoomlion, HSC, Kato, and IHI."
    }
}


@app.route('/api/chatbot/quick-responses', methods=['GET'])
def get_quick_responses():
    """Get common quick responses without using GPT API"""
    return jsonify({
        "success": True,
        "quick_responses": QUICK_RESPONSES
    })


if __name__ == '__main__':
    # Check if API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  WARNING: OPENAI_API_KEY environment variable not set!")
        print("Please set it with: export OPENAI_API_KEY='your-api-key-here'")
    
    # Run the Flask app
    print("🤖 Starting Crane Intelligence Chatbot Connector...")
    print(f"📊 Model: {chatbot.model}")
    print(f"🌡️  Temperature: {chatbot.temperature}")
    app.run(host='0.0.0.0', port=5001, debug=True)

