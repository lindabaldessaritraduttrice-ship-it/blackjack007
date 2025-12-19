import streamlit as st
import random
import time

st.set_page_config(page_title="Blackjack Rotation", page_icon="🃏")

# --- DATABASE CONDIVISO ---
@st.cache_resource
def get_server_data():
    return {
        # METTI I VOSTRI NOMI QUI SOTTO!
        "nomi": ["Marco", "Linda", "Sara", "Davide"], 
        "fiches": {"Marco": 21, "Linda": 21, "Sara": 21, "Davide": 21},
        "banco_idx": 0,    # Chi fa il banco (inizia il primo della lista)
        "sfidante_idx": 1, # Chi sfida (inizia il secondo)
        "fase": "PUNTATA",
        "carta_s": 0, "carta_b": 0, "puntata": 0,
        "ultimo_risultato": "Inizia la sfida!"
    }

data = get_server_data()

# Identifichiamo chi sono i protagonisti di questo turno
nome_banco = data["nomi"][data["banco_idx"] % len(data["nomi"])]
nome_sfidante = data["nomi"][data["sfidante_idx"] % len(data["nomi"])]

# Se per caso sono la stessa persona, saltiamo lo sfidante avanti
if nome_banco == nome_sfidante:
    data["sfidante_idx"] += 1
    st.rerun()

# --- INTERFACCIA ---
st.title("🎰 Blackjack a Rotazione")

st.sidebar.title("💰 Portafogli")
for n, f in data["fiches"].items():
    st.sidebar.metric(n, f"{f} 🪙")

st.warning(f"👑 **BANCO:** {nome_banco}")
st.info(f"⚔️ **SFIDANTE:** {nome_sfidante}")
st.write(f"📢 {data['ultimo_risultato']}")

# --- FASE 1: LO SFIDANTE PUNTA ---
if data["fase"] == "PUNTATA":
    st.subheader(f"{nome_sfidante}, fai la tua mossa!")
    c1, c2, c3 = st.columns(3)
    p = 0
    if c1.button("Punta 1 🪙"): p = 1
    if c2.button("Punta 2 🪙"): p = 2
    if c3.button("Punta 3 🪙"): p = 3
    
    if p > 0:
        data["puntata"] = p
        data["carta_s"] = random.randint(2, 11)
        data["fase"] = "BANCO"
        data["ultimo_risultato"] = f"{nome_sfidante} punta {p} e gira un {data['carta_s']}!"
        st.rerun()

# --- FASE 2: IL BANCO RISPONDE ---
elif data["fase"] == "BANCO":
    st.write(f"🃏 {nome_sfidante} ha un **{data['carta_s']}**")
    if st.button(f"
