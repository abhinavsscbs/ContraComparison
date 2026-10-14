# ContraComparison

Contract comparison and tax analysis application with a Flask API, React/Vite UI, and Cohere-based AI services.

## Workflows

- Compare contract documents and export differences and summaries to Excel.
- Maintain, import, and export a replacement dictionary.
- Analyze tax-related clauses and export analysis as Excel or JSON.

## Layout

| Path | Purpose |
| --- | --- |
| `backend/app.py` | Flask API |
| `backend/services/` | Comparison, dictionary, document, and tax services |
| `backend/cohere_client.py` | Cohere integration |
| `frontend/` | React/Vite interface |
| `Input/` | Example contract documents |
| `output/` | Example comparison spreadsheets |

## Backend setup

```bash
git clone https://github.com/abhinavsscbs/ContraComparison.git
cd ContraComparison
cd backend
python -m venv .venv
# Activate .venv before continuing.
python -m pip install -r requirements.txt
```

Copy `backend/.env.example` to `backend/.env` and configure the required Cohere settings, including `COHERE_API_KEY`.

```bash
python app.py
```

The documented backend URL is `http://localhost:5000`.

In a separate terminal, start the React UI:

```bash
cd frontend
npm install
npm run dev
```

Create a production UI build with `npm run build`.

The migration documentation specifies a frontend at `http://localhost:5173` with API proxying to Flask.

## Further documentation

See [Flask/React migration notes](README_Flask_React_Migration.md) for endpoint details. Those notes mention a legacy Streamlit file that is not present in the current repository tree.
