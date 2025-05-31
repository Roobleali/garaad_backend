# Garaad LMS Admin CMS UI — Frontend Requirements

## Overview
This document describes the requirements and logic for building a custom LMS admin UI for Garaad, inspired by the smooth workflow of Brilliant.org. The goal is to make it extremely easy for a single admin user to create and manage categories, courses, and especially lessons of various types (text, image, problem, diagram, etc.).

---

## 1. **Authentication & Access**
- Only one user (the admin) can access this CMS.
- Secure login page (JWT or session-based).
- No registration or password reset for general users.

---

## 2. **Core Entities & Relationships**

### a. **Category**
- Fields: `name`, `description`, `icon`, `order`, `is_active`
- Admin can create, edit, delete, and reorder categories.

### b. **Course**
- Fields: `title`, `description`, `category` (FK), `image`, `is_published`, `order`, `tags`
- Admin can create, edit, delete, assign to category, and manage publish status.

### c. **Lesson**
- Fields: `title`, `course` (FK), `order`, `type`, `content`, `is_published`, `media`, `resources`
- **Lesson Types:**
  - **Text/Image:** Rich text editor, support for images, LaTeX, code blocks.
  - **Problem:**
    - Fields: `question_text`, `question_type` (MCQ, open, diagram, etc.), `options`, `correct_answer`, `explanation`, `order`, `points`
    - MCQ: Add options, mark correct answer(s)
    - Open: Text answer
    - Diagram: Upload or build diagram, set correct answer
  - **Diagram:**
    - Fields: `diagram_type`, `template`, `answer`, `explanation`
    - Drag-and-drop or builder UI for diagrams

---

## 3. **UI/UX Requirements**
- **Inspired by Brilliant:**
  - Left: List of problems/lessons (sortable, add new, reorder)
  - Center: Editor for the selected lesson/problem
- **Smooth workflow:**
  - One-click to add new lesson/problem
  - Inline editing for all fields
  - Drag-and-drop reordering
  - Easy asset upload (images, diagrams)
  - Auto-save and manual save
  - Quick preview of how content will look to students
- **Bulk actions:**
  - Duplicate, delete, reorder lessons/problems
  - Import/export (CSV/JSON) for lessons/problems (optional)

---

## 4. **Lesson/Problem Creation Logic**
- **Add Lesson:**
  - Choose type: Text/Image, Problem, Diagram
  - For Problem: Select question type (MCQ, open, diagram)
  - For MCQ: Add options, mark correct answer(s)
  - For Diagram: Use builder or upload image, set answer
  - Add explanation (optional)
- **Validation:**
  - Required fields must be filled before saving
  - For MCQ, at least one correct answer
  - For Diagram, answer must be set
- **Preview:**
  - Show exactly how the lesson/problem will appear to students

---

## 5. **API Endpoints (Sample)**
- `GET/POST/PUT/DELETE /api/lms/categories/`
- `GET/POST/PUT/DELETE /api/lms/courses/`
- `GET/POST/PUT/DELETE /api/lms/lessons/`
- `GET/POST/PUT/DELETE /api/lms/problems/`
- `GET/POST/PUT/DELETE /api/lms/diagram-types/`

---

## 6. **Security**
- Only authenticated admin can access the CMS
- All API calls require admin token

---

## 7. **Extensibility**
- Support for new lesson/problem types in the future
- Analytics dashboard for admin (optional)
- Notification system for content changes (optional)

---

## 8. **Wireframe Inspiration**
- See attached screenshots for layout inspiration (Brilliant.org style)
- Focus on minimal clicks, inline editing, and instant preview

---

## 9. **Tech Stack Suggestions**
- **Frontend:** React (with MUI, Ant Design, or Chakra UI)
- **State Management:** Redux, Zustand, or Context API
- **Rich Text/Media:** TipTap, Quill, or CKEditor
- **Authentication:** JWT-based admin login

---

## 10. **Summary**
- The goal is to make course and lesson creation as easy and smooth as possible for a single admin.
- Focus on UX: minimal friction, instant feedback, and robust validation.
- Support all lesson/problem types needed for Garaad's LMS.

---

For any questions or clarifications, contact the backend team. 