import streamlit as st
import json
import re

st.set_page_config(page_title='Mobile Shopping Agent', layout='wide')
st.title("📱 Mobile Shopping Assistant")

# ---------------- Session State ----------------
if 'history' not in st.session_state:
    st.session_state.history = []
if 'compare_set' not in st.session_state:
    st.session_state.compare_set = set()

# ---------------- Load Phones Data ----------------
try:
    with open('phones.json', 'r', encoding='utf-8') as f:
        phones = json.load(f)
except Exception:
    phones = []

# ---------------- Mock Recommendation Function ----------------
def get_mock_answer(query, phones_data):
    query_lower = query.lower()

    # Comparison query: match any model in query
    selected = [p for p in phones_data if p['model'].lower() in query_lower]
    if selected:
        answer = "Comparing phones: " + ", ".join([p['model'] for p in selected])
        reasons = {}
        for p in selected:
            r = []
            cam = p['camera']['main_mp']
            if cam >= 48: r.append(f"Good camera ({cam}MP)")
            if p['battery_mah'] >= 4000: r.append(f"Decent battery ({p['battery_mah']} mAh)")
            if p['one_hand_score'] >= 7: r.append("Good one-hand usability")
            reasons[p['id']] = r
        return {'answer': answer, 'products': selected, 'reasons': reasons}

    # Budget query: show phones under budget
    budget = 30000
    m = re.search(r'under ₹?(\d+)', query.replace(',', ''))
    if m:
        budget = int(m.group(1))
    candidates = [p for p in phones_data if p['price_inr'] <= budget][:3]

    reasons = {}
    for p in candidates:
        r = []
        cam = p['camera']['main_mp']
        if cam >= 48: r.append(f"Good camera ({cam}MP)")
        if p['battery_mah'] >= 4000: r.append(f"Decent battery ({p['battery_mah']} mAh)")
        if p['one_hand_score'] >= 7: r.append("Good one-hand usability")
        reasons[p['id']] = r

    answer = "Recommended phones: " + ", ".join([p['model'] for p in candidates])
    return {'answer': answer, 'products': candidates, 'reasons': reasons}

# ---------------- User Input ----------------
with st.form('query_form', clear_on_submit=True):
    user_query = st.text_input("Ask about phones (e.g. Best camera phone under ₹30k or Compare Pixel 11 Neo vs Moto 11 Lite)")
    submitted = st.form_submit_button('Ask')

if submitted and user_query:
    st.session_state.history.append({'role': 'user', 'text': user_query})
    with st.spinner('Searching...'):
        result = get_mock_answer(user_query, phones)

    st.session_state.history.append({'role': 'assistant', 'text': result.get('answer', '')})
    products = result.get('products', [])
    reasons = result.get('reasons', {})

    # ---------------- Display Product Cards ----------------
    cols = st.columns(3)
    for i, p in enumerate(products):
        with cols[i % 3]:
            st.image(p.get('image'))
            st.markdown(f"**{p['brand']} {p['model']}**")
            st.markdown(f"Price: ₹{p['price_inr']}")
            cam = p.get('camera', {})
            st.markdown(f"Camera: {cam.get('main_mp','N/A')} MP | Features: {', '.join(cam.get('features',[]))}")
            st.markdown(f"Battery: {p.get('battery_mah','N/A')} mAh | Charging: {p.get('charging_w','N/A')}W")

            if st.checkbox('Compare', key=f"cmp_{p['id']}"):
                st.session_state.compare_set.add(p['id'])
            if st.button('Details', key=f"details_{p['id']}"):
                st.json(p)
            if st.button('Why this?', key=f"why_{p['id']}"):
                st.write('\n'.join(reasons.get(p['id'], ['No reasons available'])))

# ---------------- Compare Section ----------------
st.markdown('---')
if st.session_state.compare_set:
    ids = list(st.session_state.compare_set)
    st.subheader('Compare Selected Phones')
    if len(ids) > 3:
        st.warning('Compare supports up to 3 phones — remove some to proceed.')
    else:
        if st.button('Compare Now'):
            selected = [p for p in phones if p['id'] in ids]
            for p in selected:
                st.markdown(f"**{p['brand']} {p['model']}**")
                st.markdown(f"Price: ₹{p['price_inr']}")
                cam = p.get('camera', {})
                st.markdown(f"Camera: {cam.get('main_mp','N/A')} MP | Features: {', '.join(cam.get('features',[]))}")
                st.markdown(f"Battery: {p.get('battery_mah','N/A')} mAh | Charging: {p.get('charging_w','N/A')}W")
                st.markdown('---')

# ---------------- Chat History ----------------
for msg in st.session_state.history[::-1]:
    if msg['role'] == 'assistant':
        st.markdown(f"**Agent:** {msg['text']}")
    else:
        st.markdown(f"**You:** {msg['text']}")
