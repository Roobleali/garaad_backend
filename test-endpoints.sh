#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base URL for the API - get port from .env or default to 3000
PORT=$(grep PORT .env | cut -d '=' -f2 || echo 3000)
BASE_URL="http://localhost:${PORT}/api"

# JWT token for authenticated requests
TOKEN=""

# Function to check if the endpoint exists
check_endpoint() {
  local endpoint=$1
  local method=${2:-GET}
  local expected_status=${3:-200}
  
  echo -e "${YELLOW}Testing $method $endpoint${NC}"
  
  if [ "$method" = "GET" ]; then
    response=$(curl -s -o /dev/null -w "%{http_code}" -X $method -H "Authorization: Bearer $TOKEN" $BASE_URL$endpoint)
  else
    response=$(curl -s -o /dev/null -w "%{http_code}" -X $method -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" $BASE_URL$endpoint -d '{}')
  fi
  
  if [ "$response" = "$expected_status" ]; then
    echo -e "${GREEN}✓ $method $endpoint - Status: $response${NC}"
    return 0
  else
    echo -e "${RED}✗ $method $endpoint - Expected: $expected_status, Got: $response${NC}"
    return 1
  fi
}

# Login to get token
login() {
  echo "Logging in to get JWT token..."
  
  response=$(curl -s -X POST -H "Content-Type: application/json" $BASE_URL/auth/login -d '{"email":"admin@example.com","password":"password123"}')
  echo "Login response: $response"
  
  # Extract token from response
  TOKEN=$(echo $response | grep -o '"token":"[^"]*' | sed 's/"token":"//')
  
  if [ -z "$TOKEN" ]; then
    echo -e "${RED}Failed to get token. Please check credentials.${NC}"
    exit 1
  else
    echo -e "${GREEN}Successfully logged in and got token.${NC}"
  fi
}

# Main test function
run_tests() {
  echo "Starting API endpoint tests..."
  
  # Auth endpoints
  check_endpoint "/auth/login" "POST" 200
  check_endpoint "/auth/register" "POST" 400 # Should fail with 400 without proper data
  check_endpoint "/auth/me" "GET" 401 # Should fail without token
  
  # Login to get token for authenticated endpoints
  login
  
  # Auth endpoints with token
  check_endpoint "/auth/me" "GET" 200
  
  # Health check
  check_endpoint "/health" "GET" 200
  
  echo -e "\n${YELLOW}Testing Legacy URL Structure${NC}"
  
  # Legacy League endpoints
  check_endpoint "/league/status" "GET" 200
  check_endpoint "/league/leaderboard" "GET" 200
  check_endpoint "/league" "GET" 200
  check_endpoint "/league/123" "GET" 404 # Should fail with 404 for non-existent league
  
  # Legacy Gamification endpoints
  check_endpoint "/gamification/status" "GET" 200
  check_endpoint "/gamification/use_energy" "POST" 200
  
  # Legacy Notification endpoints
  check_endpoint "/notifications" "GET" 200
  check_endpoint "/notifications/unread_count" "GET" 200
  check_endpoint "/notifications/mark_all_read" "POST" 200
  
  # Legacy Course endpoints
  check_endpoint "/courses" "GET" 200
  check_endpoint "/courses/123" "GET" 404 # Should fail with 404 for non-existent course
  
  # Legacy Lesson endpoints
  check_endpoint "/lessons" "GET" 200
  check_endpoint "/lessons/123" "GET" 404 # Should fail with 404 for non-existent lesson
  
  # Legacy Problem endpoints
  check_endpoint "/problems" "GET" 200
  check_endpoint "/problems/123" "GET" 404 # Should fail with 404 for non-existent problem
  
  echo -e "\n${YELLOW}Testing Django-Compatible URL Structure${NC}"
  
  # Django-style League endpoints
  check_endpoint "/league/leagues/status/" "GET" 200
  check_endpoint "/league/leagues/leaderboard/" "GET" 200
  check_endpoint "/league/leagues/" "GET" 200
  check_endpoint "/league/leagues/123/" "GET" 404 # Should fail with 404 for non-existent league
  
  # Django-style Gamification endpoints
  check_endpoint "/gamification/status/" "GET" 200
  check_endpoint "/gamification/use_energy/" "POST" 200
  
  # Django-style LMS endpoints
  check_endpoint "/lms/notifications/" "GET" 200
  check_endpoint "/lms/notifications/unread_count/" "GET" 200
  check_endpoint "/lms/notifications/mark_all_read/" "POST" 200
  
  check_endpoint "/lms/courses/" "GET" 200
  check_endpoint "/lms/courses/123/" "GET" 404 # Should fail with 404 for non-existent course
  
  check_endpoint "/lms/lessons/" "GET" 200
  check_endpoint "/lms/lessons/123/" "GET" 404 # Should fail with 404 for non-existent lesson
  
  check_endpoint "/lms/problems/" "GET" 200
  check_endpoint "/lms/problems/123/" "GET" 404 # Should fail with 404 for non-existent problem
  
  echo -e "\n${GREEN}All tests completed!${NC}"
}

# Run the tests
run_tests 