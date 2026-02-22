# Document Upload API - Mobile App Integration Guide

## Fixed Issue

**Problem:** Mobile app was getting `"Field required"` error for `files` parameter.

**Solution:** The `files` parameter is now optional in the function signature but still validates that files are provided with a clearer error message.

---

## API Endpoint

```
POST /documents/upload
Content-Type: multipart/form-data
```

**Authentication:** Bearer token required in `Authorization` header

---

## Request Parameters

### Mobile App Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `files` | File[] | **Yes** | One or more document files (PDF, JPG, PNG, TIFF) |
| `driver_user_id` | Integer | **Yes** | User ID of the driver (from users table) |
| `customer_id` | Integer | No | Customer ID for validation rules |

### Desktop App Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `files` | File[] | **Yes** | One or more document files |
| `order_number` | String | **Yes** | Order number (e.g., "ORD-112-2025") |
| `customer_id` | Integer | No | Customer ID for validation rules |

**Important:** Provide **either** `driver_user_id` (mobile) **or** `order_number` (desktop), not both.

---

## Mobile App Request Example

### Using JavaScript/Fetch

```javascript
const uploadDocument = async (file, driverUserId, token) => {
    const formData = new FormData();
    
    // Add file(s) - CRITICAL: Use "files" as the field name
    formData.append('files', file);
    
    // If multiple files
    // formData.append('files', file1);
    // formData.append('files', file2);
    
    // Add driver user ID
    formData.append('driver_user_id', driverUserId);
    
    // Optional: Add customer ID
    // formData.append('customer_id', 123);
    
    const response = await fetch('http://your-api.com/documents/upload', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`
            // DO NOT set Content-Type - browser sets it automatically with boundary
        },
        body: formData
    });
    
    if (!response.ok) {
        const error = await response.json();
        console.error('Upload failed:', error);
        throw new Error(error.detail);
    }
    
    return await response.json();
};

// Usage
const file = document.getElementById('fileInput').files[0];
const driverUserId = 5; // Current driver's user ID
const token = localStorage.getItem('access_token');

uploadDocument(file, driverUserId, token)
    .then(results => {
        console.log('Upload successful:', results);
        // results is an array of DocumentUploadResponse
        results.forEach(result => {
            console.log(`Document ${result.document_id}: ${result.message}`);
        });
    })
    .catch(error => {
        console.error('Upload error:', error);
    });
```

### Using React Native

```javascript
import axios from 'axios';

const uploadDocument = async (fileUri, driverUserId, token) => {
    const formData = new FormData();
    
    // Add file - React Native
    formData.append('files', {
        uri: fileUri,
        type: 'image/jpeg', // or 'application/pdf'
        name: 'document.jpg'
    });
    
    // Add driver user ID
    formData.append('driver_user_id', driverUserId.toString());
    
    try {
        const response = await axios.post(
            'http://your-api.com/documents/upload',
            formData,
            {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'multipart/form-data'
                }
            }
        );
        
        console.log('Upload successful:', response.data);
        return response.data;
    } catch (error) {
        console.error('Upload failed:', error.response?.data);
        throw error;
    }
};
```

### Using Flutter/Dart

```dart
import 'package:http/http.dart' as http;
import 'dart:io';

Future<void> uploadDocument(File file, int driverUserId, String token) async {
  var request = http.MultipartRequest(
    'POST',
    Uri.parse('http://your-api.com/documents/upload'),
  );
  
  // Add authentication header
  request.headers['Authorization'] = 'Bearer $token';
  
  // Add file - CRITICAL: Use "files" as the field name
  request.files.add(await http.MultipartFile.fromPath('files', file.path));
  
  // Add driver user ID
  request.fields['driver_user_id'] = driverUserId.toString();
  
  // Send request
  var response = await request.send();
  
  if (response.statusCode == 201) {
    var responseData = await response.stream.bytesToString();
    print('Upload successful: $responseData');
  } else {
    var errorData = await response.stream.bytesToString();
    print('Upload failed: $errorData');
    throw Exception('Upload failed');
  }
}
```

### Using Postman/curl

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "files=@/path/to/document.pdf" \
  -F "driver_user_id=5"
```

---

## Success Response

```json
[
    {
        "document_id": 123,
        "filename": "uuid-generated-name.pdf",
        "file_size": 245678,
        "message": "Uploaded Successfully",
        "selected_order_number": "ORD-112-2025",
        "customer_code": "LLTP1",
        "bill_to_code": "HILR1",
        "driver_id": 5,
        "web_status": "Sent to Imaging",
        "mob_status": "Uploaded Successfully - Verification Pending",
        "processing_started": true
    }
]
```

**Note:** Response is always an array, even for single file uploads.

---

## Error Responses

### Missing Files

```json
{
    "detail": "No files provided. Please upload at least one file using the 'files' field in multipart/form-data"
}
```

**Solution:** Ensure you're using `files` as the field name in FormData and the file is not null.

### Missing Driver User ID

```json
{
    "detail": "Either 'order_number' or 'driver_user_id' must be provided"
}
```

**Solution:** Add `driver_user_id` to the FormData.

### No Active Order for Driver

```json
{
    "detail": "No active order found for driver with user ID 5"
}
```

**Solution:** Ensure the driver has an active order in the `order_info` table.

### Invalid File Type

```json
[
    {
        "document_id": 0,
        "filename": "document.txt",
        "file_size": 0,
        "message": "File type not supported: .txt. Allowed: .pdf, .jpg, .jpeg, .png, .tiff",
        "web_status": "Upload Failed",
        "mob_status": "File type not supported",
        "processing_started": false
    }
]
```

**Solution:** Only upload PDF or image files (JPG, PNG, TIFF).

---

## Common Mistakes & Fixes

### ❌ WRONG: Sending driver_user_id as number in React Native

```javascript
formData.append('driver_user_id', 8); // WRONG - not recognized by API!
```

### ✅ CORRECT: Convert to string in React Native

```javascript
formData.append('driver_user_id', '8'); // Correct!
// OR
formData.append('driver_user_id', driverUserId.toString()); // Best practice
```

**Why:** React Native's FormData implementation handles numbers differently than web browsers. The API expects form field values as strings.

---

### ❌ WRONG: Using wrong field name

```javascript
formData.append('file', myFile); // Wrong field name
```

### ✅ CORRECT: Use "files" as field name

```javascript
formData.append('files', myFile); // Correct!
```

---

### ❌ WRONG: Setting Content-Type manually

```javascript
headers: {
    'Authorization': 'Bearer token',
    'Content-Type': 'multipart/form-data' // Don't set this manually
}
```

### ✅ CORRECT: Let browser/library set Content-Type

```javascript
headers: {
    'Authorization': 'Bearer token'
    // Browser will set Content-Type with boundary automatically
}
```

---

### ❌ WRONG: Sending JSON instead of FormData

```javascript
fetch('/documents/upload', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ files: file }) // Wrong!
})
```

### ✅ CORRECT: Use FormData for file uploads

```javascript
const formData = new FormData();
formData.append('files', file);
fetch('/documents/upload', {
    method: 'POST',
    body: formData // Correct!
})
```

---

## Background Processing Flow

After successful upload:

1. ✅ File saved to server
2. ✅ Document record created in database
3. ✅ Response sent immediately to mobile app
4. 🔄 **Background processing starts:**
   - Quality assessment (blurriness, skew)
   - OCR text extraction (EasyOCR + Gemini)
   - Document classification (BOL, POD, Invoice, etc.)
   - Signature detection (if BOL)
   - Metadata extraction (order#, date, etc.)
   - Rule validation
5. 💾 Database updated with processing results

---

## Checking Processing Status

After upload, poll this endpoint to check processing status:

```
GET /documents/{document_id}
```

**Response:**
```json
{
    "id": 123,
    "is_processed": true,
    "validation_status": "Pass",
    "document_type": "Bill of Lading",
    "quality_score": 87.5,
    "signature_count": 2,
    "order_number": "ORD-112-2025",
    ...
}
```

---

## Testing Checklist

- [ ] File is not null before adding to FormData
- [ ] Using `files` as field name (not `file` or `document`)
- [ ] Adding `driver_user_id` as integer
- [ ] Not setting `Content-Type` header manually
- [ ] Authorization Bearer token is included
- [ ] Driver has an active order in database
- [ ] File type is PDF, JPG, PNG, or TIFF
- [ ] File size is reasonable (< 10MB recommended)

---

## Debug Mode

To test upload without background processing:

```
POST /documents/{document_id}/test-process
```

This runs processing synchronously and returns detailed results including any errors.

---

**Last Updated:** February 22, 2026  
**API Version:** 1.0

