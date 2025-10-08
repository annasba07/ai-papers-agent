# AI Paper Digest

An intelligent research paper analysis platform that helps researchers discover, understand, and apply cutting-edge AI research from arXiv. Powered by Google's Gemini AI for comprehensive paper analysis and contextual recommendations.

## Features

- **📚 Smart Paper Discovery**: Browse recent AI/ML papers from arXiv with intelligent filtering
- **🤖 AI-Powered Analysis**: Comprehensive paper summaries with:
  - Key contributions and novelty assessment
  - Technical methodology breakdown
  - Performance highlights and implementation insights
  - Research context and future implications
  - Practical applicability scores
- **🔍 Contextual Search**: Describe your project and get tailored paper recommendations with implementation guidance
- **📊 Smart Badges**: Quick visual indicators for impact score, difficulty level, reading time, and more
- **⚡ Real-time Processing**: Async backend for fast, concurrent paper analysis

## Tech Stack

### Frontend
- **Next.js 15** with React 19
- **TypeScript** for type safety
- **React Bootstrap** for UI components
- Server-side rendering and optimized performance

### Backend
- **FastAPI** for high-performance async API
- **Google Gemini AI** (gemini-1.5-flash) for paper analysis
- **arXiv API** for paper fetching
- **Pydantic** for data validation
- **SQLite** for local development (production-ready architecture)

## Getting Started

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Google Gemini API Key** ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-papers-agent
   ```

2. **Setup Backend**
   ```bash
   cd backend

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Configure environment
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

3. **Setup Frontend**
   ```bash
   cd ..  # Back to root directory
   npm install
   ```

### Running the Application

1. **Start the Backend**
   ```bash
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the Frontend** (in a new terminal)
   ```bash
   npm run dev
   ```

3. **Open your browser**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## API Endpoints

### Core Endpoints

- `GET /papers` - Get recent papers with AI analysis
  - Query params: `days`, `category`, `query`
- `POST /papers/contextual-search` - Get personalized paper recommendations
- `GET /api/v1/papers/search` - Search papers by query
- `GET /api/v1/papers/recent` - Get recent papers by category
- `POST /api/v1/papers/analyze` - Analyze a single paper
- `POST /api/v1/papers/batch-analyze` - Batch analyze multiple papers

### Health & Status

- `GET /health` - Health check endpoint
- `GET /` - API information

## Configuration

### Environment Variables

Backend (`backend/.env`):

```bash
# Required
GEMINI_API_KEY=your_api_key_here

# Optional (with defaults)
API_V1_STR=/api/v1
PROJECT_NAME=AI Paper Digest
GEMINI_MODEL=gemini-1.5-flash
MAX_PAPERS_PER_BATCH=20
ARXIV_MAX_RESULTS=10
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

Frontend (`.env.local`):

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Docker Deployment

```bash
cd backend
docker build -t ai-paper-digest .
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key ai-paper-digest
```

## Project Structure

```
ai-papers-agent/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # API route handlers
│   │   ├── core/                # Config and settings
│   │   ├── models/              # Data models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   │   ├── arxiv_service.py
│   │   │   ├── ai_analysis_service.py
│   │   │   └── cache_service.py
│   │   └── utils/               # Utilities
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── src/
│   ├── app/                     # Next.js app directory
│   ├── components/              # React components
│   │   ├── ContextualSearch.tsx
│   │   ├── PaperList.tsx
│   │   ├── PaperDetailModal.tsx
│   │   └── SmartBadges.tsx
│   └── types/                   # TypeScript types
├── public/                      # Static assets
├── package.json
└── README.md
```

## Key Features Explained

### AI Analysis Pipeline

1. **Technical Analysis**: Extracts key innovations, methodology, and performance metrics
2. **Research Context**: Evaluates field significance and future implications
3. **Practical Assessment**: Rates implementation complexity and applicability
4. **Basic Summary**: Generates concise overview and novelty assessment

All stages run in parallel for optimal performance with smart fallback handling.

### Contextual Search

1. User describes their project/problem
2. AI extracts key technical requirements
3. System searches arXiv for relevant papers
4. AI synthesizes findings into actionable recommendations
5. Returns ranked papers with implementation guidance

## Development

### Adding New Features

1. Backend endpoints: `backend/app/api/v1/endpoints/`
2. Frontend components: `src/components/`
3. API types: `src/types/`

### Running Tests

```bash
# Backend tests (when implemented)
cd backend
pytest

# Frontend tests (when implemented)
npm test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Your License Here]

## Acknowledgments

- [arXiv](https://arxiv.org/) for providing access to research papers
- [Google Gemini](https://ai.google.dev/) for AI analysis capabilities
- [Next.js](https://nextjs.org/) and [FastAPI](https://fastapi.tiangolo.com/) for excellent frameworks

## Support

For issues, questions, or contributions, please open an issue on GitHub.
