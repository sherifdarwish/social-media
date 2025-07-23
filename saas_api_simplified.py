
# Stripe Payment Integration
@app.route("/api/payments/create-checkout-session", methods=["POST"])
@jwt_required()
def create_checkout_session():
    user_email = get_jwt_identity()
    data = request.get_json() or {}
    
    plan_id = data.get("plan_id")
    success_url = data.get("success_url", "http://localhost:3000/dashboard?payment=success")
    cancel_url = data.get("cancel_url", "http://localhost:3000/settings?payment=cancelled")
    
    if plan_id != "pro":
        return jsonify({"error": "Invalid plan"}), 400
    
    # In a real implementation, you would use the Stripe API here
    # For demo purposes, we'll simulate the checkout session
    checkout_session = {
        "id": f"cs_test_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "checkout_url": f"https://checkout.stripe.com/pay/cs_test_demo#{plan_id}",
        "customer_email": user_email,
        "amount": 2000,  # $20.00 in cents
        "currency": "usd",
        "success_url": success_url,
        "cancel_url": cancel_url
    }
    
    return jsonify({
        "message": "Checkout session created successfully",
        "checkout_url": checkout_session["checkout_url"],
        "session_id": checkout_session["id"]
    })

@app.route("/api/payments/webhook", methods=["POST"])
def stripe_webhook():
    # In a real implementation, you would verify the Stripe webhook signature
    # and handle different event types (payment_intent.succeeded, etc.)
    
    payload = request.get_json() or {}
    event_type = payload.get("type", "payment_intent.succeeded")
    
    if event_type == "payment_intent.succeeded":
        # Update user subscription status
        customer_email = payload.get("data", {}).get("object", {}).get("customer_email")
        if customer_email and customer_email in users:
            users[customer_email]["subscription"] = "pro"
            users[customer_email]["subscription_status"] = "active"
            users[customer_email]["subscription_updated"] = datetime.utcnow().isoformat()
    
    return jsonify({"received": True})

@app.route("/api/payments/cancel-subscription", methods=["POST"])
@jwt_required()
def cancel_subscription():
    user_email = get_jwt_identity()
    
    if user_email in users:
        users[user_email]["subscription"] = "free"
        users[user_email]["subscription_status"] = "cancelled"
        users[user_email]["subscription_updated"] = datetime.utcnow().isoformat()
        
        return jsonify({
            "message": "Subscription cancelled successfully",
            "new_plan": "free"
        })
    
    return jsonify({"error": "User not found"}), 404

@app.route("/api/payments/subscription-status", methods=["GET"])
@jwt_required()
def get_subscription_status():
    user_email = get_jwt_identity()
    
    if user_email in users:
        user = users[user_email]
        return jsonify({
            "subscription": user.get("subscription", "free"),
            "status": user.get("subscription_status", "active"),
            "updated": user.get("subscription_updated"),
            "features": {
                "max_accounts": "unlimited" if user.get("subscription") == "pro" else 3,
                "max_posts_per_month": "unlimited" if user.get("subscription") == "pro" else 10,
                "advanced_ai": user.get("subscription") == "pro",
                "priority_support": user.get("subscription") == "pro",
                "api_access": user.get("subscription") == "pro"
            }
        })
    
    return jsonify({"error": "User not found"}), 404

# Enhanced content generation endpoints
@app.route('/api/generator/business-brief', methods=['POST'])
def save_business_brief():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('company_name') or not data.get('industry'):
            return jsonify({'error': 'Company name and industry are required'}), 400
        
        # In a real app, save to database
        # For now, return success
        return jsonify({
            'message': 'Business profile saved successfully',
            'profile_id': 'bp_' + str(int(time.time()))
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/content/save-suggestions', methods=['POST'])
def save_content_suggestions():
    try:
        data = request.get_json()
        suggestions = data.get('suggestions', [])
        campaign_name = data.get('campaign_name', 'Untitled Campaign')
        
        if not suggestions:
            return jsonify({'error': 'No suggestions to save'}), 400
        
        # In a real app, save to database
        # For now, return success
        return jsonify({
            'message': f'Saved {len(suggestions)} content suggestions for campaign: {campaign_name}',
            'campaign_id': 'camp_' + str(int(time.time())),
            'saved_count': len(suggestions)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Enhanced content suggestions endpoint
@app.route('/api/content/suggestions', methods=['GET', 'POST'])
def get_content_suggestions():
    try:
        if request.method == 'POST':
            data = request.get_json()
            business_profile = data.get('business_profile', {})
            content_strategy = data.get('content_strategy', {})
        else:
            business_profile = {}
            content_strategy = {}
        
        # Generate realistic content suggestions
        platforms = content_strategy.get('platforms', ['facebook', 'twitter', 'instagram', 'linkedin', 'tiktok'])
        company_name = business_profile.get('company_name', 'Your Company')
        industry = business_profile.get('industry', 'business')
        
        suggestions = []
        content_templates = {
            'facebook': [
                f"🚀 Exciting news from {company_name}! We're revolutionizing the {industry} industry with our latest innovation. What do you think about the future of {industry}? #Innovation #{industry.title()}",
                f"Behind the scenes at {company_name}! Our team is working hard to bring you the best {industry} solutions. Here's a sneak peek at what we're building... 👀 #BehindTheScenes #TeamWork",
                f"Did you know? The {industry} industry is evolving rapidly, and {company_name} is at the forefront of this change. Here are 3 trends we're watching closely... 📈 #Trends #{industry.title()}"
            ],
            'twitter': [
                f"🔥 Hot take: The future of {industry} is here, and {company_name} is leading the charge! What's your prediction for the next big breakthrough? #{industry} #Innovation",
                f"Quick tip Tuesday! 💡 Here's how {company_name} approaches {industry} challenges differently. Thread 🧵 1/3",
                f"Celebrating our amazing {industry} community! 🎉 Thank you for trusting {company_name} with your needs. What's been your biggest win this week? #Community #{industry.title()}"
            ],
            'instagram': [
                f"✨ Transform your {industry} experience with {company_name}! Swipe to see the difference we're making in our clients' lives. 📸 #{industry} #Transformation #ClientSuccess",
                f"Monday motivation from the {company_name} team! 💪 Every challenge in {industry} is an opportunity to innovate. What's motivating you this week? #MondayMotivation #{industry}",
                f"Behind the magic at {company_name}! 🎭 Here's how we create exceptional {industry} solutions that our clients love. Process reveal in stories! #BehindTheScenes #Process"
            ],
            'linkedin': [
                f"Industry Insight: The {industry} landscape is shifting, and {company_name} is adapting with strategic innovations. Here's what we're seeing and how we're responding to market demands. #Leadership #{industry.title()} #Strategy",
                f"Thought Leadership: At {company_name}, we believe that success in {industry} comes from understanding both technology and human needs. Here's our approach to balancing innovation with practicality. #ThoughtLeadership #Innovation",
                f"Team Spotlight: Meet our {industry} experts at {company_name} who are driving change and delivering exceptional results for our clients. Their expertise makes all the difference. #TeamSpotlight #Expertise #{industry.title()}"
            ],
            'tiktok': [
                f"POV: You discover {company_name}'s secret to {industry} success 🤫 #POV #{industry} #Success #Viral",
                f"Day in the life at {company_name}! From coffee to breakthrough moments in {industry} ☕➡️💡 #DayInTheLife #WorkLife #{industry}",
                f"Tell me you work in {industry} without telling me you work in {industry}... I'll go first! 😂 #{industry} #WorkHumor #Relatable"
            ]
        }
        
        for i, platform in enumerate(platforms[:5]):  # Limit to 5 platforms
            if platform in content_templates:
                for j, template in enumerate(content_templates[platform][:2]):  # 2 posts per platform
                    suggestions.append({
                        'id': f'suggestion_{i}_{j}',
                        'platform': platform,
                        'type': ['promotional', 'educational', 'entertaining'][j % 3],
                        'content': template,
                        'hashtags': f"#{company_name.replace(' ', '')} #{industry} #SocialMedia",
                        'engagement_score': random.randint(7, 10),
                        'optimal_time': ['9:00 AM', '1:00 PM', '5:00 PM', '7:00 PM'][j % 4],
                        'status': 'pending',
                        'created_at': datetime.now().isoformat()
                    })
        
        return jsonify({
            'suggestions': suggestions,
            'total_count': len(suggestions),
            'generated_at': datetime.now().isoformat(),
            'business_profile': business_profile,
            'content_strategy': content_strategy
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Individual content status update endpoint
@app.route('/api/content/suggestions/<suggestion_id>/status', methods=['PATCH'])
def update_content_status(suggestion_id):
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
        
        valid_statuses = ['pending', 'approved', 'rejected', 'thumbs_up', 'thumbs_down']
        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
        
        # In a real app, update the database record
        # For now, return success with the updated status
        return jsonify({
            'message': f'Content status updated to {new_status}',
            'suggestion_id': suggestion_id,
            'status': new_status,
            'updated_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
