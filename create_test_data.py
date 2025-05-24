from courses.models import Category, Course, Lesson, LessonContentBlock, Problem, PracticeSet, PracticeSetProblem
from django.utils import timezone

# Create Category
category = Category.objects.create(
    id='python-programming',
    title='Python Programming',
    description='Learn Python programming from basics to advanced concepts',
    image='https://example.com/python.png',
    in_progress=False
)

# Create Course
course = Course.objects.create(
    category=category,
    title='Python Fundamentals',
    description='A comprehensive introduction to Python programming language',
    thumbnail='https://example.com/python-fundamentals.png',
    author_id='instructor1',
    is_published=True
)

# Create Lessons
lesson1 = Lesson.objects.create(
    course=course,
    title='Introduction to Python',
    lesson_number=1,
    estimated_time=30,
    is_published=True
)

lesson2 = Lesson.objects.create(
    course=course,
    title='Variables and Data Types',
    lesson_number=2,
    estimated_time=45,
    is_published=True
)

# Create Content Blocks for Lesson 1
LessonContentBlock.objects.create(
    lesson=lesson1,
    block_type='text',
    content={
        'text': 'Welcome to Python! Python is a high-level, interpreted programming language...',
        'format': 'markdown'
    },
    order=1
)

LessonContentBlock.objects.create(
    lesson=lesson1,
    block_type='code',
    content={
        'code': 'print("Hello, World!")',
        'language': 'python',
        'explanation': 'This is your first Python program!'
    },
    order=2
)

# Create Content Blocks for Lesson 2
LessonContentBlock.objects.create(
    lesson=lesson2,
    block_type='text',
    content={
        'text': 'Python has several built-in data types including numbers, strings, and booleans...',
        'format': 'markdown'
    },
    order=1
)

LessonContentBlock.objects.create(
    lesson=lesson2,
    block_type='code',
    content={
        'code': '''# Examples of Python variables
name = "Alice"
age = 25
height = 1.75
is_student = True''',
        'language': 'python',
        'explanation': 'Examples of different variable types in Python'
    },
    order=2
)

# Create Problems
problem1 = Problem.objects.create(
    question_text='What will be the output of print("Hello, " + "World!")?',
    question_type='single_choice',
    options=[
        {'id': '1', 'text': 'Hello, World!'},
        {'id': '2', 'text': 'HelloWorld!'},
        {'id': '3', 'text': 'Error'},
        {'id': '4', 'text': 'None'}
    ],
    correct_answer=[{'id': '1'}],
    explanation='The + operator concatenates strings in Python',
    difficulty='beginner'
)

problem2 = Problem.objects.create(
    question_text='Which of these is a valid variable name in Python?',
    question_type='multiple_choice',
    options=[
        {'id': '1', 'text': '123var'},
        {'id': '2', 'text': '_count'},
        {'id': '3', 'text': 'my-var'},
        {'id': '4', 'text': 'class'}
    ],
    correct_answer=[{'id': '2'}],
    explanation='Variable names cannot start with numbers, contain hyphens, or be Python keywords',
    difficulty='beginner'
)

# Create Practice Sets
practice_set1 = PracticeSet.objects.create(
    title='Python Basics Practice',
    lesson=lesson1,
    practice_type='lesson',
    difficulty_level='beginner',
    is_published=True
)

# Add problems to practice set
PracticeSetProblem.objects.create(
    practice_set=practice_set1,
    problem=problem1,
    order=1
)

PracticeSetProblem.objects.create(
    practice_set=practice_set1,
    problem=problem2,
    order=2
)

print("Test data created successfully!") 