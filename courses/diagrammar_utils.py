import json
from typing import Dict, List, Any

def state_matches(user_state: Dict, correct_state: Dict) -> bool:
    """
    Compares user's diagram state with a correct state
    """
    return json.dumps(user_state, sort_keys=True) == json.dumps(correct_state, sort_keys=True)

def get_feedback(user_state: Dict, correct_states: List[Dict]) -> Dict:
    """
    Provides feedback based on how close the user's state is to correct states
    """
    is_correct = any(
        state_matches(user_state, correct_state)
        for correct_state in correct_states
    )
    
    if is_correct:
        return {
            'is_correct': True,
            'message': 'Your diagram is correct!',
            'hint': None
        }
    
    # If not correct, provide a hint based on the closest match
    closest_state = find_closest_state(user_state, correct_states)
    return {
        'is_correct': False,
        'message': 'Try adjusting your diagram.',
        'hint': generate_hint(user_state, closest_state)
    }

def find_closest_state(user_state: Dict, correct_states: List[Dict]) -> Dict:
    """
    Finds the correct state that most closely matches the user's state
    """
    # Simple implementation - can be enhanced with more sophisticated matching
    return correct_states[0]

def generate_hint(user_state: Dict, correct_state: Dict) -> str:
    """
    Generates a hint based on differences between user state and correct state
    """
    # Simple implementation - can be enhanced with more sophisticated hint generation
    return "Check the positions of your elements." 