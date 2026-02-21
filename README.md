# FastAPI SQLite Template

A production-ready FastAPI project template with SQLite database.

## Project Structure

```
Backend/
├── main.py                 # Main application file with all connections
├── database.py            # Database connection and session management
├── models.py              # SQLAlchemy ORM models (database schemas)
├── schemas.py             # Pydantic schemas (request/response validation)
├── routers/               # API route handlers
│   ├── __init__.py
│   ├── users.py          # User endpoints
│   └── items.py          # Item endpoints
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── .gitignore            # Git ignore file
└── README.md             # This file
```

## Features

- ✅ FastAPI framework with async support
- ✅ SQLite database with SQLAlchemy ORM
- ✅ Pydantic v2 for data validation
- ✅ Modular router structure
- ✅ CORS middleware configured
- ✅ Automatic API documentation (Swagger UI & ReDoc)
- ✅ Database initialization on startup
- ✅ Example CRUD operations for Users and Items
- ✅ Environment variable support

## Setup Instructions

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 2. Run the Application

```powershell
python main.py
```

Or using uvicorn directly:

```powershell
uvicorn main:app --reload
```

### 3. Access the API

- **Application**: http://localhost:8000
- **Swagger UI Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## API Endpoints

### Root Endpoints
- `GET /` - Welcome message
- `GET /health` - Health check

### User Endpoints
- `POST /api/users/` - Create a new user
- `GET /api/users/` - Get all users (with pagination)
- `GET /api/users/{user_id}` - Get a specific user
- `PUT /api/users/{user_id}` - Update a user
- `DELETE /api/users/{user_id}` - Delete a user

### Item Endpoints
- `POST /api/items/` - Create a new item
- `GET /api/items/` - Get all items (with pagination)
- `GET /api/items/{item_id}` - Get a specific item
- `PUT /api/items/{item_id}` - Update an item
- `DELETE /api/items/{item_id}` - Delete an item

## Example Usage

### Create a User

```bash
curl -X POST "http://localhost:8000/api/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "secretpassword"
  }'
```

### Get All Users

```bash
curl "http://localhost:8000/api/users/"
```

### Create an Item

```bash
curl -X POST "http://localhost:8000/api/items/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Item",
    "description": "This is a test item",
    "is_published": true
  }'
```

## Customization

### Adding New Models

1. Add your model in `models.py`:
```python
class YourModel(Base):
    __tablename__ = "your_table"
    id = Column(Integer, primary_key=True, index=True)
    # Add your fields...
```

2. Add schemas in `schemas.py`:
```python
class YourModelCreate(BaseModel):
    # Add your fields...
    pass

class YourModelResponse(BaseModel):
    id: int
    # Add your fields...
    model_config = ConfigDict(from_attributes=True)
```

3. Create a router in `routers/your_model.py`

4. Include the router in `main.py`:
```python
from routers import your_model
app.include_router(your_model.router, prefix="/api")
```

## Environment Variables

Edit `.env` file to configure:

```
DATABASE_URL=sqlite:///./app.db
APP_NAME=FastAPI Application
DEBUG=True
```

## Notes

- The SQLite database file (`app.db`) will be created automatically on first run
- Password hashing is not implemented in this template - add bcrypt/passlib for production
- CORS is set to allow all origins - restrict this in production
- Remember to add proper authentication/authorization for production use

## Development

To add more dependencies:

```powershell
pip install package-name
pip freeze > requirements.txt
```

## License

MIT License - feel free to use this template for your projects!

