from flask import Blueprint, request, jsonify
from models.database import get_db_connection

smart_bp = Blueprint('smart', __name__)

# Mock Data for Smart Features (Moved from frontend)
RECIPES = {
    "maggi": {
        "name": "Maggi (Basic)",
        "ingredients": ["Maggi (1 pack): ₹14", "Vegetables: ₹10", "Masala: Included"],
        "cost": 24
    },
    "paneer": {
        "name": "Paneer Butter Masala",
        "ingredients": ["Paneer (200g): ₹100", "Butter/Oil: ₹20", "Spices & Veggies: ₹40", "Cream: ₹20"],
        "cost": 180
    },
    "pasta": {
        "name": "White Sauce Pasta",
        "ingredients": ["Pasta (250g): ₹50", "Milk (500ml): ₹30", "Cheese: ₹60", "Vegetables: ₹30"],
        "cost": 170
    },
    "chai": {
        "name": "Special Masala Chai",
        "ingredients": ["Milk (250ml): ₹15", "Tea leaves: ₹5", "Ginger/Cardamom: ₹5", "Sugar: ₹2"],
        "cost": 27
    }
}

TRAVEL_COSTS = {
    "base": 5000,
    "destinations": {
        "goa": {"transport": 4000, "food": 1500, "stay": 2500},
        "manali": {"transport": 3500, "food": 1200, "stay": 2000},
        "shimla": {"transport": 3000, "food": 1000, "stay": 1800},
        "jaipur": {"transport": 2500, "food": 1000, "stay": 2000},
        "udaipur": {"transport": 3000, "food": 1200, "stay": 2500},
        "kerala": {"transport": 5000, "food": 1500, "stay": 3000},
        "mumbai": {"transport": 2000, "food": 1500, "stay": 3500},
        "delhi": {"transport": 2000, "food": 1200, "stay": 2500},
        "bangalore": {"transport": 2500, "food": 1300, "stay": 2800},
        "kolkata": {"transport": 2500, "food": 1000, "stay": 2000},
        "chennai": {"transport": 3000, "food": 1200, "stay": 2500},
        "agra": {"transport": 2000, "food": 800, "stay": 1500},
        "varanasi": {"transport": 2500, "food": 800, "stay": 1500},
        "rishikesh": {"transport": 2500, "food": 1000, "stay": 1800},
        "ladakh": {"transport": 8000, "food": 1500, "stay": 2500},
        "andaman": {"transport": 12000, "food": 2000, "stay": 4000},
        "paris": {"transport": 60000, "food": 5000, "stay": 10000},
        "dubai": {"transport": 25000, "food": 3500, "stay": 8000},
        "thailand": {"transport": 20000, "food": 2000, "stay": 3500},
        "singapore": {"transport": 30000, "food": 3000, "stay": 6000},
        "maldives": {"transport": 40000, "food": 4000, "stay": 12000}
    }
}

@smart_bp.route('/recipe/<name>', methods=['GET'])
def get_recipe(name):
    recipe = RECIPES.get(name.lower())
    if recipe:
        return jsonify(recipe), 200
    return jsonify({"error": "Recipe not found"}), 404

@smart_bp.route('/travel', methods=['POST'])
def travel_planner():
    data = request.json
    destination = data.get('destination', '').lower()
    days_input = data.get('days', 1)
    
    # Validate days input (max 30 days for realistic planning)
    try:
        days = int(days_input)
        if days < 1:
            days = 1
        elif days > 30:
            return jsonify({"error": "Please enter a realistic trip duration (max 30 days)"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid number of days"}), 400
    
    # Get destination costs or use default
    cost_data = TRAVEL_COSTS['destinations'].get(destination, {
        "transport": TRAVEL_COSTS['base'], 
        "food": 1000, 
        "stay": 2000
    })
    
    # Calculate costs
    transport = cost_data['transport']  # One-time round trip cost
    food_per_day = cost_data['food']
    stay_per_day = cost_data['stay']
    
    food_total = food_per_day * days
    stay_total = stay_per_day * days
    total = transport + food_total + stay_total
    
    return jsonify({
        "destination": destination.capitalize(),
        "days": days,
        "transport": transport,
        "food": food_total,
        "food_per_day": food_per_day,
        "stay": stay_total,
        "stay_per_day": stay_per_day,
        "total": total
    }), 200

@smart_bp.route('/set_budget', methods=['POST'])
def set_budget():
    data = request.json
    user_id = data.get('user_id')
    amount = data.get('budget')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO budgets (user_id, monthly_budget)
        VALUES (?, ?)
    ''', (user_id, amount))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Budget updated"}), 200

@smart_bp.route('/budget/<int:user_id>', methods=['GET'])
def get_budget(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    budget = cursor.execute('SELECT monthly_budget FROM budgets WHERE user_id = ?', (user_id,)).fetchone()
    
    # Also get current month's expenses
    from datetime import datetime
    current_month = datetime.now().strftime('%Y-%m')
    expenses = cursor.execute('''
        SELECT SUM(amount) as total FROM expenses 
        WHERE user_id = ? AND strftime('%Y-%m', date) = ?
    ''', (user_id, current_month)).fetchone()
    
    conn.close()
    
    monthly_budget = budget['monthly_budget'] if budget else 0
    total_expense = expenses['total'] if expenses['total'] else 0
    
    alert = ""
    if total_expense > monthly_budget and monthly_budget > 0:
        alert = "⚠️ Budget exceeded! Please control your spending"
    
    return jsonify({
        "budget": monthly_budget,
        "total_expense": total_expense,
        "remaining": max(0, monthly_budget - total_expense),
        "alert": alert
    }), 200
