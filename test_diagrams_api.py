#!/usr/bin/env python3
"""
Test script for the new Diagrams API functionality.
This script demonstrates how the frontend should interact with the backend
for both single and multiple diagram configurations.
"""

# Example payloads for testing the API

# Single Diagram Format (Backward Compatibility)
single_diagram_payload = {
    "lesson": 123,
    "question_text": "What is the weight?",
    "question_type": "diagram",
    "options": [
        {"id": "a", "text": "15 kg"},
        {"id": "b", "text": "20 kg"},
        {"id": "c", "text": "25 kg"},
        {"id": "d", "text": "30 kg"}
    ],
    "correct_answer": [{"id": "a"}],
    "explanation": "The scale shows 15 kg when balanced.",
    "content": {},
    "diagram_config": {
        "diagram_id": 101,
        "diagram_type": "scale",
        "scale_weight": 15,
        "objects": [
            {
                "type": "cube",
                "color": "#4F8EF7",
                "text_color": "#FFFFFF",
                "number": 5,
                "position": "left",
                "layout": {
                    "rows": 2,
                    "columns": 3,
                    "position": "center",
                    "alignment": "center"
                },
                "weight_value": None
            }
        ]
    },
    "diagrams": None,  # Should be null for single diagram format
    "xp": 10
}

# Multiple Diagrams Format (New Feature)
multiple_diagrams_payload = {
    "lesson": 123,
    "question_text": "Based on the two scales, what is the weight of 1 circle?",
    "question_type": "diagram", 
    "options": [
        {"id": "a", "text": "2 kg"},
        {"id": "b", "text": "3 kg"},
        {"id": "c", "text": "4 kg"},
        {"id": "d", "text": "5 kg"}
    ],
    "correct_answer": [{"id": "c"}],
    "explanation": "By solving the equations from both scales, 1 circle weighs 4 kg.",
    "content": {},
    "diagram_config": None,  # Should be null for multiple diagrams format
    "diagrams": [
        {
            "diagram_id": 101,
            "diagram_type": "scale",
            "scale_weight": 16,
            "objects": [
                {
                    "type": "cube",
                    "color": "#4F8EF7",
                    "text_color": "#FFFFFF",
                    "number": 2,
                    "position": "left",
                    "layout": {
                        "rows": 2,
                        "columns": 1,
                        "position": "center",
                        "alignment": "center"
                    },
                    "weight_value": None
                },
                {
                    "type": "triangle",
                    "color": "#9B59B6",
                    "text_color": "#FFFFFF",
                    "number": 10,
                    "position": "right",
                    "layout": {
                        "rows": 1,
                        "columns": 1,
                        "position": "center",
                        "alignment": "center"
                    },
                    "weight_value": None
                }
            ]
        },
        {
            "diagram_id": 102,
            "diagram_type": "scale",
            "scale_weight": 14,
            "objects": [
                {
                    "type": "circle",
                    "color": "#2ECC71",
                    "text_color": "#FFFFFF",
                    "number": 1,
                    "position": "left",
                    "layout": {
                        "rows": 1,
                        "columns": 1,
                        "position": "center",
                        "alignment": "center"
                    },
                    "weight_value": None
                },
                {
                    "type": "trapezoid_weight",
                    "color": "#9B59B6",
                    "text_color": "#FFFFFF",
                    "number": 4,
                    "position": "right",
                    "layout": {
                        "rows": 2,
                        "columns": 2,
                        "position": "center",
                        "alignment": "center"
                    },
                    "weight_value": 5
                }
            ]
        }
    ],
    "xp": 15
}

# Invalid payload - both formats used simultaneously (should fail)
invalid_payload = {
    "lesson": 123,
    "question_text": "This should fail validation",
    "question_type": "diagram",
    "diagram_config": {"diagram_id": 1, "diagram_type": "scale", "scale_weight": 10, "objects": []},
    "diagrams": [{"diagram_id": 2, "diagram_type": "scale", "scale_weight": 20, "objects": []}],
    "options": [],
    "correct_answer": [],
    "explanation": "",
    "content": {},
    "xp": 10
}

def test_api_endpoints():
    """
    Example of how to test the API endpoints.
    Replace with actual HTTP requests in your testing environment.
    """
    
    print("=== Testing Single Diagram Format ===")
    print("POST /api/lms/problems/")
    print(f"Payload: {single_diagram_payload}")
    print("Expected: HTTP 201 Created with problem data")
    print()
    
    print("=== Testing Multiple Diagrams Format ===")
    print("POST /api/lms/problems/")
    print(f"Payload: {multiple_diagrams_payload}")
    print("Expected: HTTP 201 Created with problem data")
    print()
    
    print("=== Testing Invalid Format (Both Used) ===")
    print("POST /api/lms/problems/")
    print(f"Payload: {invalid_payload}")
    print("Expected: HTTP 400 Bad Request with validation error")
    print()

def expected_response_format():
    """
    Shows the expected response format from the API
    """
    
    print("=== Expected Response Format ===")
    
    single_response = {
        "id": 456,
        "lesson": 123,
        "question_text": "What is the weight?",
        "question_type": "diagram",
        "options": [{"id": "a", "text": "15 kg"}],
        "correct_answer": [{"id": "a"}],
        "explanation": "The scale shows 15 kg when balanced.",
        "content": {},
        "diagram_config": {
            "diagram_id": 101,
            "diagram_type": "scale",
            "scale_weight": 15,
            "objects": [...]
        },
        "diagrams": None,  # Null for single diagram format
        "xp": 10,
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z"
    }
    
    multiple_response = {
        "id": 457,
        "lesson": 123,
        "question_text": "Based on the two scales, what is the weight of 1 circle?",
        "question_type": "diagram",
        "options": [{"id": "c", "text": "4 kg"}],
        "correct_answer": [{"id": "c"}],
        "explanation": "By solving the equations from both scales, 1 circle weighs 4 kg.",
        "content": {},
        "diagram_config": None,  # Null for multiple diagrams format
        "diagrams": [
            {
                "diagram_id": 101,
                "diagram_type": "scale",
                "scale_weight": 16,
                "objects": [...]
            },
            {
                "diagram_id": 102,
                "diagram_type": "scale", 
                "scale_weight": 14,
                "objects": [...]
            }
        ],
        "xp": 15,
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z"
    }
    
    print(f"Single Diagram Response: {single_response}")
    print()
    print(f"Multiple Diagrams Response: {multiple_response}")

if __name__ == "__main__":
    test_api_endpoints()
    print()
    expected_response_format() 