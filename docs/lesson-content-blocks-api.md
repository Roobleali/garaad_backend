# Lesson Content Blocks API Documentation

## Overview
Lesson content blocks are the building blocks of lessons, which can contain different types of content including text, code, images, and problems. This documentation focuses on the problem block type and its relationship with the Problem model.

## Block Types
- `text`: Text content with markdown/HTML formatting
- `code`: Code snippets with syntax highlighting
- `image`: Images with captions
- `video`: Video content
- `quiz`: Quiz questions
- `problem`: Interactive problems (focus of this documentation)

## Problem Block Structure

### Basic Block Information
```json
{
    "id": "integer",
    "lesson": "integer (lesson ID)",
    "block_type": "string (always 'problem' for problem blocks)",
    "order": "integer (position in lesson)",
    "problem": "integer (ID of referenced problem)",
    "content": {
        // Display settings for the problem
    }
}
```

### Block Content (Display Settings)
The `content` field in a problem block contains settings for how the problem should be displayed:
```json
{
    "introduction": "string (optional text shown before the problem)",
    "show_hints": "boolean (whether to show hints button)",
    "show_solution": "boolean (whether to show solution button)",
    "attempts_allowed": "integer (number of attempts allowed)",
    "points": "integer (points awarded for correct solution)"
}
```

## Problem Model Structure
When a block references a problem, the problem contains:
```json
{
    "id": "integer",
    "question_text": "string (the actual question)",
    "question_type": "string (type of question)",
    "options": "array (answer options if applicable)",
    "difficulty": "string (beginner/intermediate/advanced/expert)",
    "content": {
        "metadata": {
            "difficulty": "string",
            "estimated_time": "integer",
            "tags": ["string"]
        },
        "hints": [
            {
                "text": "string",
                "order": "integer"
            }
        ],
        "steps": [
            {
                "text": "string",
                "order": "integer"
            }
        ],
        "feedback": {
            "correct": "string",
            "incorrect": "string"
        }
    },
    "diagram_config": {
        // Only present for diagram-type problems
        "type": "string",
        "parameters": {
            // Diagram-specific parameters
        },
        "interactive": "boolean",
        "controls": [
            // Interactive controls
        ],
        "animations": {
            // Animation settings
        },
        "styles": {
            // Styling options
        }
    }
}
```

## API Endpoints

### 1. Get All Content Blocks for a Lesson
```
GET /api/lesson-content-blocks/?lesson={lesson_id}
```
Returns all content blocks for a lesson, including problem blocks.

### 2. Get a Specific Content Block
```
GET /api/lesson-content-blocks/{block_id}/
```
Returns detailed information about a specific content block.

### 3. Get Complete Problem Data
When you have a problem block, you can get the complete problem data in two ways:

#### Option 1: Through the Problem Endpoint
```
GET /api/problems/{problem_id}/
```
Use the `problem` ID from the block to fetch the complete problem data.

#### Option 2: Through the Block's Complete Content
```
GET /api/lesson-content-blocks/{block_id}/complete_content/
```
Returns the block's content combined with the complete problem data.

## Question Types
Problems can be of various types:
- `multiple_choice`: Multiple choice questions
- `single_choice`: Single choice questions
- `true_false`: True/False questions
- `fill_blank`: Fill in the blank questions
- `matching`: Matching questions
- `open_ended`: Open-ended questions
- `math_expression`: Math expression problems
- `code`: Coding problems
- `diagram`: Interactive diagram problems

## Frontend Implementation Notes

### 1. Block Identification
- Check `block_type === 'problem'` to identify problem blocks
- Use the `problem` field to get the referenced problem ID

### 2. Problem Data Access
- Always fetch the complete problem data when displaying a problem block
- Use either the problem endpoint or the complete content endpoint
- Cache problem data to avoid repeated fetches

### 3. Display Settings
- Use the block's `content` field for display settings
- Apply these settings when rendering the problem
- Respect `show_hints` and `show_solution` flags

### 4. Problem Interaction
- Track attempts using `attempts_allowed`
- Award points based on `points` value
- Show introduction text if present
- Display hints and solution based on settings

### 5. Error Handling
- Handle cases where the referenced problem doesn't exist
- Validate that the block type matches the problem type
- Check for required fields in both block and problem data

## Example Flow
1. Fetch lesson content blocks
2. Identify problem blocks
3. For each problem block:
   - Get the referenced problem data
   - Apply display settings from block content
   - Render the problem with appropriate controls
   - Handle user interactions and scoring

## Response Examples

### Problem Block Response
```json
{
    "id": 1,
    "lesson": 123,
    "block_type": "problem",
    "problem": 456,
    "content": {
        "introduction": "Solve this problem to test your understanding",
        "show_hints": true,
        "show_solution": false,
        "attempts_allowed": 3,
        "points": 10
    },
    "order": 1
}
```

### Complete Problem Data Response
```json
{
    "id": 456,
    "question_text": "What is 2 + 2?",
    "question_type": "multiple_choice",
    "options": ["3", "4", "5", "6"],
    "difficulty": "beginner",
    "content": {
        "metadata": {
            "difficulty": "beginner",
            "estimated_time": 2,
            "tags": ["math", "addition"]
        },
        "hints": [
            {
                "text": "Think about basic addition",
                "order": 1
            }
        ],
        "steps": [
            {
                "text": "Add the two numbers together",
                "order": 1
            }
        ],
        "feedback": {
            "correct": "Great job! You've mastered basic addition.",
            "incorrect": "Let's review addition basics and try again."
        }
    }
}
```

## Getting Problem Content

After identifying a problem block (`block_type === 'problem'`), you need to fetch the complete problem data. Here are the detailed steps:

### Step 1: Get the Problem ID
From the problem block response, extract the problem ID:
```json
{
    "id": 1,
    "block_type": "problem",
    "problem": 456,  // This is the problem ID you need
    "content": {
        "introduction": "Solve this problem...",
        "show_hints": true,
        "show_solution": false,
        "attempts_allowed": 3,
        "points": 10
    }
}
```

### Step 2: Fetch the Problem Data
You have two options to get the complete problem data:

#### Option 1: Direct Problem Endpoint
```
GET /api/problems/{problem_id}/
```
Example response:
```json
{
    "id": 456,
    "question_text": "What is 2 + 2?",
    "question_type": "multiple_choice",
    "options": ["3", "4", "5", "6"],
    "difficulty": "beginner",
    "content": {
        "metadata": {
            "difficulty": "beginner",
            "estimated_time": 2,
            "tags": ["math", "addition"]
        },
        "hints": [
            {
                "text": "Think about basic addition",
                "order": 1
            }
        ],
        "steps": [
            {
                "text": "Add the two numbers together",
                "order": 1
            }
        ],
        "feedback": {
            "correct": "Great job! You've mastered basic addition.",
            "incorrect": "Let's review addition basics and try again."
        }
    }
}
```

#### Option 2: Block's Complete Content Endpoint
```
GET /api/lesson-content-blocks/{block_id}/complete_content/
```
This endpoint returns both the block's display settings and the complete problem data in one response:
```json
{
    "block": {
        "id": 1,
        "block_type": "problem",
        "content": {
            "introduction": "Solve this problem...",
            "show_hints": true,
            "show_solution": false,
            "attempts_allowed": 3,
            "points": 10
        }
    },
    "problem": {
        "id": 456,
        "question_text": "What is 2 + 2?",
        "question_type": "multiple_choice",
        "options": ["3", "4", "5", "6"],
        "difficulty": "beginner",
        "content": {
            "metadata": {
                "difficulty": "beginner",
                "estimated_time": 2,
                "tags": ["math", "addition"]
            },
            "hints": [
                {
                    "text": "Think about basic addition",
                    "order": 1
                }
            ],
            "steps": [
                {
                    "text": "Add the two numbers together",
                    "order": 1
                }
            ],
            "feedback": {
                "correct": "Great job! You've mastered basic addition.",
                "incorrect": "Let's review addition basics and try again."
            }
        }
    }
}
```

### Step 3: Combine the Data
After getting both the block and problem data, you should combine them for display:

1. Use the block's `content` for display settings:
   - Show/hide hints based on `show_hints`
   - Show/hide solution based on `show_solution`
   - Display the introduction text
   - Track attempts using `attempts_allowed`
   - Award points based on `points`

2. Use the problem's data for the actual question:
   - Display `question_text`
   - Show options if it's a multiple choice question
   - Show hints in order if `show_hints` is true
   - Show solution steps if `show_solution` is true
   - Display feedback messages based on user's answer

### Example Frontend Flow
```javascript
// 1. Get the lesson content blocks
const blocks = await fetch('/api/lesson-content-blocks/?lesson=123');

// 2. Find problem blocks
const problemBlocks = blocks.filter(block => block.block_type === 'problem');

// 3. For each problem block, get complete data
for (const block of problemBlocks) {
    // Option 1: Get block and problem data separately
    const problemData = await fetch(`/api/problems/${block.problem}/`);
    
    // Option 2: Get combined data in one request
    const completeData = await fetch(`/api/lesson-content-blocks/${block.id}/complete_content/`);
    
    // 4. Render the problem with both block settings and problem data
    renderProblem({
        settings: block.content,
        problem: problemData
    });
}
```

## Problem Blocks vs Other Block Types

Problem blocks are unique compared to other block types in several ways:

### 1. External Reference
Unlike other blocks that store all their content directly in the `content` field, problem blocks:
- Reference an external `Problem` model through the `problem` field
- Store only display settings in their `content` field
- Require fetching additional data to show the complete content

### 2. Content Structure
Here's how different block types handle their content:

#### Text Block
```json
{
    "block_type": "text",
    "content": {
        "text": "The actual content",
        "format": "markdown"
    }
}
```

#### Code Block
```json
{
    "block_type": "code",
    "content": {
        "language": "python",
        "code": "print('Hello')",
        "explanation": "Optional explanation"
    }
}
```

#### Problem Block
```json
{
    "block_type": "problem",
    "problem": 456,  // References external Problem
    "content": {
        // Only display settings
        "introduction": "Optional intro text",
        "show_hints": true,
        "show_solution": false,
        "attempts_allowed": 3,
        "points": 10
    }
}
```

### 3. Data Flow
The data flow for problem blocks is more complex:

1. **Other Block Types**:
   - Single API call to get block
   - Content is immediately available
   - No additional data needed

2. **Problem Blocks**:
   - Get block data
   - Extract problem ID
   - Fetch problem data
   - Combine block settings with problem data

### 4. Interaction Model
Problem blocks support interactive features that other blocks don't:

- **Problem-specific features**:
  - Multiple attempts
  - Hint system
  - Solution steps
  - Feedback messages
  - Points/scoring
  - Progress tracking

- **Other blocks** are typically:
  - Read-only
  - Static content
  - No user interaction
  - No scoring

### 5. Validation Requirements
Problem blocks have additional validation requirements:

1. **Required Fields**:
   - Must have a valid `problem` reference
   - Problem must exist in the database
   - Block type must match problem type

2. **Content Validation**:
   - Problem-specific validation rules
   - Answer validation
   - Attempt tracking
   - Scoring validation

### 6. Rendering Differences
Problem blocks require special handling in the frontend:

1. **Other Blocks**:
   - Direct rendering of content
   - Simple display components
   - No state management

2. **Problem Blocks**:
   - Complex state management
   - Interactive components
   - User input handling
   - Progress tracking
   - Score calculation
   - Hint/solution management

### Example: Handling Different Block Types
```javascript
function renderBlock(block) {
    switch(block.block_type) {
        case 'text':
            return <TextBlock content={block.content} />;
            
        case 'code':
            return <CodeBlock content={block.content} />;
            
        case 'problem':
            // Problem blocks need additional data
            const problemData = await fetchProblem(block.problem);
            return <ProblemBlock 
                settings={block.content}
                problem={problemData}
            />;
            
        // ... other block types
    }
} 
```

## Problem API Structure

### Problem Endpoints

#### 1. Get Problem by ID
```
GET /api/problems/{problem_id}/
```
Response:
```json
{
    "id": 456,
    "question_text": "What is 2 + 2?",
    "question_type": "multiple_choice",
    "options": ["3", "4", "5", "6"],
    "correct_answer": "4",
    "difficulty": "beginner",
    "content": {
        "metadata": {
            "difficulty": "beginner",
            "estimated_time": 2,
            "tags": ["math", "addition"]
        },
        "hints": [
            {
                "text": "Think about basic addition",
                "order": 1
            }
        ],
        "steps": [
            {
                "text": "Add the two numbers together",
                "order": 1
            }
        ],
        "feedback": {
            "correct": "Great job! You've mastered basic addition.",
            "incorrect": "Let's review addition basics and try again."
        }
    },
    "diagram_config": {
        // Only for diagram-type problems
        "type": "scale-weight",
        "parameters": {
            "weight": 40,
            "items": [
                {
                    "type": "square",
                    "count": 4,
                    "color": "#3498db",
                    "size": 20
                }
            ]
        }
    }
}
```

#### 2. Submit Problem Answer
```
POST /api/problems/{problem_id}/submit/
```
Request:
```json
{
    "answer": "4",
    "attempt_number": 1
}
```
Response:
```json
{
    "is_correct": true,
    "feedback": "Great job! You've mastered basic addition.",
    "score": 10,
    "remaining_attempts": 2,
    "solution": {
        "steps": [
            {
                "text": "Add the two numbers together",
                "order": 1
            }
        ]
    }
}
```

#### 3. Get Problem Hints
```
GET /api/problems/{problem_id}/hints/
```
Response:
```json
{
    "hints": [
        {
            "text": "Think about basic addition",
            "order": 1
        },
        {
            "text": "Count on your fingers if needed",
            "order": 2
        }
    ]
}
```

### Frontend Implementation

Here's how to implement the `fetchProblem` function and related utilities:

```javascript
// Problem API utilities
const ProblemAPI = {
    // Get problem data
    async fetchProblem(problemId) {
        const response = await fetch(`/api/problems/${problemId}/`);
        if (!response.ok) {
            throw new Error(`Failed to fetch problem: ${response.statusText}`);
        }
        return response.json();
    },

    // Submit answer
    async submitAnswer(problemId, answer, attemptNumber) {
        const response = await fetch(`/api/problems/${problemId}/submit/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                answer,
                attempt_number: attemptNumber
            })
        });
        if (!response.ok) {
            throw new Error(`Failed to submit answer: ${response.statusText}`);
        }
        return response.json();
    },

    // Get hints
    async getHints(problemId) {
        const response = await fetch(`/api/problems/${problemId}/hints/`);
        if (!response.ok) {
            throw new Error(`Failed to fetch hints: ${response.statusText}`);
        }
        return response.json();
    }
};

// Example usage in a React component
function ProblemComponent({ problemId, settings }) {
    const [problem, setProblem] = useState(null);
    const [answer, setAnswer] = useState('');
    const [attempt, setAttempt] = useState(1);
    const [result, setResult] = useState(null);
    const [hints, setHints] = useState([]);

    // Load problem data
    useEffect(() => {
        async function loadProblem() {
            try {
                const problemData = await ProblemAPI.fetchProblem(problemId);
                setProblem(problemData);
            } catch (error) {
                console.error('Error loading problem:', error);
            }
        }
        loadProblem();
    }, [problemId]);

    // Handle answer submission
    const handleSubmit = async () => {
        try {
            const result = await ProblemAPI.submitAnswer(problemId, answer, attempt);
            setResult(result);
            setAttempt(prev => prev + 1);
        } catch (error) {
            console.error('Error submitting answer:', error);
        }
    };

    // Load hints if enabled
    useEffect(() => {
        if (settings.show_hints) {
            async function loadHints() {
                try {
                    const hintsData = await ProblemAPI.getHints(problemId);
                    setHints(hintsData.hints);
                } catch (error) {
                    console.error('Error loading hints:', error);
                }
            }
            loadHints();
        }
    }, [problemId, settings.show_hints]);

    if (!problem) return <div>Loading...</div>;

    return (
        <div>
            {settings.introduction && (
                <div className="introduction">{settings.introduction}</div>
            )}
            
            <div className="question">{problem.question_text}</div>
            
            {problem.question_type === 'multiple_choice' && (
                <div className="options">
                    {problem.options.map((option, index) => (
                        <button 
                            key={index}
                            onClick={() => setAnswer(option)}
                        >
                            {option}
                        </button>
                    ))}
                </div>
            )}
            
            {settings.show_hints && hints.length > 0 && (
                <div className="hints">
                    {hints.map(hint => (
                        <div key={hint.order}>{hint.text}</div>
                    ))}
                </div>
            )}
            
            <button 
                onClick={handleSubmit}
                disabled={attempt > settings.attempts_allowed}
            >
                Submit Answer
            </button>
            
            {result && (
                <div className={`result ${result.is_correct ? 'correct' : 'incorrect'}`}>
                    {result.feedback}
                </div>
            )}
        </div>
    );
}
```

### Error Handling

The Problem API can return various error responses:

1. **Problem Not Found**
```json
{
    "error": "Problem not found",
    "status": 404
}
```

2. **Invalid Answer Format**
```json
{
    "error": "Invalid answer format",
    "status": 400,
    "details": "Answer must be a string for multiple_choice questions"
}
```

3. **No More Attempts**
```json
{
    "error": "No more attempts allowed",
    "status": 403,
    "remaining_attempts": 0
}
```