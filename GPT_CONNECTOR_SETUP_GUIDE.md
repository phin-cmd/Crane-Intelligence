# 🤖 GPT Connector Setup Guide
## Crane Intelligence Platform - AI Chatbot Integration

**Last Updated:** October 10, 2025  
**Difficulty:** Intermediate  
**Estimated Setup Time:** 30-45 minutes

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step-by-Step Setup](#step-by-step-setup)
4. [Testing the Connector](#testing-the-connector)
5. [Integration into Valuation Terminal](#integration-into-valuation-terminal)
6. [Production Deployment](#production-deployment)
7. [Cost Management](#cost-management)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

### What is a GPT Connector?

A GPT connector is a bridge between your application and OpenAI's GPT models that allows you to:

- **Add conversational AI** to your website
- **Provide instant answers** about crane valuations
- **Analyze crane data** with AI insights
- **Answer customer questions** 24/7 without human intervention

### Architecture Diagram

```
┌─────────────────┐
│  User Browser   │
│  (Frontend)     │
└────────┬────────┘
         │
         │ HTTP Request
         ▼
┌─────────────────┐
│  Flask Backend  │
│  (Python API)   │
└────────┬────────┘
         │
         │ API Call
         ▼
┌─────────────────┐
│  OpenAI API     │
│  (GPT-4/GPT-3.5)│
└─────────────────┘
```

### Files Created

1. **`backend/chatbot_connector.py`** - Python Flask API server
2. **`frontend/js/chatbot-connector.js`** - Frontend JavaScript client
3. **This guide** - Setup and configuration instructions

---

## ✅ Prerequisites

### Required Accounts

1. **OpenAI Account**
   - Sign up at: https://platform.openai.com/signup
   - Required for API access

### Required Software

```bash
# Python 3.8+ (check version)
python --version  # or python3 --version

# pip (Python package manager)
pip --version

# Node.js & npm (optional, for frontend dev)
node --version
npm --version
```

### Required Python Packages

```bash
pip install openai==0.28.1
pip install flask==2.3.0
pip install flask-cors==4.0.0
```

---

## 🚀 Step-by-Step Setup

### Step 1: Get OpenAI API Key

1. **Go to OpenAI Platform:**
   - Visit: https://platform.openai.com/account/api-keys

2. **Create API Key:**
   - Click "Create new secret key"
   - Give it a name: "Crane Intelligence Chatbot"
   - **IMPORTANT:** Copy and save the key immediately (you can't view it again!)
   - Format: `sk-...` (starts with 'sk-')

3. **Add Billing Method:**
   - Go to: https://platform.openai.com/account/billing
   - Add payment method
   - Set spending limits (recommended: $50/month to start)

### Step 2: Set Environment Variable

#### On Linux/Mac:

```bash
# Temporary (current session only)
export OPENAI_API_KEY='sk-your-actual-api-key-here'

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export OPENAI_API_KEY="sk-your-actual-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

#### On Windows:

```cmd
# Temporary (current session)
set OPENAI_API_KEY=sk-your-actual-api-key-here

# Permanent (System Environment Variables)
1. Open System Properties > Environment Variables
2. Add new System Variable:
   - Name: OPENAI_API_KEY
   - Value: sk-your-actual-api-key-here
```

#### Verify Setup:

```bash
# Check if environment variable is set
echo $OPENAI_API_KEY  # Linux/Mac
echo %OPENAI_API_KEY%  # Windows
```

### Step 3: Install Python Dependencies

```bash
# Navigate to backend directory
cd /root/Crane-Intelligence/backend

# Install requirements
pip install openai==0.28.1 flask==2.3.0 flask-cors==4.0.0

# Or create requirements.txt file
cat > requirements_chatbot.txt << EOF
openai==0.28.1
flask==2.3.0
flask-cors==4.0.0
requests==2.31.0
EOF

# Install from requirements
pip install -r requirements_chatbot.txt
```

### Step 4: Start the Backend Server

```bash
# Navigate to backend directory
cd /root/Crane-Intelligence/backend

# Run the chatbot connector
python chatbot_connector.py
```

**Expected Output:**
```
🤖 Starting Crane Intelligence Chatbot Connector...
📊 Model: gpt-4
🌡️  Temperature: 0.7
 * Running on http://0.0.0.0:5001/ (Press CTRL+C to quit)
```

**If you see a warning about API key:**
```
⚠️  WARNING: OPENAI_API_KEY environment variable not set!
```
→ Go back to Step 2 and set the environment variable

### Step 5: Add Frontend Script to Valuation Terminal

Open `/root/Crane-Intelligence/frontend/valuation_terminal.html` and add before `</body>`:

```html
<!-- GPT Chatbot Connector -->
<script src="/js/chatbot-connector.js"></script>
```

### Step 6: Update API URL for Production

In `chatbot-connector.js`, line 7:

```javascript
// Development
const API_BASE_URL = 'http://localhost:5001/api/chatbot';

// Production (replace with your domain)
const API_BASE_URL = 'https://craneintelligence.tech/api/chatbot';
```

---

## 🧪 Testing the Connector

### Test 1: Health Check

```bash
curl http://localhost:5001/api/chatbot/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "Crane Intelligence Chatbot",
  "timestamp": "2025-10-10T12:00:00",
  "model": "gpt-4"
}
```

### Test 2: Create Conversation

```bash
curl -X POST http://localhost:5001/api/chatbot/conversation/new \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user_123"}'
```

**Expected Response:**
```json
{
  "success": true,
  "conversation_id": "test_user_123_1696950000.0",
  "message": "Conversation created successfully"
}
```

### Test 3: Send Message

```bash
curl -X POST http://localhost:5001/api/chatbot/message \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test_user_123_1696950000.0",
    "message": "What is the standard rental rate for cranes?",
    "context": null
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "The industry standard rental rate for cranes is 1.5% of the crane's estimated value per month...",
  "conversation_id": "test_user_123_1696950000.0",
  "timestamp": "2025-10-10T12:00:00",
  "tokens_used": 150
}
```

### Test 4: Test in Browser

1. Open: `http://localhost:5001/api/chatbot/health`
2. Should see JSON response with "status": "healthy"

### Test 5: Test Frontend Integration

1. Open your valuation terminal page
2. Look for chatbot button in bottom-right corner (green circle with 💬)
3. Click to open chatbot
4. Try sending a message: "What is the rental rate for a 110 ton crane?"

---

## 🔗 Integration into Valuation Terminal

### Option A: Ask About Current Valuation

Add this button to the valuation results section:

```html
<button class="btn btn-secondary" onclick="askAIAboutValuation()">
    🤖 Ask AI About This Valuation
</button>

<script>
async function askAIAboutValuation() {
    // Get current valuation data
    const craneData = {
        manufacturer: document.getElementById('manufacturer').value,
        model: document.getElementById('model').value,
        crane_type: document.getElementById('craneType').value,
        capacity: parseInt(document.getElementById('capacity').value),
        year: parseInt(document.getElementById('year').value),
        hours: parseInt(document.getElementById('hours').value),
        estimated_value: 792000, // Get from calculation
        rental_rate: 11880 // Get from calculation
    };

    // Open chatbot
    craneChatbot.toggleChat();
    
    // Auto-ask about the crane
    const response = await craneChatbot.askAboutCrane(
        "Is this a good deal? What should I know about this crane?",
        craneData
    );
}
</script>
```

### Option B: Smart Quick Actions

Update quick action buttons based on page context:

```javascript
// If on valuation page with results
if (document.getElementById('valuationResults').classList.contains('show')) {
    const quickActions = document.getElementById('quick-actions');
    quickActions.innerHTML = `
        <button class="quick-action-btn" onclick="craneChatbot.quickAsk('Is this valuation accurate?')">
            ✅ Validate This Valuation
        </button>
        <button class="quick-action-btn" onclick="craneChatbot.quickAsk('Should I buy or rent this crane?')">
            📊 Buy vs Rent
        </button>
        <button class="quick-action-btn" onclick="craneChatbot.quickAsk('What are the risks with this purchase?')">
            ⚠️ Risk Analysis
        </button>
    `;
}
```

---

## 🌐 Production Deployment

### Step 1: Deploy Backend (Flask API)

#### Option A: Gunicorn (Recommended)

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
cd /root/Crane-Intelligence/backend
gunicorn -w 4 -b 0.0.0.0:5001 chatbot_connector:app
```

#### Option B: Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements_chatbot.txt .
RUN pip install -r requirements_chatbot.txt

COPY chatbot_connector.py .

ENV OPENAI_API_KEY=""

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "chatbot_connector:app"]
```

Build and run:

```bash
docker build -t crane-chatbot .
docker run -p 5001:5001 -e OPENAI_API_KEY=$OPENAI_API_KEY crane-chatbot
```

### Step 2: Configure Nginx Reverse Proxy

Add to your nginx config:

```nginx
# Chatbot API
location /api/chatbot/ {
    proxy_pass http://localhost:5001/api/chatbot/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Reload nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Step 3: Update Frontend API URL

In `chatbot-connector.js`:

```javascript
const API_BASE_URL = 'https://craneintelligence.tech/api/chatbot';
```

### Step 4: Set Environment Variable Permanently

```bash
# Create systemd service
sudo nano /etc/systemd/system/crane-chatbot.service

[Unit]
Description=Crane Intelligence Chatbot API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/root/Crane-Intelligence/backend
Environment="OPENAI_API_KEY=sk-your-actual-key-here"
ExecStart=/usr/bin/gunicorn -w 4 -b 127.0.0.1:5001 chatbot_connector:app
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable crane-chatbot
sudo systemctl start crane-chatbot
sudo systemctl status crane-chatbot
```

---

## 💰 Cost Management

### OpenAI API Pricing (as of Oct 2025)

| Model | Input (per 1K tokens) | Output (per 1K tokens) |
|-------|----------------------|------------------------|
| GPT-4 | $0.03 | $0.06 |
| GPT-3.5-turbo | $0.0015 | $0.002 |

### Estimated Costs

**Scenario:** 1000 conversations/month, 10 messages each, average 150 tokens/message

**Using GPT-4:**
- Total tokens: 1000 × 10 × 150 = 1,500,000 tokens
- Rough cost: ~$45-60/month

**Using GPT-3.5-turbo:**
- Same usage: ~$2-3/month

### Cost Optimization Tips

1. **Use GPT-3.5-turbo for simple questions:**
```python
# In chatbot_connector.py
chatbot = GPTChatbotConnector(model="gpt-3.5-turbo", temperature=0.7)
```

2. **Limit conversation history:**
```python
# Keep only last 10 messages instead of 20
conversation_histories[conversation_id] = messages[-10:]
```

3. **Set spending limits in OpenAI dashboard:**
- Go to: https://platform.openai.com/account/billing/limits
- Set hard limit (e.g., $50/month)

4. **Cache common responses:**
- Store frequently asked questions locally
- Use quick responses without API calls

5. **Monitor usage:**
```bash
# Check usage at
https://platform.openai.com/account/usage
```

---

## 🐛 Troubleshooting

### Error: "OPENAI_API_KEY environment variable not set"

**Solution:**
```bash
export OPENAI_API_KEY='sk-your-key-here'
# Then restart the server
```

### Error: "Invalid API key"

**Causes:**
- Key not copied correctly (missing characters)
- Key revoked/deleted in OpenAI dashboard
- Billing issue with OpenAI account

**Solution:**
1. Generate new API key at platform.openai.com
2. Update environment variable
3. Restart server

### Error: "Connection refused" when frontend calls backend

**Causes:**
- Backend not running
- Port 5001 already in use
- CORS issues

**Solutions:**
```bash
# Check if backend is running
curl http://localhost:5001/api/chatbot/health

# Check what's on port 5001
lsof -i :5001  # Linux/Mac
netstat -ano | findstr :5001  # Windows

# Change port if needed (in chatbot_connector.py)
app.run(host='0.0.0.0', port=5002, debug=True)
```

### Error: "Rate limit exceeded"

**Cause:** Too many API calls in short time

**Solution:**
```python
# Add rate limiting
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@limiter.limit("10 per minute")
@app.route('/api/chatbot/message', methods=['POST'])
def send_chatbot_message():
    # ...
```

### Chatbot button not appearing

**Checklist:**
1. ✅ `chatbot-connector.js` loaded? (Check browser console)
2. ✅ No JavaScript errors? (Check browser console)
3. ✅ CSS styles injected? (Inspect page elements)
4. ✅ Script runs after DOM loaded?

**Debug:**
```javascript
// Add to browser console
console.log(craneChatbot);  // Should show object
console.log(document.getElementById('crane-chatbot-container'));  // Should show element
```

---

## 📚 Additional Resources

### OpenAI Documentation
- API Reference: https://platform.openai.com/docs/api-reference
- Best Practices: https://platform.openai.com/docs/guides/production-best-practices

### Flask Documentation
- Quickstart: https://flask.palletsprojects.com/quickstart/
- Deployment: https://flask.palletsprojects.com/deploying/

### Security Best Practices
- Never expose API keys in frontend code
- Use environment variables only
- Implement rate limiting
- Add user authentication
- Log all API calls for monitoring

---

## 🎯 Next Steps

After successful setup:

1. ✅ **Test thoroughly** with various questions
2. ✅ **Monitor costs** in OpenAI dashboard first month
3. ✅ **Gather user feedback** on chatbot quality
4. ✅ **Fine-tune system prompt** for better responses
5. ✅ **Add analytics** to track usage patterns
6. ✅ **Consider GPT-3.5-turbo** for cost savings if acceptable
7. ✅ **Implement conversation persistence** (save to database)
8. ✅ **Add user ratings** for responses (thumbs up/down)

---

## 💬 Support

For issues or questions:

1. Check this guide's troubleshooting section
2. Review OpenAI API status: https://status.openai.com
3. Test API directly with curl commands above
4. Check Flask server logs for errors

---

**Setup Complete!** 🎉

Your GPT connector is now ready to provide AI-powered assistance for crane valuations!

**Cost Estimate:** $2-60/month depending on usage and model choice  
**Setup Time:** ~30-45 minutes  
**Maintenance:** Minimal (monitor costs and update prompts as needed)

