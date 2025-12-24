# Frontend Integration Guide: Community Features V2

This guide details the updated API structure for the Community features.
**Major Change**: Campuses are now simplified to: **SaaS, AI, Physics, Math**.

---

## 1. Campuses (Subjects)

The community is divided into 4 main campuses.

### List Campuses
*   **Endpoint**: `GET /api/community/campuses/`
*   **Response**:
    ```json
    [
        {
            "id": 1,
            "subject_tag": "saas",
            "name": "SaaS",
            "description": "Software as a Service discussions.",
            "icon": "💻",
            "member_count": 42,
            "user_is_member": true
        },
        ...
    ]
    ```

### Join Campus
*   **Endpoint**: `POST /api/community/campuses/{slug}/join/`
*   **Slug Values**: `saas`, `ai`, `physics`, `math`
*   **Header**: `Authorization: Bearer <token>`

---

## 2. Rooms (Discussions)

Each campus has default rooms:
*   `sheeko-guud` (General Chat)
*   `waxbarasho` (Learning/Help)
*   `ogeysiisyada` (Announcements)

### Get Rooms
*   **Endpoint**: `GET /api/community/rooms/?campus={slug}`
*   **Response**:
    ```json
    [
        {
            "id": "uuid...",
            "name": "sheeko-guud",
            "room_type": "text",
            "is_locked": false, 
            ...
        }
    ]
    ```

---

## 3. Conversations (Posts & Messages)

Two types of conversations exist:
1.  **Posts** (Reddit-style): Threads with titles and comments. Best for questions/resources.
2.  **Messages** (Discord-style): Real-time chat in rooms.

### A. Posts (Threaded)
*   **List Posts**: `GET /api/community/posts/?room={room_id}`
*   **Create Post**: `POST /api/community/posts/`
    *   Body: `{ "title": "...", "content": "...", "room_id": "...", "post_type": "text" }`
*   **Like Post**: `POST /api/community/posts/{id}/like/`

### B. Messages (Real-time Chat)
*   **List Messages**: `GET /api/community/messages/?room={room_id}`
*   **Response**: Returns list of messages with nested `reactions`.

---

## 4. Replies & Interactions

### Comments (On Posts)
*   **Get Comments**: `GET /api/community/comments/?post={post_id}`
*   **Add Comment**: `POST /api/community/comments/`
    *   Body: `{ "post_id": "...", "content": "..." }`
*   **Reply to Comment**:
    *   Body: `{ "post_id": "...", "parent_comment_id": "...", "content": "..." }`
*   **Like Comment**: `POST /api/community/comments/{id}/like/`

### Reactions (On Messages)
*   **React**: `POST /api/community/messages/{id}/react/`
    *   Body: `{ "emoji": "👍" }`
*   **Remove Reaction**: Send same emoji again (toggle).

---

## 5. Real-time (WebSockets)

*   **URL**: `wss://api.garaad.org/ws/community/?token={jwt_token}`
*   **Events**:
    *   Server broadcasts messages to all connected clients in the room.
    *   **Sending a Message**:
        ```json
        {
            "type": "chat_message",
            "message": {
                "content": "Hello world",
                "room_id": "...", 
                "user_id": 123
            }
        }
        ```
