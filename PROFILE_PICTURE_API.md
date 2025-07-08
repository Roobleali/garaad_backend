# Profile Picture API - Frontend Guide

## Overview
This guide explains how to implement profile picture upload, update, and delete functionality in the frontend application.

## Base URL
```
https://api.garaad.org/api/auth/
```

## Authentication
All endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 📋 Available Endpoints

### 1. Get User Profile (includes profile picture)
```http
GET /api/auth/user-profile/
```

### 2. Upload/Update Profile Picture
```http
POST /api/auth/upload-profile-picture/
```

### 3. Update User Profile (text fields + optional picture)
```http
PUT /api/auth/update-user-profile/
```

### 4. Delete Profile Picture
```http
DELETE /api/auth/delete-profile-picture/
```

---

## 🖼️ File Requirements

**Supported Formats:**
- JPG/JPEG
- PNG
- GIF
- BMP

**File Size Limit:** 5MB maximum

**Storage Location:** Files are saved to `media/profile_pics/` directory

---

## 💻 JavaScript Implementation

### Basic Upload Function
```javascript
const uploadProfilePicture = async (file, token) => {
  const formData = new FormData();
  formData.append('profile_picture', file);

  try {
    const response = await fetch('/api/auth/upload-profile-picture/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData, // Don't set Content-Type, let browser set it
    });

    const data = await response.json();
    
    if (response.ok) {
      console.log('Profile picture uploaded:', data.user.profile_picture);
      return data;
    } else {
      console.error('Error:', data.error);
      throw new Error(data.error);
    }
  } catch (error) {
    console.error('Upload failed:', error);
    throw error;
  }
};
```

### Update Profile (with optional picture)
```javascript
const updateUserProfile = async (profileData, token) => {
  const formData = new FormData();
  
  // Add text fields
  if (profileData.first_name) formData.append('first_name', profileData.first_name);
  if (profileData.last_name) formData.append('last_name', profileData.last_name);
  if (profileData.bio) formData.append('bio', profileData.bio);
  
  // Add profile picture if provided
  if (profileData.profile_picture) {
    formData.append('profile_picture', profileData.profile_picture);
  }

  try {
    const response = await fetch('/api/auth/update-user-profile/', {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });

    const data = await response.json();
    
    if (response.ok) {
      return data;
    } else {
      throw new Error(data.error || 'Update failed');
    }
  } catch (error) {
    console.error('Profile update failed:', error);
    throw error;
  }
};
```

### Delete Profile Picture
```javascript
const deleteProfilePicture = async (token) => {
  try {
    const response = await fetch('/api/auth/delete-profile-picture/', {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await response.json();
    
    if (response.ok) {
      console.log('Profile picture deleted');
      return data;
    } else {
      throw new Error(data.error);
    }
  } catch (error) {
    console.error('Delete failed:', error);
    throw error;
  }
};
```

---

## ⚛️ React Component Example

```jsx
import React, { useState } from 'react';

const ProfilePictureUpload = ({ currentUser, onUpdate, token }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [preview, setPreview] = useState(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file size (5MB limit)
      if (file.size > 5 * 1024 * 1024) {
        alert('Sawirka ma noqon karo in uu ka weyn yahay 5MB');
        return;
      }

      // Validate file type
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp'];
      if (!validTypes.includes(file.type)) {
        alert('Nooca faylka aan la aqbalin. Isticmaal JPG, PNG, GIF, ama BMP.');
        return;
      }

      setSelectedFile(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target.result);
      reader.readAsDataURL(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    try {
      const result = await uploadProfilePicture(selectedFile, token);
      if (result) {
        onUpdate(result.user); // Update parent component
        setSelectedFile(null);
        setPreview(null);
        alert('Sawirka profile-ka ayaa si guul leh loo cusbooneysiyey');
      }
    } catch (error) {
      alert('Qalad ayaa dhacay: ' + error.message);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Ma hubtaa inaad tirtirto sawirka profile-ka?')) return;

    try {
      await deleteProfilePicture(token);
      onUpdate({ ...currentUser, profile_picture: null });
      alert('Sawirka profile-ka ayaa la tirtiray');
    } catch (error) {
      alert('Qalad ayaa dhacay: ' + error.message);
    }
  };

  return (
    <div className="profile-picture-upload">
      <div className="current-picture">
        {currentUser.profile_picture ? (
          <img 
            src={currentUser.profile_picture} 
            alt="Sawirka Profile-ka"
            className="profile-image"
            style={{ width: '150px', height: '150px', objectFit: 'cover', borderRadius: '50%' }}
          />
        ) : (
          <div className="no-picture" style={{ 
            width: '150px', 
            height: '150px', 
            borderRadius: '50%', 
            backgroundColor: '#f0f0f0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            Ma jiro sawir
          </div>
        )}
      </div>

      {preview && (
        <div className="preview">
          <h4>Preview:</h4>
          <img 
            src={preview} 
            alt="Preview" 
            style={{ width: '100px', height: '100px', objectFit: 'cover', borderRadius: '50%' }}
          />
        </div>
      )}
      
      <div className="controls">
        <input
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          className="file-input"
          style={{ marginBottom: '10px' }}
        />
        
        {selectedFile && (
          <button 
            onClick={handleUpload} 
            disabled={uploading}
            className="upload-button"
            style={{ marginRight: '10px' }}
          >
            {uploading ? 'Waa la soo gelayaa...' : 'Soo geli sawirka'}
          </button>
        )}
        
        {currentUser.profile_picture && (
          <button 
            onClick={handleDelete}
            className="delete-button"
            style={{ backgroundColor: '#dc3545', color: 'white' }}
          >
            Tirtir sawirka
          </button>
        )}
      </div>
    </div>
  );
};

export default ProfilePictureUpload;
```

---

## 📝 Response Formats

### Success Response (Upload/Update)
```json
{
  "message": "Sawirka profile-ka ayaa si guul leh loo cusbooneysiyey",
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com",
    "first_name": "Ahmed",
    "last_name": "Hassan",
    "profile_picture": "https://api.garaad.org/media/profile_pics/user123_profile.jpg",
    "bio": "Waxaan ahay arday xiiseysan waxbarashada...",
    "age": 25,
    "is_premium": true,
    "is_email_verified": true
  }
}
```

### User Profile Response
```json
{
  "id": 1,
  "username": "user123",
  "email": "user@example.com",
  "first_name": "Ahmed",
  "last_name": "Hassan",
  "profile_picture": "https://api.garaad.org/media/profile_pics/user123_profile.jpg",
  "bio": "Bio text here...",
  "age": 25,
  "is_premium": true,
  "has_completed_onboarding": true,
  "referral_code": "ABC123XY",
  "referral_points": 50,
  "referral_count": 3,
  "referred_by_username": null,
  "is_email_verified": true
}
```

### Delete Success Response
```json
{
  "message": "Sawirka profile-ka ayaa la tirtiray"
}
```

---

## ⚠️ Error Messages (in Somali)

| Error | Message |
|-------|---------|
| File too large | "Sawirka profile-ka ma noqon karo in uu ka weyn yahay 5MB" |
| Invalid format | "Nooca faylka aan la aqbalin. Isticmaal JPG, PNG, GIF, ama BMP." |
| Missing file | "Sawirka profile-ka ayaa loo baahan yahay" |
| No picture to delete | "Ma jiro sawir profile ah" |

### Error Response Format
```json
{
  "error": "Sawirka profile-ka ma noqon karo in uu ka weyn yahay 5MB"
}
```

---

## 🔍 Testing Tips

1. **File Size Testing**: Try uploading files larger than 5MB to test validation
2. **Format Testing**: Try uploading non-image files to test format validation
3. **Authentication Testing**: Test without token to ensure 401 responses
4. **Network Error Handling**: Test with poor connectivity

---

## 📱 Mobile Considerations

For mobile apps (React Native), use similar approach but with different file selection:

```javascript
// React Native example
import { launchImageLibrary } from 'react-native-image-picker';

const selectImage = () => {
  launchImageLibrary(
    {
      mediaType: 'photo',
      maxWidth: 1000,
      maxHeight: 1000,
      quality: 0.8,
    },
    (response) => {
      if (response.assets && response.assets[0]) {
        const file = {
          uri: response.assets[0].uri,
          type: response.assets[0].type,
          name: response.assets[0].fileName || 'profile.jpg',
        };
        uploadProfilePicture(file, token);
      }
    }
  );
};
```

---

## 🎯 Quick Integration Checklist

- [ ] Add file input with image accept attribute
- [ ] Implement file size validation (5MB max)
- [ ] Implement file type validation
- [ ] Add upload progress indicator
- [ ] Handle success/error responses
- [ ] Update UI with new profile picture URL
- [ ] Add delete functionality
- [ ] Test with different file sizes and formats
- [ ] Implement error handling with Somali messages
- [ ] Add loading states for better UX

---

**Need Help?** Contact the backend team for any API-related questions! 