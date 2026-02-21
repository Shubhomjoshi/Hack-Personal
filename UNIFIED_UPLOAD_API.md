# 📄 Unified Document Upload API
## ✅ API Merged Successfully!
The two separate endpoints have been merged into one powerful, flexible endpoint:
### ❌ Old Endpoints (REMOVED):
- ~~POST /api/documents/upload~~ (single file)
- ~~POST /api/documents/upload-multiple~~ (multiple files)
### ✅ New Unified Endpoint:
**POST /api/documents/upload** (handles both single and multiple files)
---
## 🎯 Key Features
✅ **Single Endpoint**: One API for all upload scenarios
✅ **Flexible**: Accepts 1 file or multiple files
✅ **Error Handling**: Per-file error tracking in batch uploads
✅ **Background Processing**: OCR, quality check, classification, validation
✅ **Consistent Response**: Always returns array (even for single file)
✅ **Backward Compatible**: Frontend can send single or multiple files
---
## 📡 API Specification
### Endpoint
```
POST /api/documents/upload
```
### Headers
```
Authorization: Bearer <your_jwt_token>
Content-Type: multipart/form-data
```
### Request Body (Form Data)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| files | File[] | Yes | One or more files (PDF, JPG, PNG, TIFF) |
| customer_id | integer | No | Customer ID for validation rules |
### Response (200 OK)
Returns: **Array of DocumentUploadResponse** (always an array, even for single file)
```json
[
  {
    "document_id": 123,
    "filename": "abc123-def456.pdf",
    "file_size": 245678,
    "message": "Uploaded Successfully",
    "web_status": "Sent to Imaging",
    "mob_status": "Uploaded Successfully - Verification Pending",
    "processing_started": true
  }
]
```
---
## 💻 Usage Examples
### Example 1: Upload Single File (JavaScript/Fetch)
```javascript
// Single file upload
const formData = new FormData();
formData.append('files', fileInput.files[0]);
const response = await fetch('http://localhost:8000/api/documents/upload', {
  method: 'POST',
  headers: {
    'Authorization': Bearer ${token}
  },
  body: formData
});
const results = await response.json();
console.log('Upload result:', results[0]); // Note: results is an array
```
### Example 2: Upload Multiple Files (JavaScript/Fetch)
```javascript
// Multiple files upload
const formData = new FormData();
for (let file of fileInput.files) {
  formData.append('files', file);
}
const response = await fetch('http://localhost:8000/api/documents/upload', {
  method: 'POST',
  headers: {
    'Authorization': Bearer ${token}
  },
  body: formData
});
const results = await response.json();
console.log(Uploaded ${results.length} files);
results.forEach((result, index) => {
  console.log(File ${index + 1}: ${result.message});
});
```
### Example 3: React with Axios
```javascript
import axios from 'axios';
// Works for both single and multiple files!
const uploadFiles = async (files) => {
  const formData = new FormData();
  // Handle single file or array of files
  const fileArray = Array.isArray(files) ? files : [files];
  fileArray.forEach(file => {
    formData.append('files', file);
  });
  try {
    const response = await axios.post('/api/documents/upload', formData, {
      headers: {
        'Authorization': Bearer ${localStorage.getItem('token')},
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data; // Array of results
  } catch (error) {
    console.error('Upload failed:', error);
    throw error;
  }
};
// Usage examples:
// Single file: await uploadFiles(singleFile);
// Multiple files: await uploadFiles([file1, file2, file3]);
```
### Example 4: Python Requests
```python
import requests
# Single file
files = {'files': open('document.pdf', 'rb')}
response = requests.post(
    'http://localhost:8000/api/documents/upload',
    files=files,
    headers={'Authorization': f'Bearer {token}'}
)
print(response.json())
# Multiple files
files = [
    ('files', open('document1.pdf', 'rb')),
    ('files', open('document2.pdf', 'rb')),
    ('files', open('document3.jpg', 'rb'))
]
response = requests.post(
    'http://localhost:8000/api/documents/upload',
    files=files,
    headers={'Authorization': f'Bearer {token}'}
)
print(response.json())
```
### Example 5: cURL
```bash
# Single file
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@document.pdf"
# Multiple files
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@document1.pdf" \
  -F "files=@document2.jpg" \
  -F "files=@document3.png"
# With customer_id
curl -X POST "http://localhost:8000/api/documents/upload?customer_id=123" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@document.pdf"
```
---
## 🎨 Frontend Component Examples
### React Component (Complete)
```jsx
import React, { useState } from 'react';
import axios from 'axios';
const DocumentUploader = () => {
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState([]);
  const handleUpload = async (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;
    setUploading(true);
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    try {
      const response = await axios.post(
        '/api/documents/upload',
        formData,
        {
          headers: {
            'Authorization': Bearer ${localStorage.getItem('token')},
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      setResults(response.data);
      alert(Successfully uploaded ${response.data.length} file(s)!);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed: ' + error.message);
    } finally {
      setUploading(false);
    }
  };
  return (
    <div>
      <input
        type="file"
        multiple
        accept=".pdf,.jpg,.jpeg,.png,.tiff"
        onChange={handleUpload}
        disabled={uploading}
      />
      {uploading && <p>Uploading...</p>}
      {results.length > 0 && (
        <div>
          <h3>Upload Results:</h3>
          <ul>
            {results.map((result, index) => (
              <li key={index}>
                <strong>{result.filename}</strong>: {result.message}
                {result.processing_started && ' ✅'}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
export default DocumentUploader;
```
### Vue 3 Component
```vue
<template>
  <div>
    <input
      type="file"
      multiple
      accept=".pdf,.jpg,.jpeg,.png,.tiff"
      @change="handleUpload"
      :disabled="uploading"
    />
    <p v-if="uploading">Uploading...</p>
    <div v-if="results.length > 0">
      <h3>Upload Results:</h3>
      <ul>
        <li v-for="(result, index) in results" :key="index">
          <strong>{{ result.filename }}</strong>: {{ result.message }}
          <span v-if="result.processing_started"> ✅</span>
        </li>
      </ul>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue';
import axios from 'axios';
const uploading = ref(false);
const results = ref([]);
const handleUpload = async (event) => {
  const files = Array.from(event.target.files);
  if (files.length === 0) return;
  uploading.value = true;
  const formData = new FormData();
  files.forEach(file => {
    formData.append('files', file);
  });
  try {
    const response = await axios.post('/api/documents/upload', formData, {
      headers: {
        'Authorization': Bearer ${localStorage.getItem('token')},
        'Content-Type': 'multipart/form-data'
      }
    });
    results.value = response.data;
    alert(Successfully uploaded ${response.data.length} file(s)!);
  } catch (error) {
    console.error('Upload failed:', error);
    alert('Upload failed: ' + error.message);
  } finally {
    uploading.value = false;
  }
};
</script>
```
---
## 🔍 Error Handling
### Partial Success Scenario
When uploading multiple files, some may succeed and others may fail:
```json
[
  {
    "document_id": 123,
    "filename": "abc-123.pdf",
    "file_size": 245678,
    "message": "Uploaded Successfully",
    "processing_started": true
  },
  {
    "document_id": 0,
    "filename": "invalid.txt",
    "file_size": 0,
    "message": "File type not supported: .txt. Allowed: .pdf, .jpg, .jpeg, .png, .tiff",
    "web_status": "Upload Failed",
    "mob_status": "File type not supported",
    "processing_started": false
  },
  {
    "document_id": 124,
    "filename": "def-456.jpg",
    "file_size": 123456,
    "message": "Uploaded Successfully",
    "processing_started": true
  }
]
```
### Frontend Error Handling
```javascript
const results = await uploadFiles(files);
const succeeded = results.filter(r => r.processing_started);
const failed = results.filter(r => !r.processing_started);
console.log(✅ Uploaded: ${succeeded.length});
console.log(❌ Failed: ${failed.length});
if (failed.length > 0) {
  console.error('Failed files:', failed.map(f => f.filename));
}
```
---
## 📋 Migration Guide
### For Frontend Developers
#### Before (Old Code):
```javascript
// Single file - old endpoint
await axios.post('/api/documents/upload', formData);
// Multiple files - old endpoint
await axios.post('/api/documents/upload-multiple', formData);
```
#### After (New Code):
```javascript
// Both single and multiple files - ONE endpoint
await axios.post('/api/documents/upload', formData);
// ⚠️ Important: Response is now ALWAYS an array!
const results = await axios.post('/api/documents/upload', formData);
// For single file, access first element:
const result = results.data[0];
// For multiple files, iterate:
results.data.forEach(result => {
  console.log(result.message);
});
```
### Breaking Changes
⚠️ **Response Format Changed for Single File Upload:**
- **Before**: Single object { document_id: 123, ... }
- **After**: Array with one object [{ document_id: 123, ... }]
**Fix:** Access esults[0] for single file uploads.
---
## ✅ Benefits of Merged API
| Benefit | Description |
|---------|-------------|
| 🎯 **Simplicity** | One endpoint to remember and maintain |
| 🔄 **Flexibility** | Works for 1 file or 1000 files |
| 📦 **Consistency** | Same response format always |
| 🛡️ **Better Error Handling** | Per-file errors in batch uploads |
| 📱 **Mobile Friendly** | Same API for web and mobile |
| 🧪 **Easier Testing** | Single endpoint to test |
| 📚 **Less Documentation** | One API to document |
---
## 🧪 Testing
Test the unified endpoint at: **http://localhost:8000/docs**
1. Start server: uvicorn main:app --reload
2. Go to Swagger UI: http://localhost:8000/docs
3. Find POST /api/documents/upload
4. Click "Try it out"
5. Upload single or multiple files
6. See results!
---
## 📞 Support
If you encounter issues:
- Check that files are within allowed types: .pdf, .jpg, .jpeg, .png, .tiff
- Verify JWT token is valid
- Check response array for per-file error messages
- Review server logs for detailed error information
---
**Status**: ✅ COMPLETE - Ready to use!
