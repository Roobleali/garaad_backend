from courses.models import Lesson, Module

def create_test_lessons():
    module = Module.objects.get(id='frontend-basics')
    
    # Lesson 1: HTML Structure
    Lesson.objects.create(
        module=module,
        title='HTML Structure',
        description='Learn about HTML document structure',
        type='multiple-choice',
        problem={
            'question': 'What is the correct HTML5 document structure?',
            'options': [
                '<!DOCTYPE html><html><head><title>Title</title></head><body></body></html>',
                '<html><head><title>Title</title></head><body></body></html>',
                '<!DOCTYPE><html><head><title>Title</title></head><body></body></html>'
            ],
            'solution': '<!DOCTYPE html><html><head><title>Title</title></head><body></body></html>',
            'explanation': 'HTML5 requires the DOCTYPE declaration and proper nesting of html, head, and body tags.'
        }
    )
    
    # Lesson 2: CSS Selectors
    Lesson.objects.create(
        module=module,
        title='CSS Selectors',
        description='Learn about CSS selectors',
        type='multiple-choice',
        problem={
            'question': 'Which CSS selector has the highest specificity?',
            'options': ['#id', '.class', 'element'],
            'solution': '#id',
            'explanation': 'ID selectors have the highest specificity in CSS, followed by class selectors and then element selectors.'
        }
    )
    
    # Lesson 3: JavaScript Variables
    Lesson.objects.create(
        module=module,
        title='JavaScript Variables',
        description='Learn about JavaScript variables',
        type='multiple-choice',
        problem={
            'question': 'What is the difference between let and var in JavaScript?',
            'options': [
                'let has block scope, var has function scope',
                'let has function scope, var has block scope',
                'There is no difference'
            ],
            'solution': 'let has block scope, var has function scope',
            'explanation': 'Variables declared with let are block-scoped, while variables declared with var are function-scoped.'
        }
    )
    
    # Lesson 4: CSS Box Model
    Lesson.objects.create(
        module=module,
        title='CSS Box Model',
        description='Learn about the CSS box model',
        type='multiple-choice',
        problem={
            'question': 'What are the components of the CSS box model?',
            'options': [
                'Content, padding, border, margin',
                'Content, border, margin',
                'Content, padding, margin'
            ],
            'solution': 'Content, padding, border, margin',
            'explanation': 'The CSS box model consists of content, padding, border, and margin, in that order from inside to outside.'
        }
    )
    
    # Lesson 5: JavaScript Functions
    Lesson.objects.create(
        module=module,
        title='JavaScript Functions',
        description='Learn about JavaScript functions',
        type='multiple-choice',
        problem={
            'question': 'What is the difference between function declaration and function expression?',
            'options': [
                'Function declarations are hoisted, function expressions are not',
                'Function expressions are hoisted, function declarations are not',
                'Both are hoisted in the same way'
            ],
            'solution': 'Function declarations are hoisted, function expressions are not',
            'explanation': 'Function declarations are hoisted to the top of their scope, while function expressions are not hoisted.'
        }
    )

if __name__ == '__main__':
    create_test_lessons() 