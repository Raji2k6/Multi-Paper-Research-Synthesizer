# PaperFusion AI

A standalone, local-first RAG application for uploading research PDFs, asking
evidence-grounded questions, and comparing evidence across papers.

## Requirements

- Python 3.10+
- Node.js 20.19+ or 22.12+

## Run locally

1. In `backend`, create and activate a virtual environment, then install the
   backend dependencies:

   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   Copy-Item .env.example .env
   ```

   A private JWT signing key is generated and stored in the ignored
   `backend/.jwt_secret` file the first time an account is created. To manage
   the key yourself, set `JWT_SECRET_KEY` in `backend/.env`:

   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

   Keep the key private and do not regenerate or delete it between restarts;
   doing so invalidates existing login tokens.

2. Start the API from the `backend` directory:

   ```powershell
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

   On first start, the API creates a local SQLite database (`research.db`) and
   its tables. PDF files and their indexed chunks are stored locally. The
   default SQLite embedding backend uses a deterministic local vectorizer and
   does not require a model download or hosted database.

3. In another terminal, start the frontend:

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

   Open the local Vite URL (normally `http://localhost:5173`). The API
   documentation is available at `http://127.0.0.1:8000/docs`.

## Optional hosted generation

With `LLM_BACKEND=local`, chat returns the retrieved excerpts with their
paper/page citations, and synthesis returns the evidence without claiming to
infer comparisons. `LLM_BACKEND=auto` (the default) enables hosted generation
when `OPENROUTER_API_KEY` is configured; set `LLM_BACKEND=openrouter` to
require it explicitly. The chat and synthesis model names can be changed with
`OPENROUTER_MODEL` and `OPENROUTER_SYNTHESIS_MODEL`.

## Configuration

Backend settings are read from environment variables or `backend/.env`:

- `DATABASE_URL`: defaults to `sqlite:///./research.db`. PostgreSQL with
  pgvector remains supported for existing deployments.
- `EMBEDDING_BACKEND`: `auto` selects local feature hashing for SQLite and
  Sentence Transformers for PostgreSQL; `hashing` and
  `sentence-transformers` can be selected explicitly. Re-embed documents if
  changing the embedding backend for an existing collection.
- `MAX_UPLOAD_SIZE_MB`, `RETRIEVAL_TOP_K`, `SYNTHESIS_CHUNKS_PER_DOCUMENT`,
  `SYNTHESIS_CANDIDATE_K`, and `SYNTHESIS_MAX_DISTANCE` control ingestion and
  retrieval limits.
- `CORS_ORIGINS`: comma-separated frontend origins.
- `VITE_API_BASE_URL`: optional frontend API URL; defaults to
  `http://127.0.0.1:8000`.

Create an account or sign in with an email and password. Passwords are stored
as salted PBKDF2-HMAC-SHA256 hashes; the API uses expiring HS256 JWTs. Documents,
chat history, and synthesis history are scoped to the authenticated account and
persist in the backend database across logins. Existing data from earlier,
unauthenticated versions is not automatically assigned to a new account.
