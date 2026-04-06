from flask import Blueprint, jsonify
from models.database import get_db_connection
from datetime import datetime
from collections import defaultdict

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/analysis/<int:user_id>', methods=['GET'])
def get_analysis(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses WHERE user_id = ?', (user_id,))
    expenses = cursor.fetchall()
    conn.close()
    
    if not expenses:
        return jsonify({
            "total_expense": 0,
            "category_breakdown": {},
            "monthly_summary": {}
        }), 200
    
    # Calculate totals
    total_expense = sum(expense['amount'] for expense in expenses)
    
    # Category-wise breakdown
    category_breakdown = defaultdict(float)
    for expense in expenses:
        category_breakdown[expense['category']] += expense['amount']
    
    # Monthly summary (YYYY-MM)
    monthly_summary = defaultdict(float)
    for expense in expenses:
        try:
            date_obj = datetime.strptime(expense['date'], '%Y-%m-%d')
            month_key = date_obj.strftime('%Y-%m')
            monthly_summary[month_key] += expense['amount']
        except:
            pass
    
    return jsonify({
        "total_expense": float(total_expense),
        "category_breakdown": dict(category_breakdown),
        "monthly_summary": dict(monthly_summary)
    }), 200
