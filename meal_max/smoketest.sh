#!/bin/bash

BASE_URL="http://localhost:5000/api"
ECHO_JSON=false

while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

#Check health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

#Check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database check failed."
    exit 1
  fi
}

clear_meals() {
  echo "Clearing meals"
  curl -s -X DELETE "$BASE_URL/clear-meals" | grep -q '"status": "success"'
}

create_meal() {
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Adding meal ($meal, $cuisine, $price, $difficulty) to the kitchen..."
  curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":\"$price\", \"difficulty\":$difficulty}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Meal added successfully."
  else
    echo "Failed to add meal."
    exit 1
  fi
}

delete_meal_by_id() {
  meal_id=$1

  echo "Deleting meal by ID ($meal)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi
}

get_leaderboard() {
  echo "Getting all meals in the leaderboard..."
  response=$(curl -s -X GET "$BASE_URL/get-leaderboard")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "All meals retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meals JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meals."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (ID $meal_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_name() {
  name=$1

  echo "Getting meal by name -- (Name: '$name')..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$name")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by name."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (by name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by name."
    exit 1
  fi
}

update_meal_stats() {
  meal_id=$1
  result=$2  # "win" or "loss"

  echo "Updating stats for meal ID ($meal_id) with result: $result..."
  response=$(curl -s -X PATCH "$BASE_URL/update-meal-stats/$meal_id" -H "Content-Type: application/json" \
    -d "{\"result\":\"$result\"}")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal stats updated successfully for ID ($meal_id)."
  else
    echo "Failed to update meal stats for ID ($meal_id)."
    exit 1
  fi
}


# Health checks
check_health
check_db

clear_meals

create_meal "Ravioli" "Italian" 10.0 "HIGH"
create_meal "Chicken Alfredo" "Italian-American" 15.0 "MED"
create_meal "Chicken Parm" "Italian-American" 20.0 "HIGH"
create_meal "SpaghettiOs" "American" 1.0 "LOW"

delete meal_by_id 1
get_leaderboard
get_meal_by_id 2
get_meal_by_name "Chicken Parm" 

update_meal_stats "SpaghettiOs" "loss"

echo "All tests passed successfully!"