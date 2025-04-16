# Garaad Backend API Documentation

This document provides a comprehensive guide to the Garaad Backend API, including authentication, available endpoints, request formats, and response formats.

## Base URL

For local development:
```
http://localhost:8000/
```

For production:
```
https://api.garaad.org/
```

## Authentication

The API uses JWT (JSON Web Token) for authentication. Most endpoints require authentication.

### Authentication Headers

For protected endpoints, include the JWT token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Token Lifecycle

- Access tokens are valid for 15 minutes
- Refresh tokens are valid for 1 day
- Use the refresh endpoint to get a new access token before it expires

## API Endpoints

### Authentication Endpoints

#### 1. User Registration with Onboarding

**Endpoint:** `POST /api/signup/`

**Description:** Registers a new user and creates onboarding information in a single request.

**Request Body:**
```json
{
  "name": "User Full Name",
  "email": "user@example.com",
  "password": "securepassword123",
  "goal": "Horumarinta xirfadaha",
  "learning_approach": "Waxbarasho shaqsiyeed",
  "topic": "Xisaab",
  "math_level": "Bilowga",
  "minutes_per_day": 30
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "User Full Name",
    "email": "user@example.com",
    "first_name": "User",
    "last_name": "Full Name",
    "is_premium": false,
    "has_completed_onboarding": true
  },
  "tokens": {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5..."
  }
}
```

**Errors:**
- 400 Bad Request: If validation fails (e.g., email already exists, invalid data)

#### 2. User Login

**Endpoint:** `POST /api/signin/`

**Description:** Authenticates a user and returns tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "username": "User Full Name",
    "email": "user@example.com",
    "first_name": "User",
    "last_name": "Full Name",
    "is_premium": false,
    "has_completed_onboarding": true
  },
  "tokens": {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5..."
  }
}
```

**Errors:**
- 401 Unauthorized: If credentials are invalid

#### 3. Token Refresh

**Endpoint:** `POST /api/auth/refresh/`

**Description:** Get a new access token using a refresh token.

**Request Body:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5..."
}
```

**Errors:**
- 401 Unauthorized: If refresh token is invalid or expired

### User Profile

#### 1. Get User Profile

**Endpoint:** `GET /api/auth/profile/`

**Description:** Retrieves the authenticated user's profile information.

**Authentication Required:** Yes

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "User Full Name",
  "email": "user@example.com",
  "first_name": "User",
  "last_name": "Full Name",
  "is_premium": false
}
```

**Errors:**
- 401 Unauthorized: If not authenticated

### Onboarding

#### 1. Get Onboarding Status

**Endpoint:** `GET /api/auth/onboarding/status/`

**Description:** Checks if a user has completed onboarding.

**Authentication Required:** Yes

**Response (200 OK):**
```json
{
  "has_completed_onboarding": true
}
```

**Errors:**
- 401 Unauthorized: If not authenticated

#### 2. Complete Onboarding

**Endpoint:** `POST /api/auth/onboarding/complete/`

**Description:** Submit onboarding information for an existing user.

**Authentication Required:** Yes

**Request Body:**
```json
{
  "goal": "Horumarinta xirfadaha",
  "learning_approach": "Waxbarasho shaqsiyeed",
  "topic": "Xisaab",
  "math_level": "Bilowga",
  "minutes_per_day": 30
}
```

**Response (200 OK):**
```json
{
  "goal": "Horumarinta xirfadaha",
  "learning_approach": "Waxbarasho shaqsiyeed",
  "topic": "Xisaab",
  "math_level": "Bilowga",
  "minutes_per_day": 30,
  "has_completed_onboarding": true
}
```

**Errors:**
- 400 Bad Request: If validation fails
- 401 Unauthorized: If not authenticated

### Student Profile

#### 1. Register Student Profile

**Endpoint:** `POST /api/auth/student/register/`

**Description:** Create a student profile for an authenticated user.

**Authentication Required:** Yes

**Request Body:**
```json
{
  "preferred_study_time": ["morning", "evening"],
  "subjects": ["math", "science"],
  "proficiency_level": "Intermediate",
  "study_frequency": 3
}
```

**Response (201 Created):**
```json
{
  "preferred_study_time": ["morning", "evening"],
  "subjects": ["math", "science"],
  "proficiency_level": "Intermediate",
  "study_frequency": 3
}
```

**Errors:**
- 400 Bad Request: If validation fails or profile already exists
- 401 Unauthorized: If not authenticated

### Other Endpoints

#### 1. API Root

**Endpoint:** `GET /api/`

**Description:** Returns information about available API endpoints.

**Authentication Required:** No

**Response (200 OK):**
```json
{
  "status": "online",
  "version": "1.0.0",
  "endpoints": {
    "auth": "/api/auth/",
    "hello": "/hello-world/",
    "signup": "/api/signup/",
    "signin": "/api/signin/",
    "lms": "/api/lms/"
  }
}
```

#### 2. Hello World

**Endpoint:** `GET /hello-world/`

**Description:** A simple endpoint that returns "Hello, World!"

**Authentication Required:** No

**Response (200 OK):**
```
Hello, World!
```

### Learning Management System (LMS) API

The LMS API provides endpoints for managing and accessing courses, modules, lessons, lesson content blocks, problems, and practice sets.

#### Courses

##### 1. List All Courses

**Endpoint:** `GET /api/lms/courses/`

**Description:** Returns a list of all published courses with basic information.

**Authentication Required:** No (for listing public courses)

**Query Parameters:**
- `search`: Search courses by title, description, or category
- `ordering`: Order courses by created_at, title (use `-created_at` for descending order)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Introduction to Python Programming",
    "slug": "introduction-to-python-programming",
    "description": "Learn the basics of Python programming language.",
    "thumbnail": "https://example.com/python-thumbnail.jpg",
    "level": "beginner",
    "category": "Programming",
    "author_id": "instructor1",
    "is_published": true,
    "module_count": 2,
    "created_at": "2023-04-01T10:00:00Z",
    "updated_at": "2023-04-01T10:00:00Z"
  },
  {
    "id": 2,
    "title": "Arabic for Beginners",
    "slug": "arabic-for-beginners",
    "description": "Learn the basics of Arabic language.",
    "thumbnail": "https://example.com/arabic-thumbnail.jpg",
    "level": "beginner",
    "category": "Languages",
    "author_id": "instructor2",
    "is_published": true,
    "module_count": 1,
    "created_at": "2023-04-02T10:00:00Z",
    "updated_at": "2023-04-02T10:00:00Z"
  }
]
```

##### 2. Get Course Details

**Endpoint:** `GET /api/lms/courses/{id}/`

**Description:** Returns detailed information about a specific course, including its modules, lessons, and exercises.

**Authentication Required:** No (for public courses)

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Introduction to Python Programming",
  "slug": "introduction-to-python-programming",
  "description": "Learn the basics of Python programming language.",
  "thumbnail": "https://example.com/python-thumbnail.jpg",
  "level": "beginner",
  "category": "Programming",
  "author_id": "instructor1",
  "is_published": true,
  "created_at": "2023-04-01T10:00:00Z",
  "updated_at": "2023-04-01T10:00:00Z",
  "modules": [
    {
      "id": 1,
      "title": "Getting Started with Python",
      "description": "Learn how to set up your Python environment.",
      "order": 1,
      "lessons": [
        {
          "id": 1,
          "title": "Installing Python",
          "content": "In this lesson, you will learn how to install Python...",
          "type": "lesson",
          "order": 1,
          "exercises": []
        },
        {
          "id": 2,
          "title": "Your First Python Program",
          "content": "In this lesson, you will write your first Python program...",
          "type": "lesson",
          "order": 2,
          "exercises": []
        }
      ]
    }
  ]
}
```

**Errors:**
- 404 Not Found: If the course does not exist

##### 3. Create a Course

**Endpoint:** `POST /api/lms/courses/`

**Description:** Creates a new course.

**Authentication Required:** Yes (admin or instructor)

**Request Body:**
```json
{
  "title": "JavaScript Fundamentals",
  "description": "Learn the core concepts of JavaScript programming.",
  "thumbnail": "https://example.com/js-thumbnail.jpg",
  "level": "beginner",
  "category": "Programming",
  "author_id": "instructor1",
  "is_published": false
}
```

**Response (201 Created):**
```json
{
  "id": 3,
  "title": "JavaScript Fundamentals",
  "slug": "javascript-fundamentals",
  "description": "Learn the core concepts of JavaScript programming.",
  "thumbnail": "https://example.com/js-thumbnail.jpg",
  "level": "beginner",
  "category": "Programming",
  "author_id": "instructor1",
  "is_published": false,
  "created_at": "2023-06-15T14:30:00Z",
  "updated_at": "2023-06-15T14:30:00Z",
  "modules": []
}
```

**Errors:**
- 400 Bad Request: If validation fails
- 401 Unauthorized: If not authenticated
- 403 Forbidden: If user doesn't have permission to create courses

#### Modules

##### 1. List All Modules

**Endpoint:** `GET /api/lms/modules/`

**Description:** Returns a list of all modules.

**Authentication Required:** No

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "course": 1,
    "title": "Getting Started with Python",
    "description": "Learn how to set up your Python environment.",
    "order": 1,
    "created_at": "2023-04-01T10:01:00Z",
    "updated_at": "2023-04-01T10:01:00Z"
  }
]
```

##### 2. Get Course Modules

**Endpoint:** `GET /api/lms/modules/course/{course_id}/`

**Description:** Returns all modules for a specific course.

**Authentication Required:** No (for public courses)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "course": 1,
    "title": "Getting Started with Python",
    "description": "Learn how to set up your Python environment.",
    "order": 1,
    "created_at": "2023-04-01T10:01:00Z",
    "updated_at": "2023-04-01T10:01:00Z",
    "lessons": [
      {
        "id": 1,
        "title": "Installing Python",
        "content": "In this lesson, you will learn how to install Python...",
        "type": "lesson",
        "order": 1
      },
      {
        "id": 2,
        "title": "Your First Python Program",
        "content": "In this lesson, you will write your first Python program...",
        "type": "lesson",
        "order": 2
      }
    ]
  },
  {
    "id": 2,
    "course": 1,
    "title": "Python Basics",
    "description": "Learn about variables, data types, and basic operations.",
    "order": 2,
    "created_at": "2023-04-01T10:02:00Z",
    "updated_at": "2023-04-01T10:02:00Z",
    "lessons": []
  }
]
```

##### 3. Create a Module

**Endpoint:** `POST /api/lms/modules/`

**Description:** Creates a new module for a course.

**Authentication Required:** Yes (admin or instructor)

**Request Body:**
```json
{
  "course": 1,
  "title": "Advanced Python Concepts",
  "description": "Learn about decorators, generators, and more.",
  "order": 3
}
```

**Response (201 Created):**
```json
{
  "id": 4,
  "course": 1,
  "title": "Advanced Python Concepts",
  "description": "Learn about decorators, generators, and more.",
  "order": 3,
  "created_at": "2023-06-15T15:00:00Z",
  "updated_at": "2023-06-15T15:00:00Z",
  "lessons": []
}
```

**Errors:**
- 400 Bad Request: If validation fails
- 401 Unauthorized: If not authenticated
- 403 Forbidden: If user doesn't have permission

#### Lessons

##### 1. List All Lessons

**Endpoint:** `GET /api/lms/lessons/`

**Description:** Returns a list of all lessons.

**Authentication Required:** No

**Query Parameters:**
- `module`: Filter lessons by module ID

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "module": 1,
    "title": "Installing Python",
    "slug": "installing-python",
    "lesson_number": 1,
    "estimated_time": 15,
    "is_published": true,
    "created_at": "2023-04-01T10:03:00Z",
    "updated_at": "2023-04-01T10:03:00Z"
  }
]
```

##### 2. Get Module Lessons

**Endpoint:** `GET /api/lms/lessons/module/{module_id}/`

**Description:** Returns all lessons for a specific module, including their content blocks.

**Authentication Required:** No (for public courses)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "module": 1,
    "title": "Installing Python",
    "slug": "installing-python",
    "lesson_number": 1,
    "estimated_time": 15,
    "is_published": true,
    "created_at": "2023-04-01T10:03:00Z",
    "updated_at": "2023-04-01T10:03:00Z",
    "content_blocks": [
      {
        "id": 1,
        "lesson": 1,
        "block_type": "text",
        "content": {
          "text": "In this lesson, you will learn how to install Python..."
        },
        "order": 1,
        "created_at": "2023-04-01T10:04:00Z"
      },
      {
        "id": 2,
        "lesson": 1,
        "block_type": "example",
        "content": {
          "title": "Installation Example",
          "text": "Here's an example of installing Python on different operating systems..."
        },
        "order": 2,
        "created_at": "2023-04-01T10:05:00Z"
      }
    ]
  },
  {
    "id": 2,
    "module": 1,
    "title": "Your First Python Program",
    "slug": "your-first-python-program",
    "lesson_number": 2,
    "estimated_time": 20,
    "is_published": true,
    "created_at": "2023-04-01T10:04:00Z",
    "updated_at": "2023-04-01T10:04:00Z",
    "content_blocks": []
  }
]
```

##### 3. Create a Lesson

**Endpoint:** `POST /api/lms/lessons/`

**Description:** Creates a new lesson for a module.

**Authentication Required:** Yes (admin or instructor)

**Request Body:**
```json
{
  "module": 1,
  "title": "Python Virtual Environments",
  "lesson_number": 3,
  "estimated_time": 25,
  "is_published": false
}
```

**Response (201 Created):**
```json
{
  "id": 3,
  "module": 1,
  "title": "Python Virtual Environments",
  "slug": "python-virtual-environments",
  "lesson_number": 3,
  "estimated_time": 25,
  "is_published": false,
  "created_at": "2023-06-15T15:30:00Z",
  "updated_at": "2023-06-15T15:30:00Z",
  "content_blocks": []
}
```

**Errors:**
- 400 Bad Request: If validation fails
- 401 Unauthorized: If not authenticated
- 403 Forbidden: If user doesn't have permission

#### Lesson Content Blocks

##### 1. List Content Blocks

**Endpoint:** `GET /api/lms/content-blocks/`

**Description:** Returns a list of all content blocks.

**Authentication Required:** No

**Query Parameters:**
- `lesson`: Filter content blocks by lesson ID

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "lesson": 1,
    "block_type": "text",
    "content": {
      "text": "In this lesson, you will learn how to install Python..."
    },
    "order": 1,
    "created_at": "2023-04-01T10:04:00Z"
  },
  {
    "id": 2,
    "lesson": 1,
    "block_type": "example",
    "content": {
      "title": "Installation Example",
      "text": "Here's an example of installing Python on different operating systems..."
    },
    "order": 2,
    "created_at": "2023-04-01T10:05:00Z"
  }
]
```

##### 2. Create a Content Block

**Endpoint:** `POST /api/lms/content-blocks/`

**Description:** Creates a new content block for a lesson.

**Authentication Required:** Yes (admin or instructor)

**Request Body:**
```json
{
  "lesson": 1,
  "block_type": "problem",
  "content": {
    "problem_id": 3,
    "introduction": "Let's test your understanding with a practice problem."
  },
  "order": 3
}
```

**Response (201 Created):**
```json
{
  "id": 3,
  "lesson": 1,
  "block_type": "problem",
  "content": {
    "problem_id": 3,
    "introduction": "Let's test your understanding with a practice problem."
  },
  "order": 3,
  "created_at": "2023-06-15T16:00:00Z"
}
```

**Errors:**
- 400 Bad Request: If validation fails
- 401 Unauthorized: If not authenticated
- 403 Forbidden: If user doesn't have permission

##### 3. Reorder Content Blocks

**Endpoint:** `POST /api/lms/content-blocks/reorder/`

**Description:** Reorders content blocks within a lesson.

**Authentication Required:** Yes (admin or instructor)

**Request Body:**
```json
{
  "lesson_id": 1,
  "block_order": [2, 1, 3]
}
```

**Response (200 OK):**
```json
[
  {
    "id": 2,
    "lesson": 1,
    "block_type": "example",
    "content": {
      "title": "Installation Example",
      "text": "Here's an example of installing Python on different operating systems..."
    },
    "order": 0,
    "created_at": "2023-04-01T10:05:00Z"
  },
  {
    "id": 1,
    "lesson": 1,
    "block_type": "text",
    "content": {
      "text": "In this lesson, you will learn how to install Python..."
    },
    "order": 1,
    "created_at": "2023-04-01T10:04:00Z"
  },
  {
    "id": 3,
    "lesson": 1,
    "block_type": "problem",
    "content": {
      "problem_id": 3,
      "introduction": "Let's test your understanding with a practice problem."
    },
    "order": 2,
    "created_at": "2023-06-15T16:00:00Z"
  }
]
```

**Errors:**
- 400 Bad Request: If validation fails
- 401 Unauthorized: If not authenticated
- 403 Forbidden: If user doesn't have permission
- 404 Not Found: If the lesson does not exist

#### Problems

##### 1. List All Problems

**Endpoint:** `GET /api/lms/problems/`

**Description:** Returns a list of all problems with their hints and solution steps.

**Authentication Required:** No

**Query Parameters:**
- `search`: Search problems by question text
- `difficulty`: Filter problems by difficulty level

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "question_text": "What command do you use to run a Python script named 'hello.py'?",
    "question_type": "input",
    "options": null,
    "correct_answer": "python hello.py",
    "explanation": "To run a Python script, you use the 'python' command followed by the filename.",
    "difficulty": "beginner",
    "hints": [
      {
        "id": 1,
        "content": "The command starts with 'python'",
        "order": 0
      },
      {
        "id": 2,
        "content": "After the command, you need to specify the file name",
        "order": 1
      }
    ],
    "solution_steps": [
      {
        "id": 1,
        "explanation": "First, open your terminal or command prompt",
        "order": 0
      },
      {
        "id": 2,
        "explanation": "Navigate to the directory containing your script using 'cd' commands",
        "order": 1
      },
      {
        "id": 3,
        "explanation": "Type 'python hello.py' and press Enter to execute the script",
        "order": 2
      }
    ],
    "created_at": "2023-04-01T10:07:00Z",
    "updated_at": "2023-04-01T10:07:00Z"
  }
]
```

##### 2. Create a Problem

**Endpoint:** `POST /api/lms/problems/`

**Description:** Creates a new problem with optional hints and solution steps.

**Authentication Required:** Yes (admin or instructor)

**Request Body:**
```json
{
  "question_text": "What Python function would you use to get the length of a list?",
  "question_type": "input",
  "options": null,
  "correct_answer": "len()",
  "explanation": "The len() function returns the number of items in a container like a list.",
  "difficulty": "beginner"
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "question_text": "What Python function would you use to get the length of a list?",
  "question_type": "input",
  "options": null,
  "correct_answer": "len()",
  "explanation": "The len() function returns the number of items in a container like a list.",
  "difficulty": "beginner",
  "hints": [],
  "solution_steps": [],
  "created_at": "2023-06-15T16:30:00Z",
  "updated_at": "2023-06-15T16:30:00Z"
}
```

**Errors:**
- 400 Bad Request: If validation fails
- 401 Unauthorized: If not authenticated
- 403 Forbidden: If user doesn't have permission

##### 3. Add a Hint to a Problem

**Endpoint:** `POST /api/lms/problems/{problem_id}/hints/`

**Description:** Adds a hint to an existing problem.

**Authentication Required:** Yes (admin or instructor)

**Request Body:**
```json
{
  "content": "Think about functions that can count items",
  "order": 0
}
```

**Response (201 Created):**
```json
{
  "id": 3,
  "content": "Think about functions that can count items",
  "order": 0
}
```

**Errors:**
- 400 Bad Request: If validation fails
- 401 Unauthorized: If not authenticated
- 403 Forbidden: If user doesn't have permission
- 404 Not Found: If the problem does not exist

##### 4. Add a Solution Step to a Problem

**Endpoint:** `POST /api/lms/problems/{problem_id}/solution-steps/`

**Description:** Adds a solution step to an existing problem.

**Authentication Required:** Yes (admin or instructor)

**Request Body:**
```json
{
  "explanation": "Use the len() function with the list as its argument: len(my_list)",
  "order": 0
}
```

**Response (201 Created):**
```json
{
  "id": 4,
  "explanation": "Use the len() function with the list as its argument: len(my_list)",
  "order": 0
}
```

**Errors:**
- 400 Bad Request: If validation fails
- 401 Unauthorized: If not authenticated
- 403 Forbidden: If user doesn't have permission
- 404 Not Found: If the problem does not exist

#### Practice Sets

##### 1. List All Practice Sets

**Endpoint:** `GET /api/lms/practice-sets/`

**Description:** Returns a list of all practice sets.

**Authentication Required:** No

**Query Parameters:**
- `lesson`: Filter practice sets by lesson ID
- `module`: Filter practice sets by module ID
- `practice_type`: Filter by practice type (lesson, module, mixed, challenge)
- `difficulty`: Filter by difficulty level

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Python Basics Practice",
    "lesson": 2,
    "module": null,
    "practice_type": "lesson",
    "difficulty_level": "beginner",
    "is_randomized": false,
    "is_published": true,
    "practice_set_problems": [
      {
        "id": 1,
        "practice_set": 1,
        "problem": 1,
        "problem_details": {
          "id": 1,
          "question_text": "What command do you use to run a Python script named 'hello.py'?",
          "question_type": "input",
          "options": null,
          "correct_answer": "python hello.py",
          "explanation": "To run a Python script, you use the 'python' command followed by the filename.",
          "difficulty": "beginner",
          "hints": [...],
          "solution_steps": [...],
          "created_at": "2023-04-01T10:07:00Z",
          "updated_at": "2023-04-01T10:07:00Z"
        },
        "order": 0
      }
    ],
    "created_at": "2023-04-01T11:00:00Z",
    "updated_at": "2023-04-01T11:00:00Z"
  }
]
```

##### 2. Create a Practice Set

**Endpoint:** `POST /api/lms/practice-sets/`

**Description:** Creates a new practice set linked to either a lesson or a module.

**Authentication Required:** Yes (admin or instructor)

**Request Body:**
```json
{
  "title": "Python Functions Review",
  "lesson": null,
  "module": 1,
  "practice_type": "module",
  "difficulty_level": "intermediate",
  "is_randomized": true,
  "is_published": false
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "title": "Python Functions Review",
  "lesson": null,
  "module": 1,
  "practice_type": "module",
  "difficulty_level": "intermediate",
  "is_randomized": true,
  "is_published": false,
  "practice_set_problems": [],
  "created_at": "2023-06-15T17:00:00Z",
  "updated_at": "2023-06-15T17:00:00Z"
}
```

**Errors:**
- 400 Bad Request: If validation fails
- 401 Unauthorized: If not authenticated
- 403 Forbidden: If user doesn't have permission

##### 3. Add a Problem to a Practice Set

**Endpoint:** `POST /api/lms/practice-set-problems/`

**Description:** Adds a problem to a practice set with a specified order.

**Authentication Required:** Yes (admin or instructor)

**Request Body:**
```json
{
  "practice_set": 2,
  "problem": 2,
  "order": 0
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "practice_set": 2,
  "problem": 2,
  "problem_details": {
    "id": 2,
    "question_text": "What Python function would you use to get the length of a list?",
    "question_type": "input",
    "options": null,
    "correct_answer": "len()",
    "explanation": "The len() function returns the number of items in a container like a list.",
    "difficulty": "beginner",
    "hints": [],
    "solution_steps": [],
    "created_at": "2023-06-15T16:30:00Z",
    "updated_at": "2023-06-15T16:30:00Z"
  },
  "order": 0
}
```

**Errors:**
- 400 Bad Request: If validation fails
- 401 Unauthorized: If not authenticated
- 403 Forbidden: If user doesn't have permission

##### 4. Reorder Problems in a Practice Set

**Endpoint:** `POST /api/lms/practice-set-problems/reorder/`

**Description:** Reorders problems within a practice set.

**Authentication Required:** Yes (admin or instructor)

**Request Body:**
```json
{
  "practice_set_id": 2,
  "problem_order": [3, 2, 1]
}
```

**Response (200 OK):**
```json
[
  {
    "id": 3,
    "practice_set": 2,
    "problem": 3,
    "problem_details": {...},
    "order": 0
  },
  {
    "id": 2,
    "practice_set": 2,
    "problem": 2,
    "problem_details": {...},
    "order": 1
  },
  {
    "id": 1,
    "practice_set": 2,
    "problem": 1,
    "problem_details": {...},
    "order": 2
  }
]
```

**Errors:**
- 400 Bad Request: If validation fails
- 401 Unauthorized: If not authenticated
- 403 Forbidden: If user doesn't have permission
- 404 Not Found: If the practice set does not exist

## Common Error Responses

### 400 Bad Request
```json
{
  "field_name": [
    "Error message about this field"
  ]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

## Integration Guide for Frontend Developers

### Authentication Flow

1. **Registration:**
   - Call the signup endpoint with user details and onboarding information
   - Store the returned access and refresh tokens securely (e.g., in HttpOnly cookies or localStorage)

2. **Login:**
   - Call the signin endpoint with email and password
   - Store the returned tokens

3. **Making Authenticated Requests:**
   - Include the access token in the Authorization header for every protected request
   - `Authorization: Bearer <access_token>`

4. **Token Refresh:**
   - When the access token expires, use the refresh token to get a new one
   - Implement token refresh before access token expiration (e.g., after 14 minutes for a 15-minute token)

5. Log out users when refresh token expires or is invalid 

### Error Handling

- Always handle 400, 401, and 404 errors appropriately in your frontend
- Display validation errors to the user in a friendly format
- Redirect to login page on 401 errors (after attempting token refresh)

### Example: User Registration Flow

```javascript
// Example using fetch API
async function registerUser(userData) {
  try {
    const response = await fetch('http://localhost:8000/api/signup/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(JSON.stringify(errorData));
    }
    
    const data = await response.json();
    
    // Store tokens
    localStorage.setItem('accessToken', data.tokens.access);
    localStorage.setItem('refreshToken', data.tokens.refresh);
    
    return data.user;
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
}
```

### Example: Making Authenticated Requests

```javascript
async function fetchUserProfile() {
  try {
    const accessToken = localStorage.getItem('accessToken');
    
    const response = await fetch('http://localhost:8000/api/auth/profile/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    });
    
    if (response.status === 401) {
      // Token expired, try to refresh
      await refreshToken();
      return fetchUserProfile(); // Retry with new token
    }
    
    if (!response.ok) {
      throw new Error('Failed to fetch profile');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Profile fetch error:', error);
    throw error;
  }
}

async function refreshToken() {
  const refreshToken = localStorage.getItem('refreshToken');
  
  const response = await fetch('http://localhost:8000/api/auth/refresh/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh: refreshToken }),
  });
  
  if (!response.ok) {
    // Refresh failed, redirect to login
    window.location.href = '/login';
    throw new Error('Session expired');
  }
  
  const data = await response.json();
  localStorage.setItem('accessToken', data.access);
  return data.access;
}
```

### Example: Working with the Learning Management System API

#### Fetching and Displaying Courses

```javascript
// Example function to fetch and display courses
async function fetchCourses() {
  try {
    const response = await fetch('http://localhost:8000/api/lms/courses/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch courses');
    }
    
    const courses = await response.json();
    
    // Display courses in your UI
    const coursesList = document.getElementById('courses-list');
    coursesList.innerHTML = '';
    
    courses.forEach(course => {
      const courseElement = document.createElement('div');
      courseElement.className = 'course-card';
      courseElement.innerHTML = `
        <img src="${course.thumbnail || 'default-course.jpg'}" alt="${course.title}">
        <h3>${course.title}</h3>
        <p>${course.description.substring(0, 100)}...</p>
        <span class="level-badge">${course.level}</span>
        <a href="/course/${course.slug}" class="btn">View Course</a>
      `;
      coursesList.appendChild(courseElement);
    });
    
    return courses;
  } catch (error) {
    console.error('Error fetching courses:', error);
    // Show error message to user
    document.getElementById('error-message').textContent = 'Unable to load courses. Please try again later.';
    throw error;
  }
}

// Function to fetch a specific course with all its content
async function fetchCourseDetails(courseId) {
  try {
    const accessToken = localStorage.getItem('accessToken');
    const headers = accessToken ? 
      { 'Authorization': `Bearer ${accessToken}` } : 
      { 'Content-Type': 'application/json' };
    
    const response = await fetch(`http://localhost:8000/api/lms/courses/${courseId}/`, {
      method: 'GET',
      headers: headers,
    });
    
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Course not found');
      }
      throw new Error('Failed to fetch course details');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching course details:', error);
    throw error;
  }
}

// Function to submit an exercise answer
async function submitExerciseAnswer(exerciseId, answer) {
  try {
    const accessToken = localStorage.getItem('accessToken');
    
    if (!accessToken) {
      // Redirect to login if user is not authenticated
      window.location.href = '/login?redirect=' + window.location.pathname;
      return;
    }
    
    const response = await fetch(`http://localhost:8000/api/lms/exercises/${exerciseId}/submit/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ answer }),
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        // Token expired, try to refresh
        await refreshToken();
        return submitExerciseAnswer(exerciseId, answer);
      }
      
      throw new Error('Failed to submit answer');
    }
    
    const result = await response.json();
    
    // Display the result to the user
    const resultElement = document.getElementById('exercise-result');
    if (result.is_correct) {
      resultElement.innerHTML = `
        <div class="correct-answer">
          <h4>Correct!</h4>
          <p>${result.explanation}</p>
        </div>
      `;
    } else {
      resultElement.innerHTML = `
        <div class="wrong-answer">
          <h4>Incorrect</h4>
          <p>${result.explanation}</p>
        </div>
      `;
    }
    
    return result;
  } catch (error) {
    console.error('Error submitting exercise answer:', error);
    throw error;
  }
}
```

#### Best Practices for LMS Integration

1. **Progressive Loading**: First load the course list, then load course details only when a user selects a specific course.

2. **Caching**: Consider caching course structure (but not exercises) in localStorage to improve performance.

3. **Course Navigation**: Create a side navigation that displays the module and lesson structure for easy navigation within a course.

4. **Exercise Handling**: 
   - For multiple choice exercises, validate selection before submission
   - For input exercises, provide clear instructions on expected answer format
   - Always display meaningful feedback after submission

5. **Progress Tracking**: Implement client-side progress tracking to help users know which lessons they've completed.

6. **Responsive Design**: Ensure your course UI is responsive for both desktop and mobile learning experiences.

7. **Error Handling**: Provide user-friendly messages when content fails to load or submissions fail.

## Development Guidelines

1. Always validate input on the frontend before sending to API
2. Implement proper error handling for all API calls
3. Use the token refresh mechanism to maintain session
4. Securely store tokens (HttpOnly cookies are preferred in production)
5. Log out users when refresh token expires or is invalid 


