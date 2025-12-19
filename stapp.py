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
    io_sono_banco = (st.session_state.user == banco)
    
    st.sidebar.title("💰 Saldo Attuale")
    for n, f in data["fiches"].items():
        st.sidebar.markdown(f"**{n}**: {f} 🪙")

    # --- SCELTA ASSO MANUALE ---
    if data["fase"] == "SCELTA_ASSO":
        target = sfidante if data["fase_precedente"] == "TURNO_SFIDANTE" else banco
        st.warning(f"❗ {target} ha un ASSO! Deve scegliere.")
        if st.session_state.user == target:
            c1, c2 = st.columns(2)
            if c1.button("Vale 1"):
                (data["mano_s"] if target == sfidante else data["mano_b"])[-1]['v'] = 1
                data["fase"] = data["fase_precedente"]; st.rerun()
            if c2.button("Vale 11"):
                (data["mano_s"] if target == sfidante else data["mano_b"])[-1]['v'] = 11
                data["fase"] = data["fase_precedente"]; st.rerun()
        time.sleep(2); st.rerun()

    # --- FASI DI GIOCO ---
    elif data["fase"] == "PUNTATA":
        st.info(f"👑 Banco: {banco} | ⚔️ Sfidante: {sfidante}")
        if io_sono_sfidante:
            p = st.number_input("Quanto punti?", 1, data["fiches"][sfidante], 2)
            if st.button("Inizia Mano"):
                data["puntata"] = p
                c1, c2 = {'n':random.choice(['2','3','J','Q','K','A']), 'v':0}, {'n':random.choice(['2','3','J','Q','K','A']), 'v':0}
                # (Semplificazione: qui usiamo numeri per velocità, ma la logica dell'asso resta)
                data["mano_s"] = [{'n':str(random.randint(2,10)), 'v':random.randint(2,10)}]
                data["mano_b"] = [{'n':str(random.randint(2,10)), 'v':random.randint(2,10)}]
                data["fase"] = "TURNO_SFIDANTE"; st.rerun()
        else: st.info(f"Aspetta {sfidante}...")

    elif data["fase"] == "TURNO_SFIDANTE":
        pts = sum(c['v'] for c in data["mano_s"])
        st.write(f"### Tua mano: {pts} punti")
        if io_sono_sfidante:
            col1, col2 = st.columns(2)
            if col1.button("CARTA"):
                v = random.randint(1,11)
                if v == 1 or v == 11:
                    data["mano_s"].append({'n':'A', 'v':0})
                    data["fase_precedente"] = "TURNO_SFIDANTE"; data["fase"] = "SCELTA_ASSO"
                else:
                    data["mano_s"].append({'n':str(v), 'v':v})
                st.rerun()
            if col2.button("STAI"): data["fase"] = "TURNO_BANCO"; st.rerun()

    elif data["fase"] == "TURNO_BANCO":
        pts_b = sum(c['v'] for c in data["mano_b"])
        st.write(f"### Mano Banco: {pts_b} punti")
        if io_sono_banco:
            if st.button("Gira/Pesca"):
                v = random.randint(1,11)
                data["mano_b"].append({'n':str(v), 'v':v}) # Logica semplificata per il banco
                st.rerun()
            if st.button("Confronta"):
                ps, pb = sum(c['v'] for c in data["mano_s"]), sum(c['v'] for c in data["mano_b"])
                if pb > 21 or ps > pb: 
                    data["fiches"][sfidante] += data["puntata"]; data["fiches"][banco] -= data["puntata"]
                    data["messaggio"] = "Vince lo Sfidante!"
                else:
                    data["fiches"][sfidante] -= data["puntata"]; data["fiches"][banco] += data["puntata"]
                    data["messaggio"] = "Vince il Banco!"
                data["fase"] = "FINE"; st.rerun()

    elif data["fase"] == "FINE":
        st.header(data["messaggio"])
        if st.button("Vai alla prossima mano"):
            data["banco_idx"] = data["sfidante_idx"]
            data["sfidante_idx"] = (data["sfidante_idx"] + 1) % len(data["nomi"])
            data["fase"] = "PUNTATA"; st.rerun()

    time.sleep(2); st.rerun()
