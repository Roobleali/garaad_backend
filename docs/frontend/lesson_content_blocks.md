# Lesson Content Blocks - Frontend Documentation

## Overview
Lesson content blocks are the building blocks of lessons in our learning management system. Each block has a specific type and corresponding content structure.

## Block Types and Structures

### 1. Text Block
```typescript
interface TextBlock {
  block_type: 'text';
  content: {
    text: string;
    format: 'markdown' | 'html';
  };
}
```

Example:
```json
{
  "block_type": "text",
  "content": {
    "text": "This is a **markdown** text block",
    "format": "markdown"
  }
}
```

### 2. Code Block
```typescript
interface CodeBlock {
  block_type: 'code';
  content: {
    language: string;
    code: string;
    explanation?: string;
    show_line_numbers?: boolean;
  };
}
```

Example:
```json
{
  "block_type": "code",
  "content": {
    "language": "python",
    "code": "print('Hello, World!')",
    "explanation": "This prints a greeting message",
    "show_line_numbers": true
  }
}
```

### 3. Practice Block
```typescript
interface PracticeBlock {
  block_type: 'practice';
  content: {
    title: string;
    problems: Array<{
      question: string;
      options: string[];
      correct_answer: string;
    }>;
  };
}
```

Example:
```json
{
  "block_type": "practice",
  "content": {
    "title": "Basic Python Quiz",
    "problems": [
      {
        "question": "What is the output of print(2 + 2)?",
        "options": ["3", "4", "5", "6"],
        "correct_answer": "4"
      }
    ]
  }
}
```

### 4. Image Block
```typescript
interface ImageBlock {
  block_type: 'image';
  content: {
    url: string;
    caption?: string;
    alt: string;
    width?: number;
    height?: number;
  };
}
```

Example:
```json
{
  "block_type": "image",
  "content": {
    "url": "https://example.com/image.jpg",
    "caption": "Python Logo",
    "alt": "Python programming language logo",
    "width": 200,
    "height": 200
  }
}
```

### 5. Video Block
```typescript
interface VideoBlock {
  block_type: 'video';
  content: {
    url: string;
    title: string;
    description?: string;
    thumbnail?: string;
    duration?: number;
  };
}
```

Example:
```json
{
  "block_type": "video",
  "content": {
    "url": "https://example.com/video.mp4",
    "title": "Introduction to Python",
    "description": "Learn the basics of Python programming",
    "thumbnail": "https://example.com/thumbnail.jpg",
    "duration": 300
  }
}
```

## API Endpoints

### Get Lesson Content Blocks
```http
GET /api/lessons/{lesson_id}/content-blocks/
```

Response:
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "block_type": "text",
      "content": {
        "text": "Welcome to the lesson",
        "format": "markdown"
      },
      "order": 1
    },
    // ... more blocks
  ]
}
```

### Create Content Block
```http
POST /api/lessons/{lesson_id}/content-blocks/
```

Request body should match one of the block type structures above.

## Frontend Implementation Tips

1. **Rendering Blocks**
   - Use a switch statement or object mapping to render different block types
   - Consider using a component library for markdown rendering
   - Use a code syntax highlighter for code blocks

2. **Validation**
   - Validate content structure before sending to API
   - Show appropriate error messages for invalid content

3. **Ordering**
   - Blocks are ordered by the `order` field
   - Implement drag-and-drop for reordering if needed

4. **Editing**
   - Provide appropriate editors for each block type
   - For text blocks: markdown editor
   - For code blocks: code editor with syntax highlighting
   - For practice blocks: form builder for questions

## Example React Component

```typescript
import React from 'react';
import ReactMarkdown from 'react-markdown';
import SyntaxHighlighter from 'react-syntax-highlighter';

interface ContentBlockProps {
  block: {
    block_type: string;
    content: any;
  };
}

const ContentBlock: React.FC<ContentBlockProps> = ({ block }) => {
  switch (block.block_type) {
    case 'text':
      return (
        <div className="text-block">
          <ReactMarkdown>{block.content.text}</ReactMarkdown>
        </div>
      );
    
    case 'code':
      return (
        <div className="code-block">
          <SyntaxHighlighter language={block.content.language}>
            {block.content.code}
          </SyntaxHighlighter>
          {block.content.explanation && (
            <div className="explanation">
              {block.content.explanation}
            </div>
          )}
        </div>
      );
    
    case 'practice':
      return (
        <div className="practice-block">
          <h3>{block.content.title}</h3>
          {block.content.problems.map((problem, index) => (
            <div key={index} className="problem">
              <p>{problem.question}</p>
              <ul>
                {problem.options.map((option, i) => (
                  <li key={i}>{option}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      );
    
    // ... other block types
    
    default:
      return null;
  }
};

export default ContentBlock;
```

## Best Practices

1. **Performance**
   - Lazy load heavy components (e.g., video players)
   - Implement virtualization for long lists of blocks
   - Cache block content when appropriate

2. **Accessibility**
   - Ensure proper ARIA labels
   - Provide keyboard navigation
   - Support screen readers

3. **Responsive Design**
   - Make blocks responsive
   - Adjust layout based on screen size
   - Consider mobile-first approach

4. **Error Handling**
   - Show fallback content for failed blocks
   - Provide retry mechanisms
   - Log errors for debugging 