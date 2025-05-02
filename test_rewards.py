import requests
import json

BASE_URL = 'https://api.garaad.org'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ2MTA4Njg5LCJpYXQiOjE3NDYxMDc3ODksImp0aSI6IjFhNmZhNmI4NmY4OTQ1MzViYjE3OTk1OTZmMmNkNWVkIiwidXNlcl9pZCI6MTB9.D_fpTWSsolu_sqffb7sE3HmHfD6DnrFoTaKL2wlLxhA'

def test_rewards_api():
    headers = {'Authorization': f'Bearer {TOKEN}'}
    
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