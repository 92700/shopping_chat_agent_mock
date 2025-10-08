# frontend/streamlit_app.py
import streamlit as st
import json
import re

st.set_page_config(page_title='Shopping Chat Agent', layout='wide')
st.title('📱 Mobile Shopping Assistant')

# Session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'compare_set' not in st.session_state:
    st.session_state.compare_set = set()

# Load phones data
try:
    with open('phones.json', 'r', encoding='utf-8') as f:
        phones = json.load(f)
except Exception:
    phones = []

# Mock LLM function
def get_mock_answer(query, phones_data):
    # Extract budget from query
    budget = 30000
    m = re.search(r'under ₹?(\d+)', query.replace(',', ''))
    if m:
        budget = int(m.group(1))

    # Filter top 3 phones under budget
    candidates = [p for p in phones_data if p['price_inr'] <= budget][:3]

    # Generate simple reasons
    reasons = {}
    for p in candidates:
        r = []
        cam = p.get('camera', {}).get('main_mp', 0)
        if cam >= 48:
            r.append(f"Good camera ({cam}MP)")
        bat = p.get('battery_mah', 0)
        if bat >= 4000:
            r.append(f"Decent battery ({bat} mAh)")
        if p.get('one_hand_score', 6) >= 7:
            r.append("Good one-hand usability")
        reasons[p['id']] = r

    answer = "Recommended phones: " + ", ".join([p['model'] for p in candidates])
    return {'answer': answer, 'products': candidates, 'reasons': reasons}

# User input form
with st.form('query_form', clear_on_submit=True):
    q = st.text_input('Ask about phones (e.g. Best camera phone under ₹30k)')
    submitted = st.form_submit_button('Ask')

if submitted and q:
    st.session_state.history.append({'role': 'user', 'text': q})
    with st.spinner('Searching...'):
        r = get_mock_answer(q, phones)

    st.session_state.history.append({'role': 'assistant', 'text': r.get('answer', '')})
    products = r.get('products', [])
    reasons = r.get('reasons', {})

    # Display product cards
    cols = st.columns(3)
    for i, p in enumerate(products):
        with cols[i % 3]:
            st.image(p.get('image', 'https://via.placeholder.com/300x200.png?text=Phone+Image'))
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

# Separator
st.markdown('---')

# Compare section
if st.session_state.compare_set:
    ids = list(st.session_state.compare_set)
    st.subheader('Compare selected phones')
    if len(ids) > 3:
        st.warning('Compare supports up to 3 phones — remove some to proceed.')
    else:
        if st.button('Compare now'):
            selected = [p for p in phones if p['id'] in ids]
            for p in selected:
                st.markdown(f"**{p['brand']} {p['model']}**")
                st.markdown(f"Price: ₹{p['price_inr']}")
                cam = p.get('camera', {})
                st.markdown(f"Camera: {cam.get('main_mp','N/A')} MP | Features: {', '.join(cam.get('features',[]))}")
                st.markdown(f"Battery: {p.get('battery_mah','N/A')} mAh | Charging: {p.get('charging_w','N/A')}W")
                st.markdown('---')

# Display chat history
for m in st.session_state.history[::-1]:
    if m['role'] == 'assistant':
        st.markdown(f"**Agent:** {m['text']}")
    else:
        st.markdown(f"**You:** {m['text']}")

    
