# Shopping Chat Agent — Python (FastAPI + Streamlit)

This project implements an AI shopping chat agent for mobile phones using:
- FastAPI backend (backend/)
- Streamlit frontend (frontend/)
- Mock dataset data/phones.json (120 entries)
- OpenAI GPT (set OPENAI_API_KEY) for LLM responses

Quickstart:
1. Create virtualenv: python -m venv venv && source venv/bin/activate
2. Install backend dependencies: pip install -r backend/requirements.txt
3. (Optional) generate dataset: python phones_generator.py
4. Run backend: uvicorn backend.app:app --reload --port 8000
5. Run frontend: streamlit run frontend/streamlit_app.py

Environment variables:
- OPENAI_API_KEY: your OpenAI API key
- OPENAI_MODEL: optional (defaults to gpt-4o-mini)

Notes:
- Do NOT commit API keys to the repo. Use environment variables.
