# WebSocket Infrastructure Fix

## Problem
WebSocket connections are failing with "WebSocket is closed before the connection is established" because **Nginx is not configured to proxy WebSocket connections**.

The Dockerfile correctly uses Daphne, but Nginx (your reverse proxy) is rejecting WebSocket upgrade requests.

## Solution 1: Fix Nginx Configuration (Required for WebSockets)

Add this to your Nginx configuration for `api.garaad.org`:

```nginx
server {
    listen 443 ssl http2;
    server_name api.garaad.org;

    # ... your existing SSL config ...

    # Regular HTTP location
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket location - ADD THIS
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket timeout settings
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }
}
```

After updating:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Solution 2: Use REST API Instead (No Infrastructure Changes Needed)

Your backend **already has clean REST endpoints** that work perfectly. The frontend can use these instead of WebSockets:

### Community Posts API

```javascript
// Fetch posts for a category
GET /api/community/categories/{categoryId}/posts/

// Create a post
POST /api/community/categories/{categoryId}/posts/
{
  "content": "Post content here"
}

// React to a post
POST /api/community/posts/{postId}/react/
{
  "type": "like"  // or "fire", "insight"
}

// Reply to a post
POST /api/community/posts/{postId}/reply/
{
  "content": "Reply content"
}

// Edit a post
PATCH /api/community/posts/{postId}/
{
  "content": "Updated content"
}

// Delete a post
DELETE /api/community/posts/{postId}/
```

### Polling for Real-Time Updates (Simple Alternative)

Instead of WebSockets, use polling:

```javascript
// Poll every 5 seconds for new posts
setInterval(async () => {
  const response = await fetch(
    `https://api.garaad.org/api/community/categories/${categoryId}/posts/`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    }
  );
  const posts = await response.json();
  // Update UI with new posts
}, 5000);
```

## Recommendation

**For immediate functionality**: Use the REST API with polling (Solution 2). This works NOW with zero infrastructure changes.

**For real-time updates**: Fix Nginx configuration (Solution 1) when you have server access.

## Current API Status

✅ **Working**: All REST endpoints
- Categories
- Posts (create, read, update, delete)
- Replies
- Reactions
- User authentication

❌ **Not Working**: WebSockets (requires Nginx configuration)
