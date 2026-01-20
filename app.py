from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
import os
from dotenv import load_dotenv
from datetime import datetime
import stripe

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Anthropic client
client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

# Initialize Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# Simple in-memory usage tracking (use database in production)
user_usage = {}

@app.route('/')
def home():
    return jsonify({
        "message": "Arabic Tutor API is running!",
        "status": "ok",
        "endpoints": {
            "/api/chat": "POST - Send messages to the AI tutor",
            "/api/health": "GET - Check server health",
            "/api/check-subscription": "POST - Check user subscription status",
            "/api/create-checkout": "POST - Create Stripe checkout session"
        }
    })

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "service": "Arabic Tutor API"})

@app.route('/api/create-checkout', methods=['POST'])
def create_checkout():
    """Create a Stripe checkout session for subscription"""
    try:
        data = request.json
        user_email = data.get('email')
        plan = data.get('plan', 'premium')  # premium or premium_voice
        
        # Define your price IDs (get these from Stripe Dashboard after creating products)
        price_ids = {
            'premium': os.environ.get('STRIPE_PRICE_PREMIUM'),  # £9.99/month
            'premium_voice': os.environ.get('STRIPE_PRICE_PREMIUM_VOICE')  # £19.99/month
        }
        
        price_id = price_ids.get(plan)
        
        if not price_id:
            return jsonify({'error': 'Invalid plan selected'}), 400
        
        # Get your actual domain from environment variable
        domain = os.environ.get('FRONTEND_URL', 'http://localhost:8000')
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f'{domain}/success.html?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{domain}',
            customer_email=user_email,
        )
        
        return jsonify({'checkout_url': checkout_session.url})
        
    except Exception as e:
        print(f"Checkout error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-subscription', methods=['POST'])
def check_subscription():
    """Check if user has active subscription"""
    try:
        data = request.json
        user_email = data.get('email')
        
        if not user_email:
            return jsonify({'has_subscription': False, 'remaining_messages': 10})
        
        # Search for customer by email
        customers = stripe.Customer.list(email=user_email, limit=1)
        
        if not customers.data:
            # Count today's usage
            today = datetime.now().strftime('%Y-%m-%d')
            usage_key = f"{user_email}:{today}"
            current_usage = user_usage.get(usage_key, 0)
            remaining = max(0, 10 - current_usage)
            
            return jsonify({
                'has_subscription': False,
                'remaining_messages': remaining
            })
        
        customer = customers.data[0]
        subscriptions = stripe.Subscription.list(
            customer=customer.id, 
            status='active', 
            limit=1
        )
        
        has_active = len(subscriptions.data) > 0
        
        return jsonify({
            'has_subscription': has_active,
            'subscription_status': subscriptions.data[0].status if has_active else None,
            'remaining_messages': 'unlimited' if has_active else 0
        })
        
    except Exception as e:
        print(f"Subscription check error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])
        system_prompt = data.get('system', '')
        max_tokens = data.get('max_tokens', 1024)
        user_email = data.get('user_email', 'anonymous')
        
        if not messages:
            print("ERROR: No messages provided")
            return jsonify({"error": "No messages provided"}), 400
        
        # Check if user has active subscription
        has_subscription = check_user_has_subscription(user_email)
        
        # Apply usage limits for free users
        if not has_subscription and user_email != 'anonymous':
            today = datetime.now().strftime('%Y-%m-%d')
            usage_key = f"{user_email}:{today}"
            current_usage = user_usage.get(usage_key, 0)
            
            if current_usage >= 10:
                return jsonify({
                    "success": False,
                    "error": "Daily limit reached! Upgrade to Premium for unlimited messages.",
                    "upgrade_required": True,
                    "remaining_messages": 0
                }), 429
            
            # Increment usage
            user_usage[usage_key] = current_usage + 1
            remaining = 10 - user_usage[usage_key]
        else:
            remaining = 'unlimited'
        
        print(f"Calling Claude API with {len(messages)} messages...")
        
        # Call Claude API
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages
        )
        
        assistant_message = response.content[0].text
        print(f"Success! Got response: {assistant_message[:100]}...")
        
        return jsonify({
            "success": True,
            "message": assistant_message,
            "model": "claude-sonnet-4-5-20250929",
            "remaining_messages": remaining
        })
        
    except anthropic.APIError as e:
        error_msg = f"Anthropic API error: {str(e)}"
        print(f"ERROR: {error_msg}")
        return jsonify({
            "success": False,
            "error": error_msg
        }), 500
        
    except Exception as e:
        error_msg = f"Server error: {str(e)}"
        print(f"ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": error_msg
        }), 500

def check_user_has_subscription(email):
    """Helper function to check if user has active subscription"""
    if email == 'anonymous':
        return False
    
    try:
        customers = stripe.Customer.list(email=email, limit=1)
        if not customers.data:
            return False
        
        customer = customers.data[0]
        subscriptions = stripe.Subscription.list(
            customer=customer.id, 
            status='active', 
            limit=1
        )
        
        return len(subscriptions.data) > 0
    except Exception as e:
        print(f"Subscription check helper error: {str(e)}")
        return False

if __name__ == '__main__':
    # Check environment variables
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("WARNING: ANTHROPIC_API_KEY not set!")
    else:
        print("✓ Anthropic API key loaded")
    
    if not os.environ.get("STRIPE_SECRET_KEY"):
        print("WARNING: STRIPE_SECRET_KEY not set!")
    else:
        print("✓ Stripe API key loaded")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
