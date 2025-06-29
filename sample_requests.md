# Expense Tracker API - Sample Requests

## Monthly Limit

### Set Monthly Limit
```bash
# Set the monthly limit (creates if doesn't exist, updates if exists)
curl -X POST http://localhost:5000/api/monthly-limit \
  -H "Content-Type: application/json" \
  -d '{
    "limit_amount": 3000.00
  }'
```

### Get Monthly Limit
```bash
# Get the current monthly limit
curl http://localhost:5000/api/monthly-limit
```

### Update Monthly Limit
```bash
# Update the monthly limit
curl -X PUT http://localhost:5000/api/monthly-limit \
  -H "Content-Type: application/json" \
  -d '{
    "limit_amount": 3500.00
  }'
```

### Delete Monthly Limit
```bash
# Delete the monthly limit
curl -X DELETE http://localhost:5000/api/monthly-limit
```

### Check Current Month Status
```bash
# Check current month spending vs limit
curl http://localhost:5000/api/monthly-limit/current-status

# Check specific month
curl "http://localhost:5000/api/monthly-limit/current-status?year=2025&month=6"
```

### Check if Limit is Exceeded
```bash
# Check current month
curl http://localhost:5000/api/monthly-limit/check

# Check specific month
curl "http://localhost:5000/api/monthly-limit/check?year=2025&month=6"
```

## Expenses (existing functionality)

### Create an Expense
```bash
curl -X POST http://localhost:5000/api/expenses \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 25.50,
    "description": "Lunch at cafe",
    "category": "Food",
    "date": "2025-06-28"
  }'
```

### Get Expenses
```bash
# Get all expenses
curl http://localhost:5000/api/expenses

# Get expenses with limit
curl "http://localhost:5000/api/expenses?limit=10"

# Get expenses by category
curl "http://localhost:5000/api/expenses?category=Food"
```

### Update an Expense
```bash
curl -X PUT http://localhost:5000/api/expenses/1 \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 30.00,
    "description": "Updated lunch expense",
    "category": "Food",
    "date": "2025-06-28"
  }'
```

### Delete an Expense
```bash
curl -X DELETE http://localhost:5000/api/expenses/1
```

## Categories

### Create a Category
```bash
curl -X POST http://localhost:5000/api/categories \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Groceries",
    "description": "Food and household items"
  }'
```

### Get All Categories
```bash
curl http://localhost:5000/api/categories
```

### Get a Specific Category
```bash
curl http://localhost:5000/api/categories/1
```

### Update a Category
```bash
curl -X PUT http://localhost:5000/api/categories/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Food & Groceries",
    "description": "All food-related expenses including groceries and dining"
  }'
```

### Delete a Category
```bash
# Regular delete (fails if category has expenses)
curl -X DELETE http://localhost:5000/api/categories/1

# Force delete (moves expenses to "Other" category)
curl -X DELETE "http://localhost:5000/api/categories/1?force=true"
```

## Statistics

### Get Total Expenses
```bash
curl http://localhost:5000/api/stats/total
```

### Get Expenses by Category
```bash
curl http://localhost:5000/api/stats/by-category
```

### Get Monthly Expenses
```bash
curl http://localhost:5000/api/stats/monthly
```

## Example Workflow: Setting up Monthly Budget Tracking

1. **Set monthly limit:**
```bash
# Set overall monthly budget
curl -X POST http://localhost:5000/api/monthly-limit \
  -H "Content-Type: application/json" \
  -d '{"limit_amount": 3000.00}'
```

2. **Add some expenses:**
```bash
curl -X POST http://localhost:5000/api/expenses \
  -H "Content-Type: application/json" \
  -d '{"amount": 45.00, "description": "Grocery shopping", "category": "Food", "date": "2025-06-28"}'

curl -X POST http://localhost:5000/api/expenses \
  -H "Content-Type: application/json" \
  -d '{"amount": 25.00, "description": "Bus fare", "category": "Transportation", "date": "2025-06-28"}'

curl -X POST http://localhost:5000/api/expenses \
  -H "Content-Type: application/json" \
  -d '{"amount": 120.00, "description": "Electric bill", "category": "Utilities", "date": "2025-06-28"}'
```

3. **Check budget status:**
```bash
# Check current month status
curl http://localhost:5000/api/monthly-limit/current-status

# Check if limit is exceeded
curl http://localhost:5000/api/monthly-limit/check
```
