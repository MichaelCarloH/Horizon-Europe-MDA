# API Documentation

## Overview

The Horizon Europe MDA API provides a comprehensive set of endpoints for document
management, query processing, and system administration. The API is built using FastAPI and
follows RESTful principles.

## Base URL

- Development: `http://localhost:8000`
- Production: `https://api.horizon-europe-mda.com`

## Authentication

### JWT Authentication

All API endpoints require JWT authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

### Getting a Token

```http
POST /auth/token
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

Response:
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer"
}
```

## Endpoints

### Health Check

```http
GET /health
```

Response:
```json
{
    "status": "healthy",
    "version": "1.0.0"
}
```

### Document Management

#### Upload Document

```http
POST /documents/upload
Content-Type: multipart/form-data

file: <file>
metadata: {
    "title": "Document Title",
    "author": "Author Name",
    "date": "2024-01-01"
}
```

Response:
```json
{
    "document_id": "doc_123",
    "status": "success",
    "message": "Document uploaded successfully"
}
```

#### List Documents

```http
GET /documents
Query Parameters:
- page: int (default: 1)
- limit: int (default: 10)
- sort_by: string (default: "created_at")
- order: string (default: "desc")
```

Response:
```json
{
    "documents": [
        {
            "id": "doc_123",
            "title": "Document Title",
            "author": "Author Name",
            "created_at": "2024-01-01T00:00:00Z",
            "status": "processed"
        }
    ],
    "total": 100,
    "page": 1,
    "limit": 10
}
```

#### Delete Document

```http
DELETE /documents/{document_id}
```

Response:
```json
{
    "status": "success",
    "message": "Document deleted successfully"
}
```

### Query Processing

#### Submit Query

```http
POST /query
Content-Type: application/json

{
    "text": "Your question here",
    "conversation_id": "optional_conversation_id",
    "options": {
        "max_tokens": 1000,
        "temperature": 0.7
    }
}
```

Response:
```json
{
    "response": "Answer to your question",
    "sources": [
        {
            "document_id": "doc_123",
            "title": "Source Document",
            "relevance_score": 0.95
        }
    ],
    "conversation_id": "conv_123"
}
```

#### Get Conversation History

```http
GET /conversations/{conversation_id}
```

Response:
```json
{
    "conversation_id": "conv_123",
    "messages": [
        {
            "role": "user",
            "content": "Question",
            "timestamp": "2024-01-01T00:00:00Z"
        },
        {
            "role": "assistant",
            "content": "Answer",
            "timestamp": "2024-01-01T00:00:01Z"
        }
    ]
}
```

### Vector Store Management

#### Get Statistics

```http
GET /vector-store/stats
```

Response:
```json
{
    "total_documents": 1000,
    "total_vectors": 5000,
    "collection_size": "1.2GB",
    "last_updated": "2024-01-01T00:00:00Z"
}
```

#### Export Metadata

```http
GET /vector-store/export-metadata
Query Parameters:
- format: string (default: "json")
```

Response:
```json
{
    "metadata": [
        {
            "document_id": "doc_123",
            "title": "Document Title",
            "vector_count": 50,
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

## Error Handling

### Error Response Format

```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Error description",
        "details": {
            "field": "Additional error details"
        }
    }
}
```

### Common Error Codes

- `AUTH_ERROR`: Authentication failed
- `INVALID_REQUEST`: Invalid request parameters
- `DOCUMENT_NOT_FOUND`: Document not found
- `PROCESSING_ERROR`: Document processing failed
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `SERVER_ERROR`: Internal server error

## Rate Limiting

- Standard tier: 100 requests per minute
- Premium tier: 1000 requests per minute

Rate limit headers:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1704067200
```

## WebSocket API

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

### Events

1. **Document Processing Status**
```json
{
    "event": "document_status",
    "data": {
        "document_id": "doc_123",
        "status": "processing",
        "progress": 75
    }
}
```

2. **Query Response**
```json
{
    "event": "query_response",
    "data": {
        "response": "Answer",
        "sources": [...]
    }
}
```

## SDK Examples

### Python

```python
from horizon_mda import Client

client = Client(api_key="your_api_key")

# Upload document
result = client.upload_document("path/to/document.pdf")

# Submit query
response = client.query("What is the main topic?")
```

### JavaScript

```javascript
import { HorizonMDA } from '@horizon-mda/client';

const client = new HorizonMDA({
    apiKey: 'your_api_key'
});

// Upload document
const result = await client.uploadDocument(file);

// Submit query
const response = await client.query('What is the main topic?');
```

## Best Practices

1. **Error Handling**
   - Always check for error responses
   - Implement retry logic for transient errors
   - Handle rate limiting appropriately

2. **Performance**
   - Use connection pooling
   - Implement caching where appropriate
   - Batch requests when possible

3. **Security**
   - Keep API keys secure
   - Use HTTPS in production
   - Implement proper error handling

## Support

For API support:
1. Check the [Troubleshooting Guide](Troubleshooting)
2. Open an issue on GitHub
3. Contact the API support team 