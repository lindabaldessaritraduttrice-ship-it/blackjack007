import streamlit as st
import random
import time

st.set_page_config(page_title="Blackjack Real", page_icon="🃏", layout="wide")

# --- DATABASE CONDIVISO (Sincronizzato tra tutti) ---
@st.cache_resource
def get_server_data():
    return {
        "setup_finito": False,
        "posti_totali": 0,
        "nomi": [],
        "fiches": {},
        "banco_idx": 0,
        "sfidante_idx": 1,
        "fase": "PUNTATA",
        "mano_s": [], "mano_b": [], "puntata": 0,
        "messaggio": "", "vincitori": []
    }

data = get_server_data()

# --- RESET PER EMERGENZA ---
if st.sidebar.button("🔄 Reset Totale (Usa se bloccato)"):
    data.update({"setup_finito": False, "posti_totali": 0, "nomi": [], "fiches": {}, "vincitori": [], "fase": "PUNTATA"})
    st.rerun()

# --- FINE PARTITA ---
if data["vincitori"]:
    st.balloons()
    st.title("🎊 CAMPIONATO CONCLUSO! 🎊")
    st.header(f"🏆 Vincitori rimasti: {', '.join(data['vincitori'])}")
    st.subheader("Qualcuno è andato in bancarotta!")
    if st.button("Nuova Partita"):
        data.update({"setup_finito": False, "posti_totali": 0, "nomi": [], "fiches": {}, "vincitori": [], "fase": "PUNTATA"})
        st.rerun()
    st.stop()

# --- MENU INIZIALE ---
if not data["setup_finito"]:
    st.title("🃏 Benvenuti al Tavolo")
    
    if data["posti_totali"] == 0:
        n = st.number_input("In quanti giocate?", 2, 6, 3)
        if st.button("Conferma Numero"):
            data["posti_totali"] = int(n)
            st.rerun()
    else:
        st.write(f"👥 Giocatori pronti: {len(data['nomi'])} su {data['posti_totali']}")
        nome = st.text_input("Inserisci il tuo nome:").strip()
        if st.button("Entra in gioco"):
            if nome and nome not in data["nomi"]:
                data["nomi"].append(nome)
                data["fiches"][nome] = 21
                if len(data["nomi"]) == data["posti_totali"]:
                    data["setup_finito"] = True
                st.rerun()
            else:
                st.error("Nome non valido o già preso!")
    
    time.sleep(2)
    st.rerun()

# --- GIOCO ATTIVO ---
else:
    # Controllo bancarotta
    for n, f in data["fiches"].items():
        if f <= 0:
            data["vincitori"] = [gioc for gioc, fiches in data["fiches"].items() if fiches > 0]
            st.rerun()

    banco = data["nomi"][data["banco_idx"] % len(data["nomi"])]
    sfidante = data["nomi"][data["sfidante_idx"] % len(data["nomi"])]
    
    for n, f in data["fiches"].items():
        st.sidebar.metric(n, f"{f} 🪙")

    st.title("🎰 Blackjack Live")
    st.subheader(f"👑 Banco: {banco} | ⚔️ Sfidante: {sfidante}")

    # --- SCELTA ASSO ---
    if data["fase"] == "SCELTA_ASSO":
        target = sfidante if data["fase_precedente"] == "TURNO_SFIDANTE" else banco
        st.warning(f"🃏 {target}, hai un ASSO! Scegli il valore:")
        # Qui usiamo un piccolo trucco: mostriamo i bottoni solo se il nome coincide con l'utente
        # Nota: Streamlit Cloud non sa 'chi' sei finché non lo salviamo nel session_state locale
        col1, col2 = st.columns(2)
        if col1.button("Vale 1"):
            (data["mano_s"] if target == sfidante else data["mano_b"])[-1]['v'] = 1
            data["fase"] = data["fase_precedente"]; st.rerun()
        if col2.button("Vale 11"):
            (data["mano_s"] if target == sfidante else data["mano_b"])[-1]['v'] = 11
            data["fase"] = data["fase_precedente"]; st.rerun()

    # --- FASE 1: PUNTATA ---
    elif data["fase"] == "PUNTATA":
        st.info(f"In attesa della mossa di {sfidante}...")
        p = st.number_input(f"{sfidante}, quanto punti?", 1, data["fiches"][sfidante], 2)
        if st.button("CONFERMA E PESCA"):
            data["puntata"] = p
            data["mano_s"] = [{'n':str(random.randint(2,10)), 'v':random.randint(2,10)}]
            data["mano_b"] = [{'n':str(random.randint(2,10)), 'v':random.randint(2,10)}]
            data["fase"] = "TURNO_SFIDANTE"; st.rerun()

    # --- FASE 2: TURNO SFIDANTE ---
    elif data["fase"] == "TURNO_SFIDANTE":
        pts_s = sum(c['v'] for c in data["mano_s"])
        st.write(f"### Mano di {sfidante}: {pts_s} punti")
        c1, c2 = st.columns(2)
        if c1.button("HIT (Carta)"):
            v = random.randint(1, 11)
            if v == 1 or v == 11:
                data["mano_s"].append({'v':0})
                data["fase_precedente"] = "TURNO_SFIDANTE"; data["fase"] = "SCELTA_ASSO"
            else:
                data["mano_s"].append({'v':v})
            if sum(c['v'] for c in data["mano_s"]) > 21:
                data["fiches"][sfidante] -= data["puntata"]; data["fiches"][banco] += data["puntata"]
                data["messaggio"] = f"💥 {sfidante} ha sballato!"; data["fase"] = "FINE"
            st.rerun()
        if c2.button("STAND (Stai)"):
            data["fase"] = "TURNO_BANCO"; st.rerun()

    # --- FASE 3: TURNO BANCO ---
    elif data["fase"] == "TURNO_BANCO":
        pts_b = sum(c['v'] for c in data["mano_b"])
        st.write(f"### Mano Banco ({banco}): {pts_b} punti")
        if st.button("Pesca Carta Banco"):
            v = random.randint(2,10)
            data["mano_b"].append({'v':v})
            st.rerun()
        if st.button("Confronta"):
            ps, pb = sum(c['v'] for c in data["mano_s"]), sum(c['v'] for c in data["mano_b"])
            if pb > 21 or ps > pb:
                data["fiches"][sfidante] += data["puntata"]; data["fiches"][banco] -= data["puntata"]
                data["messaggio"] = f"✅ {sfidante} vince!"
            else:
                data["fiches"][sfidante] -= data["puntata"]; data["fiches"][banco] += data["puntata"]
                data["messaggio"] = f"❌ {banco} vince!"
            data["fase"] = "FINE"; st.rerun()

    # --- FASE 4: FINE ---
    elif data["fase"] == "FINE":
        st.header(data["messaggio"])
        if st.button("Prossimo Giro ➡️"):
            data["banco_idx"] = data["sfidante_idx"]
            data["sfidante_idx"] = (data["sfidante_idx"] + 1) % len(data["nomi"])
            data["fase"] = "PUNTATA"; st.rerun()

    time.sleep(2)
    st.rerun()
