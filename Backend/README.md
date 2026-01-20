# Arabic AI Tutor - Flask Backend Setup Guide

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Python 3.8 or higher
- Your Anthropic API key from console.anthropic.com

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Set Up Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API key:
```
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
```

### Step 3: Run the Server

```bash
python app.py
```

You should see:
```
✓ API key loaded successfully
 * Running on http://0.0.0.0:5000
```

### Step 4: Open the App

1. Open `arabic-tutor.html` in your browser
2. Make sure the backend is running on port 5000
3. Start chatting!

---

## 📁 Project Structure

```
arabic-tutor/
├── backend/
│   ├── app.py              # Flask server
│   ├── requirements.txt    # Python dependencies
│   ├── .env               # Your API key (DO NOT COMMIT)
│   ├── .env.example       # Example environment file
│   └── .gitignore         # Git ignore rules
├── arabic-tutor.html      # Frontend app
├── landing-page.html      # Marketing page
└── DEVELOPMENT_GUIDE.md   # Full guide
```

---

## 🧪 Testing the Backend

### Test 1: Health Check
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Arabic Tutor API"
}
```

### Test 2: Chat Endpoint
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "مرحبا"}],
    "system": "You are an Arabic tutor"
  }'
```

---

## 🌐 Deployment Options

### Option 1: Render (Easiest - FREE)

1. Create account at render.com
2. Connect your GitHub repo
3. Create new "Web Service"
4. Set these environment variables:
   - `ANTHROPIC_API_KEY`: Your API key
5. Deploy!

**Your URL will be:** `https://your-app-name.onrender.com`

### Option 2: Railway (Also FREE)

1. Create account at railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select your repo
4. Add environment variable: `ANTHROPIC_API_KEY`
5. Deploy!

### Option 3: Heroku

1. Install Heroku CLI
2. Create `Procfile`:
```
web: gunicorn app:app
```
3. Deploy:
```bash
heroku create your-app-name
heroku config:set ANTHROPIC_API_KEY=your-key-here
git push heroku main
```

### After Deployment

Update the `BACKEND_URL` in `arabic-tutor.html`:

```javascript
const BACKEND_URL = 'https://your-app-name.onrender.com';
```

---

## 🔒 Security Best Practices

### ✅ DO:
- Keep `.env` file secret (it's in .gitignore)
- Use environment variables for API keys
- Enable HTTPS in production (automatic on Render/Railway)
- Add rate limiting for production
- Monitor API usage on console.anthropic.com

### ❌ DON'T:
- Commit API keys to GitHub
- Share your `.env` file
- Use the same API key for testing and production
- Expose the API key in frontend code

---

## 💰 Cost Management

### Current Setup:
- **Claude Sonnet 4.5:**
  - Input: $3 per million tokens (~£2.40)
  - Output: $15 per million tokens (~£12)
  - Average conversation: ~2000 tokens = £0.03

### Example Monthly Costs:
- **10 active students** (100 messages each): ~£30/month
- **50 active students** (100 messages each): ~£150/month
- **100 active students** (100 messages each): ~£300/month

### Cost Optimization Tips:
1. Add message limits for free tier (10/day)
2. Cache common responses
3. Use Claude Haiku for simple queries (much cheaper)
4. Monitor usage in Anthropic console

---

## 🔧 Adding Features

### Feature 1: User Authentication

Install Flask-Login:
```bash
pip install flask-login flask-sqlalchemy
```

Add to `app.py`:
```python
from flask_login import LoginManager, login_required

# Protect the chat endpoint
@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    # existing code...
```

### Feature 2: Usage Tracking

Add to `app.py`:
```python
from datetime import datetime
import sqlite3

def log_usage(user_id, tokens_used):
    conn = sqlite3.connect('usage.db')
    c = conn.cursor()
    c.execute('''INSERT INTO usage 
                 (user_id, tokens_used, timestamp) 
                 VALUES (?, ?, ?)''', 
              (user_id, tokens_used, datetime.now()))
    conn.commit()
    conn.close()
```

### Feature 3: Payment Integration (Stripe)

```bash
pip install stripe
```

See DEVELOPMENT_GUIDE.md for full implementation.

---

## 🐛 Troubleshooting

### Problem: "Connection refused" error
**Solution:** Make sure Flask server is running (`python app.py`)

### Problem: "API key not set" warning
**Solution:** Check your `.env` file exists and has the correct API key

### Problem: CORS errors
**Solution:** Flask-CORS is installed and configured. Make sure you installed all requirements.

### Problem: "ModuleNotFoundError: No module named 'anthropic'"
**Solution:** Run `pip install -r requirements.txt`

### Problem: Port 5000 already in use
**Solution:** Change port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```
And update `BACKEND_URL` in HTML file.

---

## 📊 Monitoring & Logs

### View Logs Locally:
Flask automatically logs to console. Look for:
- ✓ Successful requests (200)
- ✗ Errors (4xx, 5xx)
- API call details

### Production Monitoring:
- **Render:** Built-in logs in dashboard
- **Railway:** Built-in logs in dashboard
- **Heroku:** `heroku logs --tail`

### API Usage Monitoring:
Check your Anthropic dashboard:
https://console.anthropic.com

---

## 🔄 Updating Your App

### Backend Updates:
```bash
git pull
pip install -r requirements.txt
# Restart server
```

### Frontend Updates:
Just refresh the HTML file in your browser

### Deployment Updates:
- **Render/Railway:** Auto-deploy on git push
- **Heroku:** `git push heroku main`

---

## 📈 Scaling for Growth

### Up to 100 users:
- Current setup is fine
- Use free tier hosting (Render/Railway)

### 100-1000 users:
- Upgrade to paid hosting (~£5-10/month)
- Add Redis caching
- Consider Claude Haiku for simple queries

### 1000+ users:
- Use load balancer
- Multiple server instances
- Database for user management
- CDN for static files

---

## 💡 Next Steps

1. ✅ Get backend running locally
2. ✅ Test the chat functionality
3. ✅ Deploy to Render/Railway
4. ✅ Update frontend with production URL
5. ✅ Add payment integration (see DEVELOPMENT_GUIDE.md)
6. ✅ Launch and get first users!

---

## 🆘 Need Help?

**Common Issues:**
- Check the Troubleshooting section above
- Read the error messages carefully
- Check Anthropic API status: status.anthropic.com

**Resources:**
- Flask docs: flask.palletsprojects.com
- Anthropic docs: docs.anthropic.com
- Deployment guides: docs.render.com, docs.railway.app

**Contact:**
If you're stuck, feel free to ask for help!

---

## 📝 License & Usage

This is your project, Mohammed! You own all rights to:
- The code
- The business
- The content
- The brand

Use it however you want - teach students, sell subscriptions, license to schools, etc.

Good luck with your Arabic teaching business! 🚀🇸🇦
