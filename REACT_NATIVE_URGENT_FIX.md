# URGENT FIX - React Native Upload Issue

## Problem Summary

Your React Native app is getting errors when uploading documents because of how FormData sends integer values.

---

## ✅ THE FIX (1 Line Change)

### ❌ Current Code (WRONG):
```javascript
formData.append('driver_user_id', 8);  // Number - NOT RECOGNIZED!
```

### ✅ Fixed Code (CORRECT):
```javascript
formData.append('driver_user_id', '8');  // String - WORKS!
// OR
formData.append('driver_user_id', driverUserId.toString());  // Convert to string
```

---

## Complete Working Code

```javascript
const uploadDocument = async (fileUri, driverUserId, token) => {
    const formData = new FormData();
    
    // Add file
    formData.append('files', {
        uri: fileUri,
        name: '1000000026.jpg',
        type: 'image/jpeg'
    });
    
    // ⚠️ CRITICAL: Convert to string!
    formData.append('driver_user_id', driverUserId.toString());
    
    try {
        const response = await fetch('http://your-api-url/documents/upload', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'multipart/form-data'
            },
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            console.error('Upload failed:', error);
            throw new Error(error.detail || 'Upload failed');
        }
        
        const result = await response.json();
        console.log('Upload successful:', result);
        return result;
        
    } catch (error) {
        console.error('Upload error:', error);
        throw error;
    }
};

// Usage
const fileUri = 'file:///path/to/image.jpg';
const driverUserId = 8;  // Your driver's user ID
const token = 'your_auth_token';

uploadDocument(fileUri, driverUserId, token)
    .then(results => {
        console.log('Success!', results[0].message);
        // results[0].document_id
        // results[0].mob_status
    })
    .catch(error => {
        console.error('Failed!', error.message);
    });
```

---

## Why This Happens

**React Native's FormData** handles numbers differently than web browsers:

- **Web Browser**: `formData.append('id', 8)` → Sent as `"8"` (string)
- **React Native**: `formData.append('id', 8)` → Sent as binary number (NOT recognized as form field!)

**Solution**: Always convert to string using `.toString()`

---

## Expected Success Response

```json
[
    {
        "document_id": 123,
        "filename": "uuid-generated-name.jpg",
        "file_size": 245678,
        "message": "Uploaded Successfully",
        "selected_order_number": "ORD-112-2025",
        "customer_code": "LLTP1",
        "bill_to_code": "HILR1",
        "driver_id": 8,
        "web_status": "Sent to Imaging",
        "mob_status": "Uploaded Successfully - Verification Pending",
        "processing_started": true
    }
]
```

---

## Common Errors & Solutions

### Error 1: "Field required" for driver_user_id
```json
{
    "detail": "Either 'order_number' or 'driver_user_id' must be provided"
}
```
**Cause**: `driver_user_id` sent as number instead of string  
**Fix**: Use `.toString()` to convert to string

---

### Error 2: "No active order found for driver"
```json
{
    "detail": "No active order found for driver with user ID 8"
}
```
**Cause**: Driver doesn't have an active order assigned  
**Fix**: Ensure driver has an active order in the system before uploading

---

### Error 3: "No files provided"
```json
{
    "detail": "No files provided. Please upload at least one file using the 'files' field in multipart/form-data"
}
```
**Cause**: File not properly added to FormData  
**Fix**: Ensure file object has `uri`, `name`, and `type` properties

---

## Testing Checklist

Before testing, verify:

- [ ] `driver_user_id` is converted to string using `.toString()`
- [ ] File object has correct structure:
  ```javascript
  {
      uri: 'file://...',
      name: 'filename.jpg',
      type: 'image/jpeg'
  }
  ```
- [ ] Authorization header includes Bearer token
- [ ] Driver has an active order in the system
- [ ] Content-Type is set to `multipart/form-data`

---

## Server Changes Made

The backend has been fixed to:

1. ✅ Accept `files` parameter gracefully
2. ✅ Log all upload requests for debugging
3. ✅ Provide clear error messages
4. ✅ Handle both string and integer `driver_user_id` (after conversion)

**You MUST restart the FastAPI server** for changes to take effect!

---

## Need Help?

If you still get errors after making this change:

1. Check the console logs for the exact error message
2. Verify the `driver_user_id` value before calling `.toString()`
3. Confirm the driver has an active order
4. Check that the file URI is valid and accessible

---

**Last Updated**: February 22, 2026  
**Status**: ✅ Ready to test after applying the .toString() fix

