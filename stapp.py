import streamlit as st
import random
import time

st.set_page_config(page_title="Blackjack Final Challenge", page_icon="🏆", layout="wide")

# --- DATABASE CONDIVISO ---
@st.cache_resource
def get_server_data():
    return {
        "setup": False, "num_giocatori": 0, "nomi": [], "fiches": {},
        "banco_idx": 0, "sfidante_idx": 1, "fase": "PUNTATA",
        "mano_s": [], "mano_b": [], "puntata": 0, "messaggio": "",
        "fase_precedente": "", "vincitori": []
    }

data = get_server_data()

if "user" not in st.session_state:
    st.session_state.user = ""

# --- CONTROLLO FINE PARTITA (BANCAROTTA) ---
# Se qualcuno ha 0 fiches, calcoliamo i vincitori
if data["setup"] and not data["vincitori"]:
    for nome, f in data["fiches"].items():
        if f <= 0:
            data["vincitori"] = [n for n, fiches in data["fiches"].items() if fiches > 0]
            data["fase"] = "GAME_OVER"

# --- SCHERMATA FINALE ---
if data["vincitori"]:
    st.balloons()
    st.title("🎊 FINE DEI GIOCHI! 🎊")
    vincitori_str = " e ".join(data["vincitori"])
    st.header(f"🏆 I vincitori sono: {vincitori_str}")
    st.subheader("Qualcuno è rimasto senza fiches ed è andato in bancarotta!")
    if st.button("Ricomincia Nuova Partita"):
        data.clear() # Resetta tutto
        st.rerun()
    st.stop()

# --- SETUP INIZIALE ---
if not data["setup"]:
    st.title("🎰 Setup Torneo Blackjack")
    if data["num_giocatori"] == 0:
        n = st.number_input("Quanti siete a giocare?", 2, 8, 3)
        if st.button("Conferma Numero"): data["num_giocatori"] = int(n); st.rerun()
    else:
        nome = st.text_input("Tuo nome:").strip()
        if st.button("Siediti al tavolo"):
            if nome and nome not in data["nomi"]:
                st.session_state.user = nome
                data["nomi"].append(nome); data["fiches"][nome] = 21
                if len(data["nomi"]) == data["num_giocatori"]: data["setup"] = True
                st.rerun()
    time.sleep(2); st.rerun()

# --- TAVOLO DA GIOCO ---
else:
    banco = data["nomi"][data["banco_idx"] % len(data["nomi"])]
    sfidante = data["nomi"][data["sfidante_idx"] % len(data["nomi"])]
    io_sono_sfidante = (st.session_state.user == sfidante)
