# Mobile Phone Shopping Assistant - Backend

AI-powered conversational agent for phone shopping built with FastAPI and Hugging Face.

## Setup

### Prerequisites
- Python 3.11+
- pip or conda

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your Hugging Face token (optional for basic functionality)
```

4. Seed the database:
```bash
python scripts/seed_database.py
```

5. Run the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Key Endpoints

### Chat
- `POST /api/v1/chat/message` - Send a chat message
- `GET /api/v1/chat/history/{session_id}` - Get conversation history
- `POST /api/v1/chat/session` - Create new session

### Products
- `GET /api/v1/products` - List all products
- `GET /api/v1/products/{id}` - Get product details
- `POST /api/v1/products/search` - Search products
- `POST /api/v1/products/compare` - Compare phones
- `GET /api/v1/products/category/flagship` - Flagship phones
- `GET /api/v1/products/category/budget` - Budget phones
- `GET /api/v1/products/category/gaming` - Gaming phones
- `GET /api/v1/products/category/camera` - Camera phones

## Testing

Run tests:
```bash
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_safety.py -v
```

## Project Structure

```
backend/
├── app/
│   ├── api/routes/      # API endpoints
│   ├── core/            # AI agent components
│   ├── models/          # Database & Pydantic models
│   ├── repositories/    # Data access layer
│   ├── services/        # External services
│   ├── utils/           # Utilities
│   └── data/            # Phone dataset
├── tests/               # Test suite
└── scripts/             # Utility scripts
```

## Features

- Natural language phone search
- Intent classification
- Adversarial input detection
- Phone comparison
- Feature explanations
- Conversation history
