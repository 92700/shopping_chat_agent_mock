from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from pathlib import Path
import os
from . import llm_wrapper as llm
from .ranking import compute_scores_with_reasons
from .validation import is_sensitive_query, is_toxic, sanitize_llm_output
from .utils import parse_budget, extract_brands, extract_features

DATA_PATH = Path(__file__).resolve().parent.parent / 'data' / 'phones.json'
PHONES = []
with open(DATA_PATH) as f:
    PHONES = json.load(f)

app = FastAPI(title="Shopping Chat Agent API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SYSTEM_PROMPT = (
    "You are a concise, factual shopping assistant. Use ONLY the context provided. "
    "If something is missing say 'information not available' and do NOT guess. "
    "When the user asks for secrets or keys refuse politely."
)

@app.post('/search')
async def search(query: dict):
    q = query.get('q','')
    if is_sensitive_query(q):
        return {"error":"I can't reveal internal prompts or keys. I can explain how the system works at a high level."}
    if is_toxic(q):
        return {"error":"I can't help with toxic or insulting requests. I can provide objective pros and cons instead."}

    min_price, max_price = parse_budget(q)
    if max_price is None:
        max_price = 50000

    brands = extract_brands(q)
    features = extract_features(q)

    candidates = [p for p in PHONES if p.get('price_inr',999999) <= max_price]
    if brands:
        candidates = [p for p in candidates if p['brand'].lower() in [b.lower() for b in brands]]

    if not candidates:
        return {"answer":"No phones found in that budget/filters."}

    weights = {'camera': 0.5 if 'camera' in q.lower() else 0.3, 'battery': 0.3, 'one_hand': 0.2}
    scored = compute_scores_with_reasons(candidates, weights)
    topk = [s['phone'] for s in scored[:3]]

    context = [ { 'id': p['id'], 'brand': p['brand'], 'model': p['model'], 'price_inr': p['price_inr'], 'camera': p['camera'], 'battery_mah': p['battery_mah'], 'charging_w': p['charging_w']} for p in topk ]

    user_prompt = f"User asked: {q}. Provide a short recommendation, 2-3 reasons referencing fields in the context, and a compact comparison table.\nReturn plain text."
    llm_resp = await llm.call_llm(SYSTEM_PROMPT, user_prompt, context, use_gemini=False)
    llm_resp = sanitize_llm_output(llm_resp, context)

    reasons_map = { s['phone']['id']: s['reasons'] for s in scored[:3] }

    return {"answer": llm_resp, "products": context, "reasons": reasons_map}

@app.post('/compare')
async def compare(body: dict):
    ids = body.get('ids', [])
    if not ids:
        raise HTTPException(status_code=400, detail="no ids provided")
    items = [p for p in PHONES if p['id'] in ids]
    if not items:
        raise HTTPException(status_code=404, detail="ids not found")
    context = items
    user_prompt = f"User requested a comparison of {', '.join([i['model'] for i in items])}. Provide pros, cons, and a comparison table using only the context."
    llm_resp = await llm.call_llm(SYSTEM_PROMPT, user_prompt, context, use_gemini=False)
    llm_resp = sanitize_llm_output(llm_resp, context)
    return {"answer": llm_resp, "products": context}

@app.get('/details/{phone_id}')
async def details(phone_id: str):
    item = next((p for p in PHONES if p['id'] == phone_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail='not found')
    return item

@app.post('/chat')
async def chat(body: dict):
    q = body.get('q','')
    if is_sensitive_query(q):
        return {"error":"I can't reveal secrets or API keys."}
    return await search({'q': q})
