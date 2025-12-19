import streamlit as st
import random
import time

st.set_page_config(page_title="Blackjack Party", page_icon="🃏")

# --- DATABASE CONDIVISO ---
@st.cache_resource
def get_server_data():
    return {
        "setup_completo": False,
        "numero_giocatori": 0,
        "nomi": [],
        "fiches": {},
        "banco_idx": 0,
        "sfidante_idx": 1,
        "fase": "PUNTATA",
        "carta_s": 0, "carta_b": 0, "puntata": 0,
        "ultimo_risultato": "In attesa dell'inizio..."
    }

data = get_server_data()

# --- FASE 0: SETUP (HOST E NOMI) ---
if not data["setup_completo"]:
    st.title("🚀 Configurazione Blackjack")
    
    # L'host sceglie quanti sono
    if data["numero_giocatori"] == 0:
        num = st.number_input("Quante persone giocano in totale? (incluso il banco)", min_value=2, max_value=10, value=3)
        if st.button("Conferma numero giocatori"):
            data["numero_giocatori"] = int(num)
            st.rerun()
    else:
        st.write(f"Posti totali al tavolo: **{data['numero_giocatori']}**")
        st.write(f"Giocatori registrati: {len(data['nomi'])} / {data['numero_giocatori']}")
        
        nuovo_nome = st.text_input("Inserisci il tuo nome per sederti al tavolo:")
        if st.button("Entra nel gioco"):
            if nuovo_nome and nuovo_nome not in data["nomi"]:
                data["nomi"].append(nuovo_nome)
                data["fiches"][nuovo_nome] = 21
                if len(data["nomi"]) == data["numero_giocatori"]:
                    data["setup_completo"] = True
                st.rerun()
            else:
                st.error("Nome non valido o già preso!")
    
    st.info("Aspetta che tutti i tuoi amici abbiano inserito il nome...")
    time.sleep(2)
    st.rerun()

# --- GIOCO VERO E PROPRIO ---
else:
    # Identificazione ruoli
    nome_banco = data["nomi"][data["banco_idx"] % len(data["nomi"])]
    nome_sfidante = data["nomi"][data["sfidante_idx"] % len(data["nomi"])]

    if nome_banco == nome_sfidante:
        data["sfidante_idx"] = (data["sfidante_idx"] + 1) % len(data["nomi"])
        st.rerun()

    st.title("🎰 Blackjack Party")
    st.sidebar.title("💰 Portafogli")
    for n, f in data["fiches"].items():
        st.sidebar.metric(n, f"{f} 🪙")

    st.warning(f"👑 BANCO: **{nome_banco}**")
    st.info(f"⚔️ SFIDANTE: **{nome_sfidante}**")

    # --- LOGICA FASI ---
    if data["fase"] == "PUNTATA":
        st.subheader(f"{nome_sfidante}, punta e gira!")
        c1, c2, c3 = st.columns(3)
        p = 0
        if c1.button("1 🪙"): p = 1
        if c2.button("2 🪙"): p = 2
        if c3.button("3 🪙"): p = 3
        if p > 0:
            data["puntata"] = p
            data["carta_s"] = random.randint(2, 11)
            data["fase"] = "BANCO"
            data["ultimo_risultato"] = f"{nome_sfidante} ha girato un {data['carta_s']}!"
            st.rerun()

    elif data["fase"] == "BANCO":
        st.write(f"🃏 {nome_sfidante} ha un **{data['carta_s']}**")
        if st.button(f"Gira carta di {nome_banco}"):
            data["carta_b"] = random.randint(2, 11)
            if data["carta_s"] > data["carta_b"]:
                data["fiches"][nome_sfidante] += data["puntata"]
                data["fiches"][nome_banco] -= data["puntata"]
                data["ultimo_risultato"] = f"Vince {nome_sfidante}!"
            elif data["carta_s"] < data["carta_b"]:
                data["fiches"][nome_sfidante] -= data["puntata"]
                data["fiches"][nome_banco] += data["puntata"]
                data["ultimo_risultato"] = f"Vince il Banco {nome_banco}!"
            else:
                data["ultimo_risultato"] = "Pareggio!"
            data["fase"] = "RISULTATO"
            st.rerun()

    elif data["fase"] == "RISULTATO":
        st.success(data["ultimo_risultato"])
        if st.button("PROSSIMO TURNO ➡️"):
            data["banco_idx"] = data["sfidante_idx"]
            data["sfidante_idx"] = (data["sfidante_idx"] + 1) % len(data["nomi"])
            data["fase"] = "PUNTATA"
            st.rerun()

    time.sleep(2)
    st.rerun()
