import os
import django
import requests
import json
import time
from requests.exceptions import ConnectionError
from django.contrib.auth import get_user_model

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()

from courses.models import Problem, DiagrammarContent

def create_test_user():
    """Create a test user and get authentication token"""
    User = get_user_model()
    username = "test_user"
    email = "test@example.com"
    password = "test_password"
    
    # Create user if doesn't exist
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': email}
    )
    if created:
        user.set_password(password)
        user.save()
    
    # Get authentication token
    response = requests.post(
        'http://127.0.0.1:8000/api/auth/signin/',
        json={
            'username': username,
            'email': email,
            'password': password
        }
    )
    
    if response.status_code == 200:
        print(f"Full response: {response.json()}")
        response_data = response.json()
        if 'tokens' in response_data and 'access' in response_data['tokens']:
            return response_data['tokens']['access']
        else:
            print("No access token found in response")
            raise Exception("No access token found in response")
    else:
        print(f"Authentication failed: {response.status_code}")
        print(f"Response: {response.text}")
        raise Exception("Failed to get authentication token")

def create_test_problem():
    """Create a test problem with Diagrammar content"""
    # Create the problem
    problem = Problem.objects.create(
        question_text="Draw a simple graph with two connected nodes",
        question_type="diagrammar",
        correct_answer={"type": "diagrammar"}
    )
    
    # Create Diagrammar content
    diagrammar_content = DiagrammarContent.objects.create(
        problem=problem,
        diagram_definition={
            "nodes": [
                {
                    "id": "node1",
                    "type": "circle",
                    "position": {"x": 100, "y": 100},
                    "data": {"label": "A"}
                },
                {
                    "id": "node2",
                    "type": "circle",
                    "position": {"x": 300, "y": 100},
                    "data": {"label": "B"}
                }
            ],
            "edges": [
                {
                    "id": "edge1",
                    "source": "node1",
                    "target": "node2"
                }
            ]
        },
        correct_states=[
            {
                "nodes": [
                    {
                        "id": "node1",
                        "type": "circle",
                        "position": {"x": 100, "y": 100},
                        "data": {"label": "A"}
                    },
                    {
                        "id": "node2",
                        "type": "circle",
                        "position": {"x": 300, "y": 100},
                        "data": {"label": "B"}
                    }
                ],
                "edges": [
                    {
                        "id": "edge1",
                        "source": "node1",
                        "target": "node2"
                    }
                ]
            }
        ]
    )
    
    return problem

def test_diagrammar_endpoint(problem_id, auth_token):
    """Test the Diagrammar validation endpoint"""
    base_url = "http://127.0.0.1:8000/api/lms"  # Using 127.0.0.1 instead of localhost
    url = f"{base_url}/problems/{problem_id}/validate-diagrammar/"
    headers = {'Authorization': f'Bearer {auth_token}'}
    
    # Test with correct state
    correct_state = {
        "state": {
            "nodes": [
                {
                    "id": "node1",
                    "type": "circle",
                    "position": {"x": 100, "y": 100},
                    "data": {"label": "A"}
                },
                {
                    "id": "node2",
                    "type": "circle",
                    "position": {"x": 300, "y": 100},
                    "data": {"label": "B"}
                }
            ],
            "edges": [
                {
                    "id": "edge1",
                    "source": "node1",
                    "target": "node2"
                }
            ]
        }
    }
    
    # Test with incorrect state
    incorrect_state = {
        "state": {
            "nodes": [
                {
                    "id": "node1",
                    "type": "circle",
                    "position": {"x": 100, "y": 100},
                    "data": {"label": "A"}
                }
            ],
            "edges": []
        }
    }
    
    # Function to make request with retry
    def make_request(state, description):
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                print(f"\nTesting with {description}:")
                print(f"URL: {url}")
                print(f"Request body: {json.dumps(state, indent=2)}")
                
                response = requests.post(url, json=state, headers=headers)
                print(f"Status Code: {response.status_code}")
                print(f"Raw Response: {response.text}")
                try:
                    print(f"JSON Response: {response.json()}")
                except:
                    print("Could not parse response as JSON")
                return response
            except ConnectionError as e:
                if attempt < max_retries - 1:
                    print(f"Connection failed, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(f"Failed to connect after {max_retries} attempts: {e}")
                    raise
            except Exception as e:
                print(f"Error: {e}")
                raise
    
    # Make requests with retry
    make_request(correct_state, "correct state")
    make_request(incorrect_state, "incorrect state")

if __name__ == "__main__":
    # Get authentication token
    print("Getting authentication token...")
    auth_token = create_test_user()
    print("Got authentication token")
    
    # Create test problem
    problem = create_test_problem()
    print(f"Created test problem with ID: {problem.id}")
    
    # Test the endpoint
    test_diagrammar_endpoint(problem.id, auth_token) 