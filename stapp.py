import streamlit as st
import random
import time

st.set_page_config(page_title="Blackjack Rotation", page_icon="🃏")

# --- DATABASE CONDIVISO ---
@st.cache_resource
def get_server_data():
    # Sostituisci i nomi qui sotto con quelli dei tuoi amici
    lista_nomi = ["Marco", "Linda", "Sara", "Davide"]
    return {
        "nomi": lista_nomi,
        "fiches": {nome: 21 for nome in lista_nomi},
        "banco_idx": 0,    
        "sfidante_idx": 1, 
        "fase": "PUNTATA",
        "carta_s": 0, 
        "carta_b": 0, 
        "puntata": 0,
        "ultimo_risultato": "Inizia la sfida!"
    }

data = get_server_data()

# Identificazione ruoli
nome_banco = data["nomi"][data["banco_idx"] % len(data["nomi"])]
nome_sfidante = data["nomi"][data["sfidante_idx"] % len(data["nomi"])]

# Evitiamo che banco e sfidante siano la stessa persona
if nome_banco == nome_sfidante:
    data["sfidante_idx"] += 1
    st.rerun()

st.title("🎰 Blackjack: Il Banco Gira")

# Sidebar con le fiches
st.sidebar.title("💰 Portafogli")
for n, f in data["fiches"].items():
    st.sidebar.metric(n, f"{f} 🪙")

st.warning(f"👑 BANCO: **{nome_banco}**")
st.info(f"⚔️ SFIDANTE: **{nome_sfidante}**")
st.write(f"📢 {data['ultimo_risultato']}")

# --- FASE 1: PUNTATA ---
if data["fase"] == "PUNTATA":
    st.subheader(f"{nome_sfidante}, quanto punti?")
    c1, c2, c3 = st.columns(3)
    p = 0
    if c1.button("Punta 1 🪙"): p = 1
    if c2.button("Punta 2 🪙"): p = 2
    if c3.button("Punta 3 🪙"): p = 3
    
    if p > 0:
        data["puntata"] = p
        data["carta_s"] = random.randint(2, 11)
        data["fase"] = "BANCO"
        data["ultimo_risultato"] = f"{nome_sfidante} ha puntato {p} e ha un {data['carta_s']}!"
        st.rerun()

# --- FASE 2: BANCO ---
elif data["fase"] == "BANCO":
    st.write(f"🃏 {nome_sfidante} ha girato un **{data['carta_s']}**")
    st.write(f"💰 Puntata in palio: {data['puntata']} fiches")
    
    # Riga corretta senza errori di f-string
    testo_bottone = f"Gira carta di {nome_banco}"
    if st.button(testo_bottone):
        data["carta_b"] = random.randint(2, 11)
        
        if data["carta_s"] > data["carta_b"]:
            data["fiches"][nome_sfidante] += data["puntata"]
            data["fiches"][nome_banco] -= data["puntata"]
            data["ultimo_risultato"] = f"Vince {nome_sfidante}! ({data['carta_s']} vs {data['carta_b']})"
        elif data["carta_s"] < data["carta_b"]:
            data["fiches"][nome_sfidante] -= data["puntata"]
            data["fiches"][nome_banco] += data["puntata"]
            data["ultimo_risultato"] = f"Vince il Banco {nome_banco}! ({data['carta_b']} vs {data['carta_s']})"
        else:
            data["ultimo_risultato"] = "Pareggio! Nessuno perde fiches."
            
        data["fase"] = "RISULTATO"
        st.rerun()

# --- FASE 3: RISULTATO E ROTAZIONE ---
elif data["fase"] == "RISULTATO":
    st.success(data["ultimo_risultato"])
    st.write(f"Carta {nome_sfidante}: **{data['carta_s']}** | Carta {nome_banco}: **{data['carta_b']}**")
    
    if st.button("PROSSIMO TURNO ➡️"):
        # Rotazione: lo sfidante attuale diventa il banco, il prossimo della lista sfida
        data["banco_idx"] = data["sfidante_idx"]
        data["sfidante_idx"] += 1
        data["fase"] = "PUNTATA"
        st.rerun()

# Auto-refresh per il multiplayer
time.sleep(2)
st.rerun()
