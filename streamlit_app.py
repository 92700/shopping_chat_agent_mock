import streamlit as st
import requests, os, json
st.set_page_config(page_title='Shopping Chat Agent', layout='wide')
API_BASE = os.getenv('API_BASE','http://localhost:8000')

st.title('📱 Mobile Shopping Assistant')
if 'history' not in st.session_state:
    st.session_state.history = []
if 'compare_set' not in st.session_state:
    st.session_state.compare_set = set()

# load local data for demo (falls back to calling backend)
try:
    with open('data/phones.json') as f:
        phones = json.load(f)
except Exception:
    phones = []

with st.form('query_form', clear_on_submit=True):
    q = st.text_input('Ask about phones (e.g. Best camera phone under ₹30k)')
    submitted = st.form_submit_button('Ask')

if submitted and q:
    st.session_state.history.append({'role':'user','text':q})
    with st.spinner('Searching...'):
        try:
            r = requests.post(f"{API_BASE}/search", json={'q': q}, timeout=30).json()
        except Exception:
            # fallback to local filtering
            r = {'answer': 'Local results', 'products': [p for p in phones if p['price_inr'] <= 30000][:3], 'reasons': {}}
    if r.get('error'):
        st.error(r['error'])
    else:
        st.session_state.history.append({'role':'assistant','text': r.get('answer','')})
        products = r.get('products', [])
        reasons = r.get('reasons', {})
        cols = st.columns(3)
        for i, p in enumerate(products):
            with cols[i%3]:
                st.image(p.get('image','https://via.placeholder.com/300x200.png?text=Phone+Image'))
                st.markdown(f"**{p['brand']} {p['model']}**")
                st.markdown(f"Price: ₹{p['price_inr']}")
                cam = p.get('camera',{})
                st.markdown(f"Camera: {cam.get('main_mp','N/A')} MP | Features: {', '.join(cam.get('features',[]))}")
                st.markdown(f"Battery: {p.get('battery_mah','N/A')} mAh | Charging: {p.get('charging_w','N/A')}W")
                if st.checkbox('Compare', key=f"cmp_{p['id']}"):
                    st.session_state.compare_set.add(p['id'])
                if st.button('Details', key=f"details_{p['id']}"):
                    try:
                        d = requests.get(f"{API_BASE}/details/{p['id']}").json()
                        st.json(d)
                    except Exception:
                        st.write(p)
                if st.button('Why this?', key=f"why_{p['id']}"):
                    st.write('\n'.join(reasons.get(p['id'], ['No reasons available'])))

st.markdown('---')
if st.session_state.compare_set:
    ids = list(st.session_state.compare_set)
    st.subheader('Compare selected phones')
    if len(ids) > 3:
        st.warning('Compare supports up to 3 phones — remove some to proceed.')
    else:
        if st.button('Compare now'):
            try:
                r = requests.post(f"{API_BASE}/compare", json={'ids': ids}).json()
                st.write(r.get('answer'))
            except Exception:
                st.write('Compare unavailable (backend not running).')
for m in st.session_state.history[::-1]:
    if m['role']=='assistant':
        st.markdown(f"**Agent:** {m['text']}")
    else:
        st.markdown(f"**You:** {m['text']}")
