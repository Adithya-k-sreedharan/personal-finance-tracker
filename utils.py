"""
Utility functions for the Expense Tracker application
"""

from datetime import datetime, date
from functools import wraps
from flask import jsonify, request

def validate_date_format(date_string):
    """Validate date string format (YYYY-MM-DD)"""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_amount(amount):
    """Validate expense amount"""
    try:
        amount = float(amount)
        return amount >= 0
    except (ValueError, TypeError):
        return False

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:.2f}"

def get_current_month():
    """Get current month in YYYY-MM format"""
    return datetime.now().strftime('%Y-%m')

def get_date_range(start_date, end_date):
    """Get date range for filtering"""
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        return start, end
    except ValueError:
        return None, None

def handle_validation_error(func):
    """Decorator to handle validation errors"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return jsonify({'error': 'Validation error', 'message': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Internal error', 'message': str(e)}), 500
    return wrapper

def paginate_query(query, page=1, per_page=20):
    """Paginate database query"""
    try:
        page = int(page) if page else 1
        per_page = int(per_page) if per_page else 20
        per_page = min(per_page, 100)  # Limit max items per page
        
        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    except ValueError:
        return query.paginate(page=1, per_page=20, error_out=False)

def get_request_args():
    """Get and validate common request arguments"""
    return {
        'page': request.args.get('page', 1, type=int),
        'per_page': request.args.get('per_page', 20, type=int),
        'category': request.args.get('category'),
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
        'sort_by': request.args.get('sort_by', 'date'),
        'order': request.args.get('order', 'desc')
    }
