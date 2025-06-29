#!/bin/bash

# Expense Tracker API Test Script for Monthly Limits
BASE_URL="http://localhost:5000/api"

echo "=== Testing Monthly Limits API ==="
echo

# Test 1: Create a monthly limit
echo "1. Creating overall monthly limit for June 2025..."
curl -s -X POST $BASE_URL/monthly-limits \
  -H "Content-Type: application/json" \
  -d '{
    "year": 2025,
    "month": 6,
    "limit_amount": 3000.00
  }' | jq .

echo -e "\n"

# Test 2: Create category-specific limit
echo "2. Creating Food category limit for June 2025..."
curl -s -X POST $BASE_URL/monthly-limits \
  -H "Content-Type: application/json" \
  -d '{
    "year": 2025,
    "month": 6,
    "limit_amount": 600.00,
    "category": "Food"
  }' | jq .

echo -e "\n"

# Test 3: Get all monthly limits
echo "3. Getting all monthly limits..."
curl -s $BASE_URL/monthly-limits | jq .

echo -e "\n"

# Test 4: Add some expenses to test against limits
echo "4. Adding test expenses..."
curl -s -X POST $BASE_URL/expenses \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 45.00,
    "description": "Grocery shopping",
    "category": "Food",
    "date": "2025-06-28"
  }' | jq .

echo -e "\n"

curl -s -X POST $BASE_URL/expenses \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 25.00,
    "description": "Restaurant dinner",
    "category": "Food",
    "date": "2025-06-28"
  }' | jq .

echo -e "\n"

# Test 5: Check current month status
echo "5. Checking current month budget status..."
curl -s "$BASE_URL/monthly-limits/current-status?year=2025&month=6" | jq .

echo -e "\n"

# Test 6: Check if limits are exceeded
echo "6. Checking if monthly limits are exceeded..."
curl -s $BASE_URL/monthly-limits/check/2025/6 | jq .

echo -e "\n"

# Test 7: Try to create duplicate limit (should fail)
echo "7. Testing duplicate limit creation (should fail)..."
curl -s -X POST $BASE_URL/monthly-limits \
  -H "Content-Type: application/json" \
  -d '{
    "year": 2025,
    "month": 6,
    "limit_amount": 2500.00
  }' | jq .

echo -e "\n"

# Test 8: Update a monthly limit
echo "8. Updating monthly limit..."
LIMIT_ID=$(curl -s $BASE_URL/monthly-limits | jq -r '.[0].id')
if [ "$LIMIT_ID" != "null" ] && [ "$LIMIT_ID" != "" ]; then
  curl -s -X PUT $BASE_URL/monthly-limits/$LIMIT_ID \
    -H "Content-Type: application/json" \
    -d '{
      "year": 2025,
      "month": 6,
      "limit_amount": 3500.00
    }' | jq .
else
  echo "No limit found to update"
fi

echo -e "\n"

# Test 9: Test error handling - invalid month
echo "9. Testing error handling with invalid month..."
curl -s -X POST $BASE_URL/monthly-limits \
  -H "Content-Type: application/json" \
  -d '{
    "year": 2025,
    "month": 13,
    "limit_amount": 1000.00
  }' | jq .

echo -e "\n"

echo "=== Monthly Limits API Testing Complete ==="
