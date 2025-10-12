# 🚀 GPT Chatbot - Quick Start Guide

**Get your AI chatbot running in 5 minutes!**

---

## ⚡ Super Quick Setup

### 1. Get OpenAI API Key (2 minutes)

```bash
# Go to: https://platform.openai.com/account/api-keys
# Click "Create new secret key"
# Copy the key (starts with 'sk-')
```

### 2. Set Environment Variable (1 minute)

```bash
# Linux/Mac
export OPENAI_API_KEY='sk-your-key-here'

# Windows
set OPENAI_API_KEY=sk-your-key-here
```

### 3. Install Dependencies (1 minute)

```bash
cd /root/Crane-Intelligence/backend
pip install openai==0.28.1 flask==2.3.0 flask-cors==4.0.0
```

### 4. Start Backend Server (30 seconds)

```bash
python chatbot_connector.py
```

**Expected:** You'll see:
```
🤖 Starting Crane Intelligence Chatbot Connector...
 * Running on http://0.0.0.0:5001/
```

### 5. Test It (30 seconds)

Open browser to your valuation terminal page. You should see a green chatbot button (💬) in the bottom-right corner!

---

## 🧪 Quick Test Commands

```bash
# Test 1: Health check
curl http://localhost:5001/api/chatbot/health

# Test 2: Send a message
curl -X POST http://localhost:5001/api/chatbot/message \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test_123",
    "message": "What is the standard crane rental rate?"
  }'
```

---

## 🎯 What You Get

✅ **AI-powered chatbot** on your site  
✅ **24/7 crane expertise** for customers  
✅ **Context-aware responses** about valuations  
✅ **Professional UI** with typing indicators  
✅ **Conversation history** maintained  

---

## 💰 Cost

- **GPT-3.5-turbo:** ~$2-3/month for 1000 conversations
- **GPT-4:** ~$45-60/month for 1000 conversations

Start with GPT-3.5-turbo to save costs!

Change model in `chatbot_connector.py` line 19:
```python
chatbot = GPTChatbotConnector(model="gpt-3.5-turbo", temperature=0.7)
```

---

## 🐛 Troubleshooting

**Problem:** "OPENAI_API_KEY not set"  
**Fix:** Run `export OPENAI_API_KEY='sk-...'` then restart server

**Problem:** Can't see chatbot button  
**Fix:** Check browser console for errors, ensure `chatbot-connector.js` is loaded

**Problem:** "Connection refused"  
**Fix:** Make sure backend server is running on port 5001

---

## 📖 Full Documentation

See `GPT_CONNECTOR_SETUP_GUIDE.md` for:
- Production deployment
- Security best practices
- Advanced configuration
- Cost optimization
- Integration examples

---

## 🎉 Done!

Your AI chatbot is ready. Click the green button to start chatting!

**Example questions to try:**
- "What's the rental rate for a 110 ton crane?"
- "Should I buy or rent?"
- "How does boom configuration affect value?"
- "Tell me about crawler cranes vs all-terrain cranes"

---

**Need help?** Check the full setup guide or test with curl commands above.

