# AI Paper Digest

An intelligent, evolving research atlas that helps teams navigate the entire AI landscape—from discovering the latest work to understanding technique lineages and implementing state-of-the-art solutions. The platform combines automated analysis, knowledge-graph reasoning, and visual exploration so researchers can see where the frontier is moving and ship production-ready code faster.

## Vision

> **Help AI researchers go from idea → production code in hours, not months, by mapping the research universe, highlighting the frontier, and auto-generating implementation playbooks.**

The platform is being built around four complementary pillars:

1. **Living Research Graph** – A dense, constantly-updated graph linking papers, techniques, datasets, benchmarks, institutions, and authors. Semantic search, citation lineages, and concept ontologies expose connections that keyword search misses.
2. **Deep Paper Intelligence** – Gemini-powered analysis plus PDF table parsing extract techniques, metrics, code availability, novelty, and implementation insights. Benchmark deltas, performance trends, and reproducibility signals surface automatically.
3. **Exploratory Atlas UI** – Interactive maps, timelines, and benchmark leaderboards let you see where topics are heating up, which approaches dominate, and how methods evolve over time. Contextual search and guided flows help you plan projects from vague goals.
4. **Implementation Acceleration** – Multi-agent code generation turns paper insights into runnable projects with tests and debugging loops, enabling engineers to go from literature review to prototype with minimal hand-holding.

## Current Capabilities

- **📚 Smart Paper Discovery** – Browse recent AI/ML papers with intelligent filtering and semantic augmentation.
- **🤖 AI-Powered Analysis** – Comprehensive summaries covering novelty, methodology, performance, context, limitations, applicability, and code availability.
- **🔍 Contextual Search** – Describe your project and receive tailored paper recommendations with actionable guidance.
- **💻 Code Detection** – Identify official and community implementations, ranked by a quality heuristic.
- **📊 Insightful Badges** – Impact, difficulty, reading time, significance, and practicality at a glance.
- **⚡ Async Processing Stack** – FastAPI + background tasks deliver concurrent analysis and caching with Redis or in-memory fallback.
- **🗂️ Local Atlas Bootstrap** – Seed the research atlas by downloading the last N years of arXiv papers to NDJSON files (`--dump-dir`) and build derived JSON datasets for the prototype UI (`python -m app.cli.build_atlas_dataset`).

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
# Optional: used by the Next.js proxy to reach FastAPI
RESEARCH_API_BASE_URL=http://localhost:8000

# (legacy) expose backend URL directly to the browser if needed
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

### Precomputing Embeddings

Use the embedding CLI to cache vectors so the backend can load them instantly:

```bash
cd backend
source ../venv-py311/bin/activate
python -m app.cli.generate_embeddings \
  --catalog ../data/derived_12mo/papers_catalog.ndjson \
  --output ../embeddings \
  --model specter2
```

Additional baselines:

- **Voyage AI** (commercial). Set `VOYAGE_API_KEY` (or pass `--voyage-api-key`) and run:
  ```bash
  python -m app.cli.generate_embeddings \
    --model voyage --voyage-model voyage-3.5 \
    --batch-size 16 --voyage-sleep 1.0 --voyage-dimension 1024
  ```
  The CLI uses the official `voyageai` SDK (see `backend/requirements.txt`) so it will automatically retry on transient errors. Adjust `--voyage-sleep` and `--batch-size` if you hit rate limits.
- **Qwen3 (self-hosted)**. Deploy HuggingFace Text-Embeddings-Inference for `Qwen/Qwen3-Embedding-8B`, expose its `/v1/embeddings` URL, then run:
  ```bash
  python -m app.cli.generate_embeddings ... --model qwen \
    --qwen-endpoint https://<your-tei-host>/v1/embeddings
  ```
  Provide `--qwen-api-key` if your TEI endpoint requires auth.

Each run writes `<label>_embeddings.npy` + `<label>_ids.json` into `embeddings/`. Set `ATLAS_EMBED_CACHE_LABEL` in `backend/.env` to the label you want (e.g., `specter2`, `voyage_voyage-3_5`, `qwen_Qwen3-Embedding-8B`) and restart FastAPI to switch models.

### Multimodal (PDF Page) Pipeline

1. **Download PDFs from arXiv** (optional limit for testing):
   ```bash
   cd backend
   python -m app.cli.download_pdfs \
     --catalog ../data/derived_12mo/papers_catalog.ndjson \
     --output-root ../data/papers_pdf \
     --rate-limit 0.5
   ```
   Adjust `--rate-limit` to stay polite with arXiv; use `--limit` to download a subset.
2. **Render PDFs to images** (expects PDFs under `data/papers_pdf/`):
   ```bash
   cd backend
   python -m app.cli.render_pdf_pages \
     --catalog ../data/derived_12mo/papers_catalog.ndjson \
     --pdf-root ../data/papers_pdf \
     --output-root ../data/rendered_pages \
     --dpi 144
   ```
   This writes PNGs per page plus `render_manifest.jsonl`.
3. **Generate multimodal embeddings (Nomic single-vector)**:
   ```bash
   python -m app.cli.embed_pages_nomic \
     --images-root ../data/rendered_pages \
     --output ../embeddings \
     --model-id nomic-ai/nomic-embed-multimodal-v1.5 \
     --device cuda \
     --batch-size 8
   ```
   Requires a GPU with sufficient VRAM. The script emits `nomic_multimodal_embeddings.npy` and `_ids.json`.
4. **Fuse search results**: load the multimodal cache in a parallel index (work in progress) and blend with the text embeddings via reciprocal-rank fusion / reranking. This enables figure/equation retrieval without relying solely on OCR.

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
