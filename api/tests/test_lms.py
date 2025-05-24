from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from courses.models import Course, Lesson, Category, LessonContentBlock, Problem
from django.contrib.auth import get_user_model

User = get_user_model()

class LMSTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        # Create test category
        self.category = Category.objects.create(
            id='programming',
            title='Programming',
            description='Learn programming languages',
            image='programming.jpg'
        )

        # Create test course
        self.course = Course.objects.create(
            category=self.category,
            title='Python Programming',
            description='Learn Python from scratch',
            author_id=str(self.user.id),
            is_published=True
        )

        # Create test lesson
        self.lesson = Lesson.objects.create(
            course=self.course,
            title='Python Data Types',
            lesson_number=1,
            estimated_time=30,
            is_published=True
        )

        # Create test problem
        self.problem = Problem.objects.create(
            lesson=self.lesson,
            question_text='What is the data type of the value 42?',
            question_type='single_choice',
            options=[
                {'id': '1', 'text': 'string'},
                {'id': '2', 'text': 'integer'},
                {'id': '3', 'text': 'float'},
                {'id': '4', 'text': 'boolean'}
            ],
            correct_answer=[{'id': '2'}],
            explanation='42 is a whole number, which is represented as an integer in Python.',
            order=1
        )

    def test_list_lessons(self):
        """Test retrieving a list of lessons"""
        url = reverse('lesson-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Python Data Types')

    def test_create_lesson(self):
        """Test creating a new lesson"""
        url = reverse('lesson-list')
        data = {
            'course': self.course.id,
            'title': 'New Lesson',
            'lesson_number': 2,
            'estimated_time': 25,
            'is_published': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        self.assertEqual(Lesson.objects.get(title='New Lesson').title, 'New Lesson')

    def test_course_lessons(self):
        """Test retrieving lessons for a specific course"""
        url = reverse('lesson-list')
        response = self.client.get(url, {'course': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Python Data Types')

    def test_get_course_through_api(self):
        """Test retrieving course through API endpoint"""
        url = reverse('course-detail', kwargs={'pk': self.course.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Python Programming')
        self.assertEqual(response.data['description'], 'Learn Python from scratch')
        self.assertTrue(response.data['is_published'])

    def test_get_lesson_through_api(self):
        """Test retrieving lesson through API endpoint"""
        url = reverse('lesson-detail', kwargs={'pk': self.lesson.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Python Data Types')
        self.assertEqual(response.data['lesson_number'], 1)
        self.assertEqual(response.data['estimated_time'], 30)
        self.assertTrue(response.data['is_published'])

    def test_list_courses(self):
        """Test retrieving a list of courses"""
        url = reverse('course-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Python Programming')

    def test_create_course(self):
        """Test creating a new course"""
        url = reverse('course-list')
        data = {
            'category': self.category.id,
            'title': 'New Course',
            'description': 'New Description',
            'author_id': str(self.user.id),
            'is_published': False
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)
        self.assertEqual(Course.objects.get(slug='new-course').title, 'New Course')

    def test_retrieve_course(self):
        """Test retrieving a specific course"""
        url = reverse('course-detail', kwargs={'pk': self.course.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Python Programming')

    def test_update_course(self):
        """Test updating a course"""
        url = reverse('course-detail', kwargs={'pk': self.course.id})
        data = {
            'category': self.category.id,
            'title': 'Updated Course',
            'description': 'Updated Description',
            'author_id': str(self.user.id),
            'is_published': True
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Updated Course')

    def test_unauthorized_access(self):
        """Test that unauthorized users cannot create resources"""
        self.client.force_authenticate(user=None)
        
        # Try to create a course
        url = reverse('course-list')
        data = {
            'category': self.category.id,
            'title': 'Unauthorized Course',
            'description': 'This should fail',
            'author_id': str(self.user.id),
            'is_published': False
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_course_filtering(self):
        """Test filtering courses by category"""
        url = reverse('course-list')
        response = self.client.get(url, {'category': self.category.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Python Programming')

    def test_category_creation(self):
        """Test that the category was created correctly"""
        self.assertEqual(self.category.title, 'Programming')
        self.assertEqual(self.category.description, 'Learn programming languages')

    def test_course_creation(self):
        """Test that the course was created correctly"""
        self.assertEqual(self.course.title, 'Python Programming')
        self.assertEqual(self.course.category, self.category)
        self.assertTrue(self.course.is_published)

    def test_get_category_through_api(self):
        """Test retrieving category through API endpoint"""
        url = reverse('category-detail', kwargs={'pk': self.category.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Programming')
        self.assertEqual(response.data['description'], 'Learn programming languages')

    def test_get_course_modules(self):
        """Test retrieving all modules for a course"""
        url = reverse('module-list')
        response = self.client.get(url, {'course': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Python Programming')

    def test_lesson_problem(self):
        """Test retrieving a lesson's problem (exercise)"""
        url = reverse('lesson-detail', kwargs={'pk': self.lesson.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['problem_data']['question_text'], 'What is the data type of the value 42?')
        self.assertEqual(response.data['problem_data']['correct_answer'], 'integer')

    def test_get_course_through_api(self):
        """Test retrieving course through API endpoint"""
        url = reverse('course-detail', kwargs={'pk': self.course.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Python Programming')
        self.assertEqual(response.data['description'], 'Learn Python from scratch')
        self.assertTrue(response.data['is_published'])

    def test_get_module_through_api(self):
        """Test retrieving module through API endpoint"""
        url = reverse('module-detail', kwargs={'pk': self.course.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Python Programming')
        self.assertEqual(response.data['description'], 'Learn Python from scratch')
        self.assertTrue(response.data['is_published'])

    def test_get_lesson_through_api(self):
        """Test retrieving lesson through API endpoint"""
        url = reverse('lesson-detail', kwargs={'pk': self.lesson.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Python Data Types')
        self.assertEqual(response.data['lesson_number'], 1)
        self.assertEqual(response.data['estimated_time'], 30)
        self.assertTrue(response.data['is_published'])

    def test_get_course_modules(self):
        """Test retrieving all modules for a course"""
        url = reverse('module-list')
        response = self.client.get(url, {'course': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Python Programming')

    def test_get_module_lessons(self):
        """Test retrieving all lessons for a module"""
        url = reverse('lesson-list')
        response = self.client.get(url, {'course': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Python Data Types')

    def test_create_lesson_content_blocks(self):
        """Test creating different types of lesson content blocks"""
        # Create a text block
        text_block_data = {
            'lesson': self.lesson.id,
            'block_type': 'text',
            'content': {
                'text': 'This is a test text block',
                'format': 'markdown'
            },
            'order': 1
        }
        url = reverse('lessoncontentblock-list')
        response = self.client.post(url, text_block_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['block_type'], 'text')
        self.assertEqual(response.data['content']['text'], 'This is a test text block')

        # Create a code block
        code_block_data = {
            'lesson': self.lesson.id,
            'block_type': 'code',
            'content': {
                'language': 'python',
                'code': 'print("Hello, World!")',
                'explanation': 'A simple print statement'
            },
            'order': 2
        }
        response = self.client.post(url, code_block_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['block_type'], 'code')
        self.assertEqual(response.data['content']['language'], 'python')

        # Create a practice block
        practice_block_data = {
            'lesson': self.lesson.id,
            'block_type': 'practice',
            'content': {
                'title': 'Practice Problems',
                'problems': [
                    {
                        'question': 'What is 2 + 2?',
                        'options': [
                            {'id': '1', 'text': '3'},
                            {'id': '2', 'text': '4'},
                            {'id': '3', 'text': '5'},
                            {'id': '4', 'text': '6'}
                        ],
                        'correct_answer': [{'id': '2'}]
                    }
                ]
            },
            'order': 3
        }
        response = self.client.post(url, practice_block_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['block_type'], 'practice')
        self.assertEqual(len(response.data['content']['problems']), 1)

    def test_invalid_content_block(self):
        """Test validation of invalid content blocks"""
        url = reverse('lessoncontentblock-list')

        # Test invalid text block (missing format)
        invalid_text_block = {
            'lesson': self.lesson.id,
            'block_type': 'text',
            'content': {
                'text': 'Test text'
                # missing format field
            },
            'order': 1
        }
        response = self.client.post(url, invalid_text_block, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test invalid practice block (missing required fields)
        invalid_practice_block = {
            'lesson': self.lesson.id,
            'block_type': 'practice',
            'content': {
                'title': 'Practice',
                'problems': [
                    {
                        'question': 'Test question'
                        # missing options and correct_answer
                    }
                ]
            },
            'order': 2
        }
        response = self.client.post(url, invalid_practice_block, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lesson_content_navigation(self):
        """Test navigation between lesson content blocks and problems"""
        # Create a lesson with mixed content
        lesson = Lesson.objects.create(
            course=self.course,
            title='Test Navigation',
            lesson_number=1,
            estimated_time=30,
            is_published=True
        )

        # Create content blocks
        block1 = LessonContentBlock.objects.create(
            lesson=lesson,
            block_type='text',
            content={
                'text': 'First content block',
                'format': 'markdown'
            },
            order=1
        )

        block2 = LessonContentBlock.objects.create(
            lesson=lesson,
            block_type='code',
            content={
                'code': 'print("Hello")',
                'language': 'python',
                'explanation': 'A simple print statement'
            },
            order=3
        )

        # Create problems
        problem1 = Problem.objects.create(
            lesson=lesson,
            question_text='What is 2 + 2?',
            question_type='single_choice',
            options=[
                {'id': '1', 'text': '3'},
                {'id': '2', 'text': '4'},
                {'id': '3', 'text': '5'}
            ],
            correct_answer=[{'id': '2'}],
            explanation='Basic addition',
            order=2
        )

        problem2 = Problem.objects.create(
            lesson=lesson,
            question_text='What is 3 * 3?',
            question_type='single_choice',
            options=[
                {'id': '1', 'text': '6'},
                {'id': '2', 'text': '9'},
                {'id': '3', 'text': '12'}
            ],
            correct_answer=[{'id': '2'}],
            explanation='Basic multiplication',
            order=4
        )

        # Test getting all content in order
        url = reverse('lesson-detail', kwargs={'pk': lesson.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = response.data['content_blocks']
        self.assertEqual(len(content), 4)
        self.assertEqual(content[0]['order'], 1)
        self.assertEqual(content[1]['order'], 2)
        self.assertEqual(content[2]['order'], 3)
        self.assertEqual(content[3]['order'], 4)

        # Test getting next content
        url = reverse('lesson-next-content', kwargs={'pk': lesson.id})
        response = self.client.get(f"{url}?order=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'problem')
        self.assertEqual(response.data['order'], 2)

        # Test getting previous content
        url = reverse('lesson-previous-content', kwargs={'pk': lesson.id})
        response = self.client.get(f"{url}?order=3")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'problem')
        self.assertEqual(response.data['order'], 2)

        # Test end of content
        url = reverse('lesson-next-content', kwargs={'pk': lesson.id})
        response = self.client.get(f"{url}?order=4")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test beginning of content
        url = reverse('lesson-previous-content', kwargs={'pk': lesson.id})
        response = self.client.get(f"{url}?order=1")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_problem_block(self):
        """Test creating a problem block with valid content"""
        problem = Problem.objects.create(
            lesson=self.lesson,
            question_text='What is 2 + 2?',
            question_type='single_choice',
            options=[
                {'id': '1', 'text': '3'},
                {'id': '2', 'text': '4'},
                {'id': '3', 'text': '5'}
            ],
            correct_answer=[{'id': '2'}],
            explanation='Basic addition',
            order=1
        )

        block = LessonContentBlock.objects.create(
            lesson=self.lesson,
            block_type='problem',
            content={
                'introduction': 'Solve this simple math problem',
                'show_hints': True,
                'show_solution': False,
                'attempts_allowed': 3,
                'points': 10
            },
            problem=problem,
            order=1
        )

        self.assertEqual(block.content['introduction'], 'Solve this simple math problem')
        self.assertTrue(block.content['show_hints'])
        self.assertEqual(block.problem, problem) 