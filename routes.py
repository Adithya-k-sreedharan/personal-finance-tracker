from flask import Blueprint, request, jsonify
from models import db, Expense, Category, MonthlyLimit
from schemas import expense_schema, expenses_schema, category_schema, categories_schema, monthly_limit_schema, monthly_limits_schema
from marshmallow import ValidationError
from datetime import datetime
from sqlalchemy import func

api = Blueprint('api', __name__, url_prefix='/api')

# Expense endpoints
@api.route('/expenses', methods=['GET'])
def get_expenses():
    """Get all expenses with optional filtering"""
    category_filter = request.args.get('category')
    limit = request.args.get('limit', type=int)
    
    query = Expense.query
    
    if category_filter:
        query = query.filter(Expense.category == category_filter)
    
    query = query.order_by(Expense.date.desc())
    
    if limit:
        query = query.limit(limit)
    
    expenses = query.all()
    return jsonify(expenses_schema.dump(expenses))

@api.route('/expenses', methods=['POST'])
def create_expense():
    """Create a new expense"""
    try:
        data = expense_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    expense = Expense(**data)
    
    # Create category if it doesn't exist
    category = Category.query.filter_by(name=data['category']).first()
    if not category:
        category = Category(name=data['category'])
        db.session.add(category)
        db.session.commit()
        expense.category_id = category.id
    else:
        expense.category_id = category.id
    
    db.session.add(expense)
    db.session.commit()
    
    return jsonify(expense_schema.dump(expense)), 201

@api.route('/expenses/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    """Get a specific expense"""
    expense = Expense.query.get_or_404(expense_id)
    return jsonify(expense_schema.dump(expense))

@api.route('/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    """Update an expense"""
    expense = Expense.query.get_or_404(expense_id)
    
    try:
        data = expense_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    # Update expense fields
    for key, value in data.items():
        setattr(expense, key, value)
    
    expense.updated_at = datetime.utcnow()
    
    # Update category if changed
    if 'category' in data:
        category = Category.query.filter_by(name=data['category']).first()
        if not category:
            category = Category(name=data['category'])
            db.session.add(category)
            db.session.commit()
        expense.category_id = category.id
    
    db.session.commit()
    
    return jsonify(expense_schema.dump(expense))

@api.route('/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """Delete an expense"""
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    
    return jsonify({'message': 'Expense deleted successfully'}), 200

# Category endpoints
@api.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    categories = Category.query.all()
    return jsonify(categories_schema.dump(categories))

@api.route('/categories', methods=['POST'])
def create_category():
    """Create a new category"""
    try:
        data = category_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    # Check if category already exists
    existing_category = Category.query.filter_by(name=data['name']).first()
    if existing_category:
        return jsonify({'error': 'Category already exists'}), 409
    
    category = Category(**data)
    db.session.add(category)
    db.session.commit()
    
    return jsonify(category_schema.dump(category)), 201

@api.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Get a specific category"""
    category = Category.query.get_or_404(category_id)
    return jsonify(category_schema.dump(category))

@api.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """Update a category"""
    category = Category.query.get_or_404(category_id)
    
    try:
        data = category_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    # Check if another category with the same name exists (excluding current category)
    existing_category = Category.query.filter(
        Category.name == data['name'],
        Category.id != category_id
    ).first()
    
    if existing_category:
        return jsonify({'error': 'Another category with this name already exists'}), 409
    
    # Update category fields
    category.name = data['name']
    if 'description' in data:
        category.description = data['description']
    
    # Update all expenses that reference the old category name
    old_name = category.name
    if old_name != data['name']:
        expenses_to_update = Expense.query.filter_by(category=old_name).all()
        for expense in expenses_to_update:
            expense.category = data['name']
    
    db.session.commit()
    
    return jsonify(category_schema.dump(category))

@api.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Delete a category"""
    category = Category.query.get_or_404(category_id)
    
    # Check if there are expenses using this category
    expense_count = Expense.query.filter_by(category=category.name).count()
    
    if expense_count > 0:
        return jsonify({
            'error': f'Cannot delete category. {expense_count} expenses are using this category.',
            'suggestion': 'Move expenses to another category first or use force=true parameter'
        }), 409
    
    # Check for force delete parameter
    force_delete = request.args.get('force', '').lower() == 'true'
    
    if force_delete and expense_count > 0:
        # Move all expenses to "Other" category
        other_category = Category.query.filter_by(name='Other').first()
        if not other_category:
            other_category = Category(name='Other', description='Uncategorized expenses')
            db.session.add(other_category)
            db.session.commit()
        
        # Update all expenses to use "Other" category
        expenses_to_update = Expense.query.filter_by(category=category.name).all()
        for expense in expenses_to_update:
            expense.category = 'Other'
            expense.category_id = other_category.id
    
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({'message': 'Category deleted successfully'}), 200

# Statistics endpoints
@api.route('/stats/total', methods=['GET'])
def get_total_expenses():
    """Get total expense amount"""
    total = db.session.query(func.sum(Expense.amount)).scalar() or 0
    count = Expense.query.count()
    
    return jsonify({
        'total_amount': total,
        'total_count': count
    })

@api.route('/stats/by-category', methods=['GET'])
def get_expenses_by_category():
    """Get expenses grouped by category"""
    results = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label('total_amount'),
        func.count(Expense.id).label('count')
    ).group_by(Expense.category).all()
    
    data = [
        {
            'category': result.category,
            'total_amount': float(result.total_amount),
            'count': result.count
        }
        for result in results
    ]
    
    return jsonify(data)

@api.route('/stats/monthly', methods=['GET'])
def get_monthly_expenses():
    """Get expenses by month"""
    results = db.session.query(
        func.strftime('%Y-%m', Expense.date).label('month'),
        func.sum(Expense.amount).label('total_amount'),
        func.count(Expense.id).label('count')
    ).group_by(func.strftime('%Y-%m', Expense.date)).order_by('month').all()
    
    data = [
        {
            'month': result.month,
            'total_amount': float(result.total_amount),
            'count': result.count
        }
        for result in results
    ]
    
    return jsonify(data)

# Monthly Limit endpoints
@api.route('/monthly-limit', methods=['GET'])
def get_monthly_limit():
    """Get the current monthly limit"""
    limit = MonthlyLimit.query.first()
    if not limit:
        return jsonify({'message': 'No monthly limit set'}), 404
    return jsonify(monthly_limit_schema.dump(limit))

@api.route('/monthly-limit', methods=['POST'])
def create_monthly_limit():
    """Create or update the monthly limit"""
    try:
        data = monthly_limit_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    # Check if a limit already exists
    existing_limit = MonthlyLimit.query.first()
    
    if existing_limit:
        # Update existing limit
        existing_limit.limit_amount = data['limit_amount']
        existing_limit.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify(monthly_limit_schema.dump(existing_limit)), 200
    else:
        # Create new limit
        monthly_limit = MonthlyLimit(**data)
        db.session.add(monthly_limit)
        db.session.commit()
        return jsonify(monthly_limit_schema.dump(monthly_limit)), 201

@api.route('/monthly-limit', methods=['PUT'])
def update_monthly_limit():
    """Update the monthly limit"""
    limit = MonthlyLimit.query.first()
    if not limit:
        return jsonify({'error': 'No monthly limit exists. Create one first.'}), 404
    
    try:
        data = monthly_limit_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    limit.limit_amount = data['limit_amount']
    limit.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(monthly_limit_schema.dump(limit))

@api.route('/monthly-limit', methods=['DELETE'])
def delete_monthly_limit():
    """Delete the monthly limit"""
    limit = MonthlyLimit.query.first()
    if not limit:
        return jsonify({'error': 'No monthly limit exists'}), 404
    
    db.session.delete(limit)
    db.session.commit()
    
    return jsonify({'message': 'Monthly limit deleted successfully'}), 200

@api.route('/monthly-limit/current-status', methods=['GET'])
def get_current_month_status():
    """Get current month spending vs the monthly limit"""
    year = request.args.get('year', type=int, default=datetime.now().year)
    month = request.args.get('month', type=int, default=datetime.now().month)
    
    # Get the monthly limit
    limit = MonthlyLimit.query.first()
    if not limit:
        return jsonify({'error': 'No monthly limit set'}), 404
    
    # Get expenses for the specified month
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date()
    else:
        end_date = datetime(year, month + 1, 1).date()
    
    # Calculate total spending for the month
    total_spent = db.session.query(func.sum(Expense.amount)).filter(
        Expense.date >= start_date,
        Expense.date < end_date
    ).scalar() or 0
    
    remaining = limit.limit_amount - total_spent
    percentage_used = (total_spent / limit.limit_amount * 100) if limit.limit_amount > 0 else 0
    
    result = {
        'year': year,
        'month': month,
        'limit_amount': limit.limit_amount,
        'total_spent': float(total_spent),
        'remaining': float(remaining),
        'percentage_used': round(percentage_used, 2),
        'is_exceeded': total_spent > limit.limit_amount
    }
    
    return jsonify(result)

@api.route('/monthly-limit/check', methods=['GET'])
def check_monthly_limit():
    """Check if monthly limit is exceeded for current or specified month"""
    year = request.args.get('year', type=int, default=datetime.now().year)
    month = request.args.get('month', type=int, default=datetime.now().month)
    
    # Validate month parameter
    if month < 1 or month > 12:
        return jsonify({'error': 'Invalid month. Must be between 1 and 12.'}), 400
    
    # Get the monthly limit
    limit = MonthlyLimit.query.first()
    if not limit:
        return jsonify({'error': 'No monthly limit set'}), 404
    
    # Get expenses for the specified month
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date()
    else:
        end_date = datetime(year, month + 1, 1).date()
    
    # Calculate total spending for the month
    total_spent = db.session.query(func.sum(Expense.amount)).filter(
        Expense.date >= start_date,
        Expense.date < end_date
    ).scalar() or 0
    
    is_exceeded = total_spent > limit.limit_amount
    
    result = {
        'year': year,
        'month': month,
        'limit_amount': limit.limit_amount,
        'total_spent': float(total_spent),
        'is_exceeded': is_exceeded,
        'excess_amount': float(max(0, total_spent - limit.limit_amount)) if is_exceeded else 0
    }
    
    return jsonify(result)
