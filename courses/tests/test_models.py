from django.test import TestCase
from django.core.exceptions import ValidationError
from courses.models import Category, Course, Lesson, LessonContentBlock, Problem

class LessonContentBlockTests(TestCase):
    def setUp(self):
        # Create necessary related objects
        self.category = Category.objects.create(
            id="test-category",
            title="Test Category",
            description="Test Category Description",
            image="test.jpg"
        )
        
        self.course = Course.objects.create(
            category=self.category,
            title="Test Course",
            description="Test Course Description"
        )
        
        self.lesson = Lesson.objects.create(
            course=self.course,
            title="Test Lesson",
            lesson_number=1
        )
        
        self.problem = Problem.objects.create(
            lesson=self.lesson,
            question_text="Test Question",
            question_type="multiple_choice",
            options=[
                {'id': '1', 'text': 'A'},
                {'id': '2', 'text': 'B'},
                {'id': '3', 'text': 'C'}
            ],
            correct_answer=[{'id': '1'}]
        )

    def test_create_text_block(self):
        """Test creating a text block with valid content"""
        block = LessonContentBlock.objects.create(
            lesson=self.lesson,
            block_type='text',
            content={
                'text': 'Test content',
                'format': 'markdown'
            },
            order=1
        )
        self.assertEqual(block.content['text'], 'Test content')
        self.assertEqual(block.content['format'], 'markdown')

    def test_create_problem_block(self):
        """Test creating a problem block with valid content"""
        block = LessonContentBlock.objects.create(
            lesson=self.lesson,
            block_type='problem',
            problem=self.problem,
            content={
                'introduction': 'Test introduction',
                'show_hints': True,
                'show_solution': False
            },
            order=1
        )
        self.assertEqual(block.content['introduction'], 'Test introduction')
        self.assertTrue(block.content['show_hints'])
        self.assertFalse(block.content['show_solution'])
        self.assertEqual(block.content['attempts_allowed'], 3)  # Default value
        self.assertEqual(block.content['points'], 10)  # Default value

    def test_problem_block_requires_problem(self):
        """Test that problem blocks require a Problem reference"""
        with self.assertRaises(ValidationError):
            LessonContentBlock.objects.create(
                lesson=self.lesson,
                block_type='problem',
                content={
                    'introduction': 'Test introduction'
                },
                order=1
            )

    def test_invalid_content_type(self):
        """Test that content must be a dictionary"""
        with self.assertRaises(ValidationError):
            LessonContentBlock.objects.create(
                lesson=self.lesson,
                block_type='text',
                content="invalid content",  # Should be a dict
                order=1
            )

    def test_default_content_initialization(self):
        """Test that default content is properly initialized"""
        block = LessonContentBlock.objects.create(
            lesson=self.lesson,
            block_type='text',
            order=1
        )
        self.assertIsInstance(block.content, dict)
        self.assertEqual(block.content['text'], '')
        self.assertEqual(block.content['format'], 'markdown')

    def test_problem_block_complete_content(self):
        """Test getting complete content for problem blocks"""
        block = LessonContentBlock.objects.create(
            lesson=self.lesson,
            block_type='problem',
            problem=self.problem,
            content={
                'introduction': 'Test introduction',
                'show_hints': True
            },
            order=1
        )
        complete_content = block.get_complete_content()
        
        # Check problem display settings
        self.assertEqual(complete_content['introduction'], 'Test introduction')
        self.assertTrue(complete_content['show_hints'])
        
        # Check problem data
        problem_data = complete_content['problem_data']
        self.assertEqual(problem_data['id'], self.problem.id)
        self.assertEqual(problem_data['question_text'], 'Test Question')
        self.assertEqual(problem_data['question_type'], 'multiple_choice')
        self.assertEqual(problem_data['options'], ['A', 'B', 'C'])

    def test_update_problem_block(self):
        """Test updating a problem block's content"""
        block = LessonContentBlock.objects.create(
            lesson=self.lesson,
            block_type='problem',
            problem=self.problem,
            content={
                'introduction': 'Initial introduction',
                'show_hints': True
            },
            order=1
        )
        
        # Update content
        block.content['introduction'] = 'Updated introduction'
        block.content['show_solution'] = True
        block.save()
        
        # Refresh from database
        block.refresh_from_db()
        self.assertEqual(block.content['introduction'], 'Updated introduction')
        self.assertTrue(block.content['show_solution'])
        self.assertTrue(block.content['show_hints'])  # Original value preserved 