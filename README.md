# AI Mobile Phone Shopping Assistant

An intelligent conversational AI agent that helps customers discover, compare, and purchase mobile phones through natural language interactions.

## Features

- **Natural Language Chat**: Ask questions like "Best camera phone under 30k" or "Compare Samsung S24 vs OnePlus 12"
- **Smart Recommendations**: AI-powered phone suggestions based on your requirements
- **Phone Comparison**: Side-by-side comparison of multiple phones
- **Feature Explanations**: Learn about AMOLED, OIS, refresh rates, and more
- **Adversarial Detection**: Robust protection against prompt injection attacks
- **Dark/Light Mode**: Beautiful UI with theme support

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/seed_database.py
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
mykarmaa/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # REST API endpoints
│   │   ├── core/           # AI agent components
│   │   │   ├── agent.py           # Main shopping agent
│   │   │   ├── intent_classifier.py
│   │   │   ├── query_processor.py
│   │   │   ├── response_generator.py
│   │   │   └── safety_filter.py   # Adversarial detection
│   │   ├── models/         # Database & Pydantic schemas
│   │   ├── repositories/   # Data access layer
│   │   ├── services/       # HuggingFace & embedding services
│   │   └── data/           # Phone dataset (25 phones)
│   └── tests/              # Test suite
│
├── frontend/               # React TypeScript frontend
│   └── src/
│       ├── components/     # UI components
│       │   ├── chat/       # Chat interface
│       │   ├── products/   # Phone cards & comparison
│       │   └── ui/         # Reusable components
│       ├── hooks/          # Custom hooks
│       ├── services/       # API client
│       └── store/          # Zustand state management
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat/message` | Send chat message |
| GET | `/api/v1/chat/history/{session_id}` | Get chat history |
| GET | `/api/v1/products` | List all phones |
| GET | `/api/v1/products/{id}` | Get phone details |
| POST | `/api/v1/products/search` | Search phones |
| POST | `/api/v1/products/compare` | Compare phones |
| GET | `/api/v1/health` | Health check |

## Sample Queries

```
"Best phones under Rs 30,000"
"Compare Samsung S24 Ultra vs OnePlus 12"
"Gaming phones with 120Hz display"
"What is AMOLED display?"
"Show me Xiaomi phones"
"Phones with best camera for low light"
"Compact Android with good one-hand use"
"Battery king with fast charging around 15k"
```

## Technology Stack

### Backend
- Python 3.11+
- FastAPI
- Hugging Face Transformers
- SQLAlchemy (async)
- Sentence Transformers

### Frontend
- React 18
- TypeScript
- Vite
- Tailwind CSS
- TanStack Query
- Zustand

## Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Specific tests
pytest tests/test_safety.py -v      # Adversarial detection
pytest tests/test_intent.py -v      # Intent classification
pytest tests/test_api.py -v         # API endpoints
```

## Configuration

Create `.env` in backend directory:

# Hugging Face Configuration
HF_TOKEN=your_hf_token #add your token here
HF_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.2
USE_INFERENCE_API=true

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Database
DATABASE_URL=sqlite+aiosqlite:///./phones.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Rate Limiting
RATE_LIMIT_PER_MINUTE=30
```

## Phone Database

Includes 25 phones covering:
- **Brands**: Samsung, OnePlus, Google, Xiaomi, Realme, Vivo, Oppo, Nothing, iQOO, Poco, Motorola
- **Price Range**: Rs 17,999 - Rs 129,999
- **Categories**: Budget, Mid-range, Flagship, Gaming, Camera-focused

## Adversarial Protection

The system detects and safely handles:
- Prompt injection attempts
- Jailbreaking attempts
- System information extraction
- Off-topic queries

## License

MIT License
