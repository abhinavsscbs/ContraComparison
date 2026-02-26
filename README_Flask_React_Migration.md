# Flask + React Migration (Cohere-based)

This project now includes a new architecture:

- `backend/`: Flask API for contract comparison, replacement dictionary, and enhanced tax analysis
- `frontend/`: React (Vite) UI for all three workflows
- `Contract_comparison_0407_enhanced.py`: retained as legacy Streamlit implementation

## Cohere replacement
All new AI logic uses Cohere chat API via `backend/cohere_client.py`.
No OpenAI API calls are used in the new backend.

## Backend setup
1. `cd backend`
2. `python -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `cp .env.example .env` and set `COHERE_API_KEY`
5. `python app.py`

Runs at `http://localhost:5000`.

## Frontend setup
1. `cd frontend`
2. `npm install`
3. `npm run dev`

Runs at `http://localhost:5173` and proxies `/api` to Flask.

## Main API endpoints
- `POST /api/comparisons/run` (multipart: `files`, `pairs`, `output_folder`)
- `GET/POST/DELETE /api/dictionary`
- `DELETE /api/dictionary/<key>`
- `POST /api/dictionary/import`
- `GET /api/dictionary/export?format=csv|json`
- `POST /api/tax/analyze` (multipart: `file`)
- `POST /api/tax/export/excel`
- `POST /api/tax/export/json`

## Notes
- The comparison Excel output format is preserved with difference rows and overall summary.
- File extraction supports PDF/DOCX/DOC using cross-platform parsers.
- Tax analysis includes executive summary, detailed analysis, clause extraction, and export outputs.
