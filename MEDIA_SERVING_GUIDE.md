# 🖼️ Media File Serving Guide - Frontend Integration

## ✅ Problem Solved

Your frontend uploads profile pictures successfully, but the images don't display because the backend now serves media files with authentication and security.

## 🚀 Implementation Complete

The backend now includes secure media serving endpoints that:
- ✅ Require authentication (JWT token)
- ✅ Prevent directory traversal attacks
- ✅ Support multiple file types (images, videos, documents)
- ✅ Include proper cache headers for performance
- ✅ Handle CORS for cross-origin requests

---

## 📋 API Endpoints

### Base URL
All media endpoints are under: `https://api.garaad.org/api/media/`

### Authentication Required
All endpoints require JWT Bearer token in the Authorization header:
```javascript
headers: {
  'Authorization': 'Bearer YOUR_JWT_TOKEN',
  'Content-Type': 'application/json'
}
```

---

## 🔗 Available Endpoints

### 1. Generic Media Serving
```
GET /api/media/<path:file_path>
```
Serves any file from the media directory with path validation.

**Example:**
```javascript
// Serve any file from media directory
const imageUrl = 'https://api.garaad.org/api/media/profile_pics/user123.jpg';
```

### 2. Profile Pictures
```
GET /api/media/profile_pics/<filename>
```
Specific endpoint for profile pictures.

**Example:**
```javascript
// Get user profile picture
const profilePicUrl = `https://api.garaad.org/api/media/profile_pics/${filename}`;
```

### 3. Community Post Images
```
GET /api/media/community/posts/<filename>
```
Specific endpoint for community post images.

**Example:**
```javascript
// Get community post image
const postImageUrl = `https://api.garaad.org/api/media/community/posts/${filename}`;
```

### 4. Course Images
```
GET /api/media/courses/<filename>
```
Specific endpoint for course images.

**Example:**
```javascript
// Get course thumbnail
const courseImageUrl = `https://api.garaad.org/api/media/courses/${filename}`;
```

### 5. Health Check
```
GET /api/media/health/
```
Check if media serving is operational (no auth required).

---

## 🎯 Frontend Implementation

### React Component Example

```jsx
import React, { useState, useEffect } from 'react';

const ProfilePicture = ({ filename, alt = "Profile picture", className = "" }) => {
  const [imageUrl, setImageUrl] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!filename) {
      setLoading(false);
      return;
    }

    const fetchImage = async () => {
      try {
        const token = localStorage.getItem('access_token'); // or from your auth context
        
        const response = await fetch(
          `https://api.garaad.org/api/media/profile_pics/${filename}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
            }
          }
        );

        if (!response.ok) {
          if (response.status === 401) {
            throw new Error('Authentication required');
          } else if (response.status === 404) {
            throw new Error('Image not found');
          } else {
            throw new Error('Failed to load image');
          }
        }

        // Convert response to blob URL
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setImageUrl(url);
        setError(null);
      } catch (err) {
        setError(err.message);
        console.error('Error loading profile picture:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchImage();

    // Cleanup blob URL on unmount
    return () => {
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl);
      }
    };
  }, [filename]);

  if (loading) {
    return <div className={`${className} loading-placeholder`}>Loading...</div>;
  }

  if (error) {
    return (
      <div className={`${className} error-placeholder`}>
        <span>👤</span> {/* Default avatar emoji */}
      </div>
    );
  }

  return (
    <img 
      src={imageUrl} 
      alt={alt}
      className={className}
      onError={() => setError('Failed to load image')}
    />
  );
};

export default ProfilePicture;
```

### Hook for Media URLs

```javascript
// hooks/useMediaUrl.js
import { useMemo } from 'react';

export const useMediaUrl = (filename, type = 'profile_pics') => {
  const mediaUrl = useMemo(() => {
    if (!filename) return null;
    
    const baseUrl = 'https://api.garaad.org/api/media';
    
    switch (type) {
      case 'profile_pics':
        return `${baseUrl}/profile_pics/${filename}`;
      case 'community_posts':
        return `${baseUrl}/community/posts/${filename}`;
      case 'courses':
        return `${baseUrl}/courses/${filename}`;
      default:
        return `${baseUrl}/${filename}`;
    }
  }, [filename, type]);

  return mediaUrl;
};

// Usage
const ProfileComponent = ({ user }) => {
  const profilePicUrl = useMediaUrl(user.profile_picture, 'profile_pics');
  
  return (
    <div>
      {profilePicUrl ? (
        <img src={profilePicUrl} alt="Profile" />
      ) : (
        <div className="default-avatar">👤</div>
      )}
    </div>
  );
};
```

### Axios Configuration

```javascript
// api/mediaApi.js
import axios from 'axios';

const mediaApi = axios.create({
  baseURL: 'https://api.garaad.org/api/media',
});

// Add auth token to all requests
mediaApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle media responses
mediaApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle authentication error
      console.error('Authentication required for media access');
    } else if (error.response?.status === 404) {
      // Handle file not found
      console.error('Media file not found');
    }
    return Promise.reject(error);
  }
);

export const getProfilePicture = (filename) => 
  mediaApi.get(`/profile_pics/${filename}`, { responseType: 'blob' });

export const getCommunityPostImage = (filename) => 
  mediaApi.get(`/community/posts/${filename}`, { responseType: 'blob' });

export const getCourseImage = (filename) => 
  mediaApi.get(`/courses/${filename}`, { responseType: 'blob' });

export const checkMediaHealth = () => 
  mediaApi.get('/health/');
```

### Error Handling Component

```jsx
// components/MediaErrorBoundary.jsx
import React from 'react';

class MediaErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Media loading error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <div>🖼️</div>;
    }

    return this.props.children;
  }
}

export default MediaErrorBoundary;
```

---

## 🎨 CSS Styling Examples

### Loading States
```css
.loading-placeholder {
  width: 100px;
  height: 100px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 50%;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.error-placeholder {
  width: 100px;
  height: 100px;
  background: #f8f9fa;
  border: 2px dashed #dee2e6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
}
```

### Responsive Images
```css
.profile-picture {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.post-image {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.course-thumbnail {
  width: 200px;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
}
```

---

## 🔧 Testing & Debugging

### Test Media Health
```javascript
// Test if media serving is working
const testMediaHealth = async () => {
  try {
    const response = await fetch('https://api.garaad.org/api/media/health/');
    const data = await response.json();
    console.log('Media health:', data);
    return data.status === 'healthy';
  } catch (error) {
    console.error('Media health check failed:', error);
    return false;
  }
};
```

### Debug Media Loading
```javascript
// Debug function for media loading issues
const debugMediaLoading = async (filename, type = 'profile_pics') => {
  const token = localStorage.getItem('access_token');
  
  console.log('Debugging media loading:', { filename, type, hasToken: !!token });
  
  try {
    const response = await fetch(
      `https://api.garaad.org/api/media/${type}/${filename}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      }
    );
    
    console.log('Response status:', response.status);
    console.log('Response headers:', Object.fromEntries(response.headers));
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Error response:', errorText);
    } else {
      console.log('Media loaded successfully');
    }
  } catch (error) {
    console.error('Network error:', error);
  }
};
```

### Browser Network Tab
Check these in your browser's Network tab:
1. **Request URL**: Should be `https://api.garaad.org/api/media/...`
2. **Request Headers**: Should include `Authorization: Bearer <token>`
3. **Response Status**: Should be 200 for success, 401 for auth error, 404 for not found
4. **Response Headers**: Should include `Content-Type: image/jpeg` etc.

---

## 🚨 Common Issues & Solutions

### Issue 1: 401 Unauthorized
**Problem**: Image requests return 401 status
**Solution**: 
- Ensure JWT token is included in request headers
- Check if token is expired and refresh if needed
- Verify token is stored correctly in localStorage

```javascript
// Check token validity
const checkToken = () => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    console.error('No access token found');
    return false;
  }
  
  // Decode JWT to check expiration
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const isExpired = payload.exp * 1000 < Date.now();
    
    if (isExpired) {
      console.error('Token is expired');
      return false;
    }
    
    return true;
  } catch (error) {
    console.error('Invalid token format');
    return false;
  }
};
```

### Issue 2: 404 Not Found
**Problem**: Image requests return 404 status
**Solution**:
- Verify the filename exists in the media directory
- Check the file path is correct
- Ensure the file was uploaded successfully

### Issue 3: CORS Errors
**Problem**: Cross-origin request blocked
**Solution**: 
- The backend includes CORS headers
- Ensure your frontend domain is in the allowed origins
- Check if the request includes proper headers

### Issue 4: Images Not Loading
**Problem**: Images appear broken or don't load
**Solution**:
- Check browser console for errors
- Verify the image URL is correct
- Test the URL directly in browser (with auth token)
- Check if the file exists on the server

---

## 📱 Mobile Considerations

### Responsive Images
```jsx
// Responsive image component
const ResponsiveImage = ({ src, alt, sizes = "100vw" }) => {
  return (
    <img
      src={src}
      alt={alt}
      sizes={sizes}
      style={{
        width: '100%',
        height: 'auto',
        maxWidth: '100%'
      }}
      loading="lazy"
    />
  );
};
```

### Lazy Loading
```jsx
// Lazy loading hook
const useLazyImage = (src) => {
  const [imageSrc, setImageSrc] = useState(null);
  const [loading, setLoading] = useState(true);
  const imgRef = useRef();

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && src) {
          setImageSrc(src);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, [src]);

  return { imageSrc, loading, imgRef };
};
```

---

## 🔒 Security Notes

1. **Authentication Required**: All media endpoints require valid JWT token
2. **Path Validation**: Backend prevents directory traversal attacks
3. **File Type Validation**: Only allowed file types are served
4. **CORS Protection**: Proper CORS headers are included
5. **Cache Headers**: Images are cached for performance

---

## ✅ Checklist for Frontend Team

- [ ] Update image components to use new media URLs
- [ ] Add authentication headers to media requests
- [ ] Implement error handling for 401/404 responses
- [ ] Add loading states for media components
- [ ] Test with different file types (JPG, PNG, etc.)
- [ ] Verify mobile responsiveness
- [ ] Add fallback images for failed loads
- [ ] Test with expired tokens
- [ ] Implement lazy loading for better performance

---

## 🎉 Expected Result

After implementing these changes:

1. ✅ **Profile pictures display correctly**
2. ✅ **Community post images load properly**
3. ✅ **Course thumbnails show up**
4. ✅ **Authentication works seamlessly**
5. ✅ **Error handling provides good UX**
6. ✅ **Performance is optimized with caching**

Your media files will now display correctly with proper authentication and security! 🚀 