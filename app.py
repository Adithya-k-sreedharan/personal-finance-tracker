import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from models import db
from routes import api

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///expenses.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(api)
    
    # Create tables
    with app.app_context():
        db.create_all()
        
        # Add some default categories if they don't exist
        from models import Category
        default_categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Healthcare', 'Shopping', 'Other']
        
        for cat_name in default_categories:
            if not Category.query.filter_by(name=cat_name).first():
                category = Category(name=cat_name, description=f'Default {cat_name.lower()} category')
                db.session.add(category)
        
        db.session.commit()
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Expense Tracker API',
            'version': '1.0.0',
            'endpoints': {
                'expenses': '/api/expenses',
                'categories': '/api/categories',
                'monthly_limit': '/api/monthly-limit',
                'statistics': {
                    'total': '/api/stats/total',
                    'by_category': '/api/stats/by-category',
                    'monthly': '/api/stats/monthly'
                },
                'monthly_limit_status': {
                    'current': '/api/monthly-limit/current-status',
                    'check': '/api/monthly-limit/check'
                }
            }
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"Starting Expense Tracker API on port {port}")
    print(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
