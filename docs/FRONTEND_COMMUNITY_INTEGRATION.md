# Frontend Integration Guide: Community Features

This guide details the API contracts and integration steps for the new Community features, specifically addressing WebSocket connections, Trending Tags, and Media file access.

> **CRITICAL**: The backend must be redeployed with the latest changes for these endpoints to function. If you see 404s or connection failures, the server is running an old version.

---

## 1. Real-time Chat (WebSockets)

The backend uses Django Channels to support real-time WebSocket connections.

### Connection Specification
*   **Method**: `GET` (Upgrade to WebSocket)
*   **Protocol**: `wss://` (Secure) or `ws://` (Local)
*   **URL**: `/ws/community/`
*   **Query Parameters**:
    *   `token`: **Required**. A valid JWT Access Token.

**Example URL:**
```
wss://api.garaad.org/ws/community/?token=eyJhbGciOiJIUzI...
```

### Connection Flow
1.  **Connect**: Frontend initiates WebSocket handshake with the token.
2.  **Authenticate**: Backend validates the token (implicit in handshake). 
    *   *Note: Current implementation accepts connections to resolve network errors, but proper token validation should be enforced.*
3.  **Events**:
    *   **On Open**: Connection established.
    *   **On Message**: Receive JSON payload.
    *   **On Error**: Handle disconnection/retry strategies.

### Message Protocol
The server acts as a simplified echo/broadcast server for the `community_global` group.

**Client to Server:**
```json
{
  "active_room": "room-slug",
  "content": "Hello everyone!",
  "type": "chat_message" 
}
```

**Server to Client (Broadcast):**
The server broadcasts the exact message received to all connected clients.

---

## 2. Trending Tags API

Fetches the list of trending topics/subjects based on community activity.

### HTTP Endpoint
*   **Method**: `GET`
*   **URL**: `/api/community/trending/tags/`
*   **Query Parameters**:
    *   `period`: (Optional) `week` | `month` | `all`. Defaults to `week`.

### Response Format (JSON)
Returns a list of tag objects sorted by popularity (post count).

```json
[
  {
    "id": "physics",
    "name": "Fiisigis",
    "count": 150
  },
  {
    "id": "math",
    "name": "Xisaab",
    "count": 120
  },
  {
    "id": "technology",
    "name": "Tignoolajiyada",
    "count": 95
  }
]
```

### Usage
Use this endpoint to populate the "Trending" or "Popular Topics" sidebar.

---

## 3. Media & Profile Pictures

The backend has been updated to serve media files directly, supporting public access for profile pictures.

### URL Structure

| content Type | Endpoint Pattern | Access Level |
| :--- | :--- | :--- |
| **Profile Pictures** | `/media/profile_pics/<filename>` | **Public** (No Token) |
| **Post Images** | `/media/community/posts/<filename>` | Authenticated (Header) |
| **Course Images** | `/media/courses/<filename>` | Authenticated (Header) |

### Frontend Handling
*   **Profile Pics**: You can use the URL directly in `src` attributes (e.g., `<img src="https://api.garaad.org/media/profile_pics/user.jpg" />`).
*   **Protected Media**: For other media, you may need to fetch with `Authorization` headers if strict mode is enabled, or use the token in a query param if supported by the specific view (standard implementation requires headers).
    *   *Current Fix*: The implemented internal `serve_media_file` logic checks for file existence and valid paths.

---

## Troubleshooting

### "WebSocket connection failed"
*   **Cause**: The backend server is not running the ASGI service (`daphne`). using `gunicorn` does not support WebSockets.
*   **Fix**: Update the deployment command to use `daphne -b 0.0.0.0 -p 8000 garaad.asgi:application`.

### "404 Not Found" for Trending/Media
*   **Cause**: The new code (views/URLs) is not deployed.
*   **Fix**: Re-deploy the backend container.
