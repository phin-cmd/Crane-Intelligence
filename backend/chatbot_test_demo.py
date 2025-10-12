"""
Crane Intelligence - Demo Chatbot (No API Key Required)
This is a simplified demo version for testing the system
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Demo responses (no OpenAI API needed)
DEMO_RESPONSES = {
    "rental": "The industry standard rental rate for cranes is 1.5% of the crane's estimated value per month. For example, a $1 million crane would typically rent for $15,000 per month. This rate can vary based on region, crane type, and market conditions.",
    
    "crane types": "We evaluate 5 main crane types:\n\n1. **Crawler Cranes** - Tracked base, high capacity (50-1500+ tons)\n2. **All-Terrain Cranes** - Highway capable, versatile (30-1200 tons)\n3. **Rough Terrain Cranes** - Off-road, compact (15-165 tons)\n4. **Truck-Mounted Cranes** - Road mobile, quick setup (15-100 tons)\n5. **Telescopic Crawler Cranes** - Combines crawler + telescopic boom (50-300 tons)\n\nEach type has specific valuation considerations.",
    
    "boom": "Boom configuration significantly affects crane value:\n\n- **Extended Boom Length**: Adds $500 per foot over 300ft\n- **Standard Jib**: Adds $50,000 base + $400 per foot\n- **Luffing Jib**: Adds $150,000 base + $800 per foot\n- **Special Models**: Premium models like Liebherr LR1300SX or Kobelco CK1100G with luffing jib can add $300,000+\n\nA complete boom package can add $200,000-$450,000 to a crane's value.",
    
    "buy vs rent": "Here's how to decide:\n\n**Buy if:**\n- You'll use it for 3+ years (typical break-even point)\n- You have stable, long-term projects\n- You want to build equity\n- Your crane utilization is high (>60%)\n\n**Rent if:**\n- Short-term project (< 2 years)\n- Variable workload\n- Cash flow concerns\n- You want flexibility and latest models\n\n**5-Year Analysis Example:**\n- Purchase: $1M crane + $250k operating = $1.25M\n- Rental: $15k/month × 60 months = $900k\n- Break-even: ~67 months",
    
    "manufacturers": "We cover all major crane manufacturers:\n\n**Top Tier:**\n- Liebherr (German, premium quality)\n- Tadano (Japanese, reliable)\n- Grove (Manitowoc, versatile)\n\n**Mid Tier:**\n- Manitowoc (American, crawler specialist)\n- Link-Belt (American, value)\n- Kobelco (Japanese, crawler expert)\n\n**Growing:**\n- Sany (Chinese, competitive pricing)\n- XCMG (Chinese, expanding market)\n- Zoomlion (Chinese, innovative)\n\nEach manufacturer has different resale values and premiums.",
    
    "valuation": "Our valuation methodology uses:\n\n1. **Base Value**: Capacity × $5,000/ton\n2. **Manufacturer Premium**: 5-20% depending on brand\n3. **Model Premium**: 5-15% for sought-after models\n4. **Boom Package**: $50k-$450k depending on configuration\n5. **Age Depreciation**: 5% per year\n6. **Hours Adjustment**: -3% if above average usage\n7. **Regional Factor**: -5% to +4% by location\n8. **Market Conditions**: -5% to +5% current trends\n\n**Confidence Score**: Based on comparable sales data and market liquidity.",
    
    "default": "I'm the Crane Intelligence AI assistant (Demo Mode). I can help you with:\n\n• Crane valuations and rental rates\n• Different crane types and their uses\n• Boom package configurations\n• Purchase vs rental decisions\n• Manufacturer information\n• Market analysis\n\nWhat would you like to know?"
}

conversation_histories = {}

@app.route('/api/chatbot/health', methods=['GET'])
def health_check():
    """Check if the chatbot service is running"""
    return jsonify({
        "status": "healthy",
        "service": "Crane Intelligence Chatbot (DEMO MODE)",
        "timestamp": datetime.now().isoformat(),
        "mode": "demo",
        "note": "Using demo responses - No OpenAI API key required"
    })

@app.route('/api/chatbot/conversation/new', methods=['POST'])
def create_new_conversation():
    """Create a new chatbot conversation"""
    data = request.json
    user_id = data.get('user_id', 'anonymous')
    
    conversation_id = f"{user_id}_{datetime.now().timestamp()}"
    conversation_histories[conversation_id] = []
    
    return jsonify({
        "success": True,
        "conversation_id": conversation_id,
        "message": "Demo conversation created - No API key needed!",
        "mode": "demo"
    })

@app.route('/api/chatbot/message', methods=['POST'])
def send_chatbot_message():
    """Send a message to the chatbot (demo responses)"""
    data = request.json
    conversation_id = data.get('conversation_id')
    user_message = data.get('message', '').lower()
    
    if not conversation_id or not user_message:
        return jsonify({
            "success": False,
            "error": "conversation_id and message are required"
        }), 400
    
    # Simple keyword matching for demo
    response_text = DEMO_RESPONSES["default"]
    
    if "rental" in user_message or "rent" in user_message:
        response_text = DEMO_RESPONSES["rental"]
    elif "crane type" in user_message or "types of crane" in user_message:
        response_text = DEMO_RESPONSES["crane types"]
    elif "boom" in user_message or "jib" in user_message:
        response_text = DEMO_RESPONSES["boom"]
    elif "buy" in user_message or "purchase" in user_message:
        response_text = DEMO_RESPONSES["buy vs rent"]
    elif "manufacturer" in user_message or "brand" in user_message:
        response_text = DEMO_RESPONSES["manufacturers"]
    elif "valuation" in user_message or "value" in user_message or "calculate" in user_message:
        response_text = DEMO_RESPONSES["valuation"]
    
    # Add note that this is demo mode
    response_text += "\n\n_Note: This is demo mode with pre-programmed responses. For AI-powered responses, add your OpenAI API key._"
    
    return jsonify({
        "success": True,
        "message": response_text,
        "conversation_id": conversation_id,
        "timestamp": datetime.now().isoformat(),
        "mode": "demo",
        "tokens_used": 0
    })

@app.route('/api/chatbot/crane-query', methods=['POST'])
def crane_specific_query():
    """Handle crane-specific queries (demo mode)"""
    data = request.json
    conversation_id = data.get('conversation_id')
    query = data.get('query', '').lower()
    crane_data = data.get('crane_data', {})
    
    # Extract crane details
    manufacturer = crane_data.get('manufacturer', 'N/A')
    model = crane_data.get('model', 'N/A')
    capacity = crane_data.get('capacity', 'N/A')
    estimated_value = crane_data.get('estimated_value', 0)
    rental_rate = crane_data.get('rental_rate', 0)
    
    # Generate contextual response
    response = f"""Based on this {manufacturer} {model} ({capacity} tons):

**Estimated Value**: ${estimated_value:,}
**Monthly Rental Rate**: ${rental_rate:,} (1.5% of value)

"""
    
    if "good deal" in query or "worth it" in query:
        response += """**Deal Analysis**:
• The rental rate aligns with industry standard (1.5%)
• Consider comparable sales in your region
• Check the crane's maintenance history
• Verify boom package configuration
• Review recent market trends

This appears to be a fair market valuation. I recommend:
1. Get a physical inspection
2. Review maintenance records
3. Check for any outstanding liens
4. Compare with 3-4 similar units

_Note: Demo mode - For detailed AI analysis, add OpenAI API key_"""
    elif "buy or rent" in query:
        break_even = int(estimated_value / rental_rate) if rental_rate > 0 else 0
        response += f"""**Buy vs Rent Analysis**:

**Break-even Point**: ~{break_even} months ({break_even/12:.1f} years)

**Purchase Option**:
- Initial Cost: ${estimated_value:,}
- 5-Year Total: ~${int(estimated_value * 1.23):,} (with operating costs)

**Rental Option**:
- Monthly: ${rental_rate:,}
- 5-Year Total: ${rental_rate * 60:,}

**Recommendation**: {'Buy if using 3+ years' if break_even < 50 else 'Rent for flexibility'}

_Note: Demo mode - For personalized AI recommendations, add OpenAI API key_"""
    else:
        response += """**Key Considerations**:
• This crane's capacity and age affect resale value
• Boom configuration adds significant value
• Regional market demand varies
• Operating hours impact depreciation

For a detailed analysis, use the full valuation terminal.

_Note: Demo mode - For AI-powered insights, add OpenAI API key_"""
    
    return jsonify({
        "success": True,
        "message": response,
        "conversation_id": conversation_id,
        "timestamp": datetime.now().isoformat(),
        "mode": "demo"
    })

@app.route('/api/chatbot/quick-responses', methods=['GET'])
def get_quick_responses():
    """Get common quick responses"""
    return jsonify({
        "success": True,
        "quick_responses": {
            "rental_rate": {
                "question": "What is the standard rental rate?",
                "answer": DEMO_RESPONSES["rental"]
            },
            "crane_types": {
                "question": "What types of cranes do you evaluate?",
                "answer": DEMO_RESPONSES["crane types"]
            },
            "manufacturers": {
                "question": "Which manufacturers do you cover?",
                "answer": DEMO_RESPONSES["manufacturers"]
            }
        }
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🤖 CRANE INTELLIGENCE CHATBOT - DEMO MODE")
    print("=" * 60)
    print("✅ No OpenAI API key required for demo")
    print("📝 Uses pre-programmed responses")
    print("🌐 Running on http://0.0.0.0:5001/")
    print("=" * 60)
    print("\n💡 To use real AI (GPT-4):")
    print("   1. Get API key: https://platform.openai.com/account/api-keys")
    print("   2. Set: export OPENAI_API_KEY='sk-...'")
    print("   3. Run: python chatbot_connector.py")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5001, debug=True)

