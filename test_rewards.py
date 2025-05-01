import requests
import json

BASE_URL = 'http://localhost:8000'

def test_rewards_api():
    # First, get a token (you'll need to replace these with actual credentials)
    auth_data = {
        'email': 'test@example.com',
        'password': 'test_password'
    }
    
    # Get token
    response = requests.post(f'{BASE_URL}/api/auth/signin/', json=auth_data)
    if response.status_code != 200:
        print("Failed to get token:", response.text)
        return
    
    token = response.json()['tokens']['access']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test getting all rewards
    response = requests.get(f'{BASE_URL}/api/lms/rewards/', headers=headers)
    print("\nAll rewards:")
    print(json.dumps(response.json(), indent=2))
    
    # Test filtering by lesson
    response = requests.get(f'{BASE_URL}/api/lms/rewards/?lesson_id=1', headers=headers)
    print("\nRewards for lesson 1:")
    print(json.dumps(response.json(), indent=2))
    
    # Test filtering by course
    response = requests.get(f'{BASE_URL}/api/lms/rewards/?course_id=1', headers=headers)
    print("\nRewards for course 1:")
    print(json.dumps(response.json(), indent=2))
    
    # Test searching
    response = requests.get(f'{BASE_URL}/api/lms/rewards/?search=completion', headers=headers)
    print("\nSearch results for 'completion':")
    print(json.dumps(response.json(), indent=2))

if __name__ == '__main__':
    test_rewards_api() 