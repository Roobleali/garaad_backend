from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from courses.models import Course, Module, Lesson, Category

class LMSAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_staff=True
        )
        self.client.force_authenticate(user=self.user)

        # Create a programming category
        self.category = Category.objects.create(
            id='programming',
            title='Programming',
            description='Learn programming languages and concepts',
            image='programming.jpg',
            in_progress=False,
            course_ids=[]
        )
        
        # Create a Python course
        self.course = Course.objects.create(
            category=self.category,
            title='Python Programming',
            description='Learn Python from scratch',
            author_id='1',
            is_published=True,
            thumbnail='https://example.com/python.jpg'
        )
        
        # Create a Variables module
        self.module = Module.objects.create(
            id='variables',
            course=self.course,
            title='Variables and Data Types',
            description='Learn about Python variables and data types',
            lesson_ids=[]
        )
        
        # Create a Data Types lesson
        self.lesson = Lesson.objects.create(
            module=self.module,
            title='Python Data Types',
            description='Understanding different data types in Python',
            type='exercise',
            problem={
                'question': 'What is the data type of the value 42?',
                'example': 'x = 42',
                'options': ['string', 'integer', 'float', 'boolean'],
                'solution': 'integer',
                'explanation': '42 is an integer in Python'
            },
            language_options=['en']
        )
        
        # Update module's lesson_ids
        self.module.lesson_ids = [str(self.lesson.id)]
        self.module.save()
        
        # Update course's module_ids
        self.course.module_ids = [self.module.id]
        self.course.save()
        
        # Update category's course_ids
        self.category.course_ids = [str(self.course.id)]
        self.category.save()

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

    def test_list_modules(self):
        """Test retrieving a list of modules"""
        url = reverse('module-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Variables and Data Types')

    def test_create_module(self):
        """Test creating a new module"""
        url = reverse('module-list')
        data = {
            'id': 'new-module',
            'course': self.course.id,
            'title': 'New Module',
            'description': 'New Module Description',
            'lesson_ids': []
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Module.objects.count(), 2)
        self.assertEqual(Module.objects.get(id='new-module').title, 'New Module')

    def test_list_lessons(self):
        """Test retrieving a list of lessons"""
        url = reverse('lesson-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Python Data Types')

    def test_create_lesson(self):
        """Test creating a new lesson with an exercise"""
        url = reverse('lesson-list')
        data = {
            'module': self.module.id,
            'title': 'New Lesson',
            'description': 'New Lesson Description',
            'type': 'exercise',
            'problem': {
                'question': 'New Question',
                'example': 'New Example',
                'options': ['A', 'B', 'C', 'D'],
                'solution': 'B',
                'explanation': 'New Explanation'
            },
            'language_options': ['en']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        self.assertEqual(Lesson.objects.get(slug='new-lesson').title, 'New Lesson')

    def test_module_lessons(self):
        """Test retrieving lessons for a specific module"""
        url = reverse('lesson-list')
        response = self.client.get(url, {'module': self.module.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Python Data Types')

    def test_lesson_problem(self):
        """Test retrieving a lesson's problem (exercise)"""
        url = reverse('lesson-detail', args=[self.lesson.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['problem']['question'], 'What is the data type of the value 42?')
        self.assertEqual(response.data['problem']['solution'], 'integer')

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
        self.assertEqual(self.category.description, 'Learn programming languages and concepts')
        self.assertEqual(len(self.category.course_ids), 1)

    def test_course_creation(self):
        """Test that the course was created correctly"""
        self.assertEqual(self.course.title, 'Python Programming')
        self.assertEqual(self.course.category, self.category)
        self.assertEqual(len(self.course.module_ids), 1)
        self.assertTrue(self.course.is_published)

    def test_module_creation(self):
        """Test that the module was created correctly"""
        self.assertEqual(self.module.title, 'Variables and Data Types')
        self.assertEqual(self.module.course, self.course)
        self.assertEqual(len(self.module.lesson_ids), 1)

    def test_lesson_creation(self):
        """Test that the lesson was created correctly"""
        self.assertEqual(self.lesson.title, 'Python Data Types')
        self.assertEqual(self.lesson.module, self.module)
        self.assertEqual(self.lesson.type, 'exercise')
        self.assertEqual(self.lesson.problem['question'], 'What is the data type of the value 42?')
        self.assertEqual(self.lesson.problem['solution'], 'integer')

    def test_get_category_through_api(self):
        """Test retrieving category through API endpoint"""
        url = reverse('category-detail', args=[self.category.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Programming')
        self.assertEqual(response.data['description'], 'Learn programming languages and concepts')
        self.assertEqual(len(response.data['course_ids']), 1)

    def test_get_course_through_api(self):
        """Test retrieving course through API endpoint"""
        url = reverse('course-detail', args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Python Programming')
        self.assertEqual(response.data['description'], 'Learn Python from scratch')
        self.assertEqual(len(response.data['module_ids']), 1)
        self.assertTrue(response.data['is_published'])

    def test_get_module_through_api(self):
        """Test retrieving module through API endpoint"""
        url = reverse('module-detail', args=[self.module.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Variables and Data Types')
        self.assertEqual(response.data['description'], 'Learn about Python variables and data types')
        self.assertEqual(len(response.data['lesson_ids']), 1)

    def test_get_lesson_through_api(self):
        """Test retrieving lesson through API endpoint"""
        url = reverse('lesson-detail', args=[self.lesson.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Python Data Types')
        self.assertEqual(response.data['description'], 'Understanding different data types in Python')
        self.assertEqual(response.data['type'], 'exercise')
        self.assertEqual(response.data['problem']['question'], 'What is the data type of the value 42?')
        self.assertEqual(response.data['problem']['solution'], 'integer')

    def test_get_course_modules(self):
        """Test retrieving all modules for a course"""
        url = reverse('module-list')
        response = self.client.get(url, {'course': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Variables and Data Types')

    def test_get_module_lessons(self):
        """Test retrieving all lessons for a module"""
        url = reverse('lesson-list')
        response = self.client.get(url, {'module': self.module.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Python Data Types') 