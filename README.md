# Expense Tracker Backend

A simple expense tracker backend API built with Flask and SQLAlchemy.

## Features

- Add, update, delete, and view expenses
- Categorize expenses
- Get expense summaries and statistics
- RESTful API endpoints

## Database

This project uses **SQLite** - a lightweight, file-based database that requires **no setup**!

- ✅ **No installation needed** - SQLite is built into Python
- ✅ **No server required** - Database is just a file (`expenses.db`)
- ✅ **Zero configuration** - Works out of the box
- ✅ **Perfect for development** - Simple and portable

The database file will be automatically created when you first run the application.

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file (optional):
   ```
   FLASK_ENV=development
   DATABASE_URL=sqlite:///expenses.db
   ```

5. Run the application:
   ```bash
   python app.py
   ```

   The SQLite database (`expenses.db`) will be automatically created with sample data!

## API Endpoints

### Expenses
- `GET /api/expenses` - Get all expenses
- `POST /api/expenses` - Create a new expense
- `GET /api/expenses/<id>` - Get a specific expense
- `PUT /api/expenses/<id>` - Update an expense
- `DELETE /api/expenses/<id>` - Delete an expense

### Categories
- `GET /api/categories` - Get all categories
- `POST /api/categories` - Create a new category

### Statistics
- `GET /api/stats/total` - Get total expenses
- `GET /api/stats/by-category` - Get expenses grouped by category


## Database Management

The project includes helpful database utilities:

```bash
# Initialize empty database
python db_utils.py init

# Reset database (delete all data and recreate tables)
python db_utils.py reset
