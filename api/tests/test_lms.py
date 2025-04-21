from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from courses.models import Course, Lesson, Category
from django.contrib.auth import get_user_model

User = get_user_model()

class LMSTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        # Create a test category
        self.category = Category.objects.create(
            name='Programming',
            description='Programming courses'
        )

        # Create a Python course
        self.course = Course.objects.create(
            title='Python Programming',
            description='Learn Python from scratch',
            category=self.category,
            is_published=True
        )

        # Create a lesson
        self.lesson = Lesson.objects.create(
            title='Python Data Types',
            course=self.course,
            lesson_number=1,
            estimated_time=30,
            is_published=True
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
        url = reverse('course-detail', args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Python Programming')
        self.assertEqual(response.data['description'], 'Learn Python from scratch')
        self.assertTrue(response.data['is_published'])

    def test_get_lesson_through_api(self):
        """Test retrieving lesson through API endpoint"""
        url = reverse('lesson-detail', args=[self.lesson.id])
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
        url = reverse('course-detail', args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Python Programming')

    def test_update_course(self):
        """Test updating a course"""
        url = reverse('course-detail', args=[self.course.id])
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
        self.assertEqual(self.category.name, 'Programming')
        self.assertEqual(self.category.description, 'Programming courses')

    def test_course_creation(self):
        """Test that the course was created correctly"""
        self.assertEqual(self.course.title, 'Python Programming')
        self.assertEqual(self.course.category, self.category)
        self.assertTrue(self.course.is_published)

    def test_get_category_through_api(self):
        """Test retrieving category through API endpoint"""
        url = reverse('category-detail', args=[self.category.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Programming')
        self.assertEqual(response.data['description'], 'Programming courses')

    def test_get_course_modules(self):
        """Test retrieving all modules for a course"""
        url = reverse('module-list')
        response = self.client.get(url, {'course': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Python Programming')

    def test_lesson_problem(self):
        """Test retrieving a lesson's problem (exercise)"""
        url = reverse('lesson-detail', args=[self.lesson.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['problem']['question'], 'What is the data type of the value 42?')
        self.assertEqual(response.data['problem']['solution'], 'integer')

    def test_get_course_through_api(self):
        """Test retrieving course through API endpoint"""
        url = reverse('course-detail', args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Python Programming')
        self.assertEqual(response.data['description'], 'Learn Python from scratch')
        self.assertTrue(response.data['is_published'])

    def test_get_module_through_api(self):
        """Test retrieving module through API endpoint"""
        url = reverse('module-detail', args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Python Programming')
        self.assertEqual(response.data['description'], 'Learn Python from scratch')
        self.assertTrue(response.data['is_published'])

    def test_get_lesson_through_api(self):
        """Test retrieving lesson through API endpoint"""
        url = reverse('lesson-detail', args=[self.lesson.id])
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
        url = reverse('lesson-content-block-list')
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
                        'options': ['3', '4', '5', '6'],
                        'correct_answer': '4'
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
        url = reverse('lesson-content-block-list')

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