import streamlit as st
import random
import time

st.set_page_config(page_title="Blackjack Live", page_icon="🃏")

# --- DATABASE CONDIVISO ---
@st.cache_resource
def get_server_data():
    return {
        "nomi": ["Giocatore 1", "Giocatore 2", "Banco"], # Cambia i nomi qui!
        "fiches": {"Giocatore 1": 21, "Giocatore 2": 21, "Banco": 100},
        "fase": "PUNTATA",
        "sfidante_idx": 0,
        "carta_s": 0, "carta_b": 0, "puntata": 0,
        "ultimo_risultato": "In attesa..."
    }

data = get_server_data()

# Titolo e Classifica
st.title("🎰 Blackjack Multiplayer")
st.sidebar.title("💰 Fiches")
for n, f in data["fiches"].items():
    st.sidebar.write(f"{n}: {f}")

# Funzione per cambiare turno
def prossimo_turno():
    data["sfidante_idx"] = (data["sfidante_idx"] + 1) % (len(data["nomi"]) - 1)
    data["fase"] = "PUNTATA"

sfidante = data["nomi"][data["sfidante_idx"]]

st.info(f"⚔️ Turno di: **{sfidante}**")
st.write(f"📢 Stato: {data['ultimo_risultato']}")

# --- LOGICA DI GIOCO ---
if data["fase"] == "PUNTATA":
    st.subheader(f"{sfidante}, quanto punti?")
    c1, c2, c3 = st.columns(3)
    p = 0
    if c1.button("1 🪙"): p = 1
    if c2.button("2 🪙"): p = 2
    if c3.button("3 🪙"): p = 3
    
    if p > 0:
        data["puntata"] = p
        data["carta_s"] = random.randint(2, 11)
        data["fase"] = "BANCO"
        data["ultimo_risultato"] = f"{sfidante} ha puntato {p} e ha un {data['carta_s']}. Tocca al Banco!"
        st.rerun()

elif data["fase"] == "BANCO":
    st.write(f"🃏 {sfidante} ha un **{data['carta_s']}**")
    if st.button("GIRA CARTA BANCO 👑"):
        data["carta_b"] = random.randint(2, 11)
        
        if data["carta_s"] > data["carta_b"]:
            data["fiches"][sfidante] += data["puntata"]
            data["fiches"]["Banco"] -= data["puntata"]
            data["ultimo_risultato"] = f"{sfidante} VINCE ({data['carta_s']} vs {data['carta_b']})!"
        elif data["carta_s"] < data["carta_b"]:
            data["fiches"][sfidante] -= data["puntata"]
            data["fiches"]["Banco"] += data["puntata"]
            data["ultimo_risultato"] = f"BANCO VINCE ({data['carta_b']} vs {data['carta_s']})!"
        else:
            data["ultimo_risultato"] = "PAREGGIO!"
        
        data["fase"] = "RISULTATO"
        st.rerun()

elif data["fase"] == "RISULTATO":
    st.success(data["ultimo_risultato"])
    if st.button("PROSSIMO GIOCATORE ➡️"):
        prossimo_turno()
        st.rerun()

# --- AUTO AGGIORNAMENTO OGNI 3 SECONDI ---
time.sleep(3)
st.rerun()
