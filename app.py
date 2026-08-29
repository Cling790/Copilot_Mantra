import streamlit as st
import pandas as pd
import re
import json
import os
import string
st.set_page_config(page_title="Fanta_Cop Mantra 2026/27", layout="wide")

# ==========================================
# 🎨 STILI CSS PERSONALIZZATI (FIX HEADER MOBILE)
# ==========================================
st.markdown("""
<style>
/* 1. AZZERA I MARGINI DI PAGINA STREAMLIT */
.main .block-container {
    padding-left: 8px !important;
    padding-right: 8px !important;
    padding-top: 0.6rem !important;
    max-width: 100vw !important;
    overflow-x: hidden !important;
}

/* 2. FORZA L'HEADER A RIMANERE SEMPRE SUI UNA SOLA RIGA (MAI ACCAPO) */
[data-testid="stHorizontalBlock"]:has(button:contains("Esci")) {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    width: 100% !important;
    gap: 8px !important;
    margin-bottom: 5px !important;
}

[data-testid="stHorizontalBlock"]:has(button:contains("Esci")) > [data-testid="stColumn"],
[data-testid="stHorizontalBlock"]:has(button:contains("Esci")) > [data-testid="column"] {
    min-width: 0 !important;
}

[data-testid="stHorizontalBlock"]:has(button:contains("Esci")) > [data-testid="stColumn"]:nth-child(1),
[data-testid="stHorizontalBlock"]:has(button:contains("Esci")) > [data-testid="column"]:nth-child(1) {
    flex: 1 1 auto !important;
}

[data-testid="stHorizontalBlock"]:has(button:contains("Esci")) > [data-testid="stColumn"]:nth-child(2),
[data-testid="stHorizontalBlock"]:has(button:contains("Esci")) > [data-testid="column"]:nth-child(2) {
    flex: 0 0 85px !important;
    width: 85px !important;
}

/* TITOLO COMPATTO MOBILE */
.app-title {
    font-size: 17px !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    margin: 0 !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    gap: 5px !important;
}

/* 3. GAP VERTICALI CONTENUTI */
[data-testid="stVerticalBlock"] { gap: 4px !important; }
.element-container { margin-bottom: 0px !important; margin-top: 0px !important; }

/* 4. LARGHEZZA RIGIDA SOLO PER LA RIGA CARD GIOCATORE + TASTO FULMINE */
[data-testid="stHorizontalBlock"]:has(div.player-main-card) {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    gap: 4px !important;
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    margin-bottom: 3px !important;
}

[data-testid="stHorizontalBlock"]:has(div.player-main-card) > [data-testid="stColumn"]:nth-child(1),
[data-testid="stHorizontalBlock"]:has(div.player-main-card) > [data-testid="column"]:nth-child(1) {
    flex: 1 1 auto !important;
    width: calc(100% - 46px) !important;
    min-width: 0 !important;
}

[data-testid="stHorizontalBlock"]:has(div.player-main-card) > [data-testid="stColumn"]:nth-child(2),
[data-testid="stHorizontalBlock"]:has(div.player-main-card) > [data-testid="column"]:nth-child(2) {
    flex: 0 0 42px !important;
    width: 42px !important;
    min-width: 42px !important;
    max-width: 42px !important;
}

[data-testid="stColumn"], [data-testid="column"] {
    min-width: 0 !important;
}

/* CONTENITORE E STILE BOTTONE */
div.stButton {
    width: 100% !important;
    display: flex !important;
}

div.stButton > button {
    min-height: 38px !important; 
    font-size: 14px !important;  
    padding: 0px !important;
    margin: 0px !important;
    border-radius: 6px !important;
}

/* RIGA NERA PRINCIPALE DEL GIOCATORE */
.player-main-card {
    background-color: #1a1b20 !important;
    border: 1px solid #343a40 !important;
    border-radius: 8px !important;
    padding: 5px 8px !important;
    width: 100% !important;
    box-sizing: border-box !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 3px !important;
    overflow: hidden !important; 
}

/* Badge Ruolo Adattivo */
.role-circle {
    min-width: 28px; 
    height: 18px; 
    padding: 0 4px;
    border-radius: 4px; 
    display: flex; 
    align-items: center; 
    justify-content: center;
    font-size: 9px; 
    font-weight: 800; 
    color: #ffffff !important; 
    flex-shrink: 0;
    white-space: nowrap;
}

/* Nome Giocatore */
.player-name-text {
    font-size: 12px; font-weight: 700; color: #ffffff !important;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; 
    flex-grow: 1; flex-shrink: 1; min-width: 0;
}

/* Badge Squadra */
.team-badge {
    font-size: 9px; font-weight: 700; background: #343a40; color: #e0e0e0 !important;
    padding: 1px 4px; border-radius: 3px; flex-shrink: 0;
}

/* Stelle */
.stars-text { font-size: 8px; color: #f1c40f !important; flex-shrink: 0; letter-spacing: -1px; }

/* Badge FVM */
.fvm-badge-right {
    font-size: 9px; font-weight: 700; background: #0f381e; color: #2ecc71 !important;
    border: 1px solid #27ae60; padding: 1px 5px; border-radius: 4px;
    text-align: center; white-space: nowrap; flex-shrink: 0;
}

/* Tag micro inferiori */
.tag-micro {
    font-size: 8px !important; 
    padding: 1px 4px !important; 
    border-radius: 4px !important; 
    background-color: #e2e8f0 !important;   
    color: #1a202c !important;         
    font-weight: 700 !important;      
    border: 1px solid #cbd5e1 !important; 
    white-space: nowrap !important;
    margin-right: 2px !important; 
    margin-bottom: 2px !important;
}
.tag-mio-style { background: #0055ff !important; color: #ffffff !important; font-weight: bold; border: none !important; }
.tag-venduto-style { background: #c0392b !important; color: #ffffff !important; font-weight: bold; border: none !important; }
.tag-affare-style { background: #d35400 !important; color: #ffffff !important; font-weight: bold; border: none !important; }
.tag-interesse-style { 
    background: #ea580c !important; 
    color: #ffffff !important;      
    font-weight: 800 !important; 
    border: 1px solid #c2410c !important; 
}

/* STILE TAB COMPATTO */
.stTabs [data-baseweb="tab-list"] { 
    gap: 3px !important; 
    background-color: #1e1f26 !important; 
    padding: 3px !important; 
    border-radius: 8px !important; 
    overflow-x: auto !important;
}
.stTabs [data-baseweb="tab"] { 
    background-color: #2e3039 !important; 
    color: #b0b0b0 !important; 
    border-radius: 6px !important; 
    padding: 5px 8px !important; 
    font-size: 11px !important; 
    border: none !important; 
    white-space: nowrap !important;
}
.stTabs [aria-selected="true"] { 
    background-color: #3b82f6 !important; 
    color: #ffffff !important; 
    font-weight: bold !important; 
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 💾 GESTIONE BACKUP E STATO
# ==========================================
FILE_BACKUP = "backup_asta.json"

def salva_backup():
    try:
        dati = {
            "rosa": st.session_state.get("rosa", []),
            "tutti_venduti": st.session_state.get("tutti_venduti", []),
            "autenticato": st.session_state.get("autenticato", False)
        }
        with open(FILE_BACKUP, "w", encoding="utf-8") as f:
            json.dump(dati, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def carica_backup():
    if os.path.exists(FILE_BACKUP):
        try:
            with open(FILE_BACKUP, "r", encoding="utf-8") as f:
                dati = json.load(f)
                if 'rosa' not in st.session_state or not st.session_state.rosa:
                    st.session_state.rosa = dati.get("rosa", [])
                if 'tutti_venduti' not in st.session_state or not st.session_state.tutti_venduti:
                    st.session_state.tutti_venduti = dati.get("tutti_venduti", [])
                if 'autenticato' not in st.session_state:
                    st.session_state.autenticato = dati.get("autenticato", False)
        except Exception:
            pass

carica_backup()

if 'rosa' not in st.session_state: st.session_state.rosa = []
if 'tutti_venduti' not in st.session_state: st.session_state.tutti_venduti = []
if 'autenticato' not in st.session_state: st.session_state.autenticato = False

def rimuovi_giocatore(nome_giocatore):
    st.session_state.rosa = [p for p in st.session_state.rosa if p['Nome'] != nome_giocatore]
    st.session_state.tutti_venduti = [v for v in st.session_state.tutti_venduti if v['Nome'] != nome_giocatore]
    salva_backup()
    st.rerun()

# ==========================================
# 🔐 CONFIGURAZIONE SICUREZZA
# ==========================================
PASSWORD_CORRETTA = "Pf703.d-s"

if not st.session_state.autenticato:
    st.title("🔐 Accesso Riservato")
    st.info("Inserisci la password per accedere alla dashboard.")
    
    col_pwd1, col_pwd2 = st.columns([2, 1])
    with col_pwd1:
        pwd_input = st.text_input("Password:", type="password", key="pwd_field")
    
    if st.button("🔓 Accedi", type="primary"):
        if pwd_input == PASSWORD_CORRETTA:
            st.session_state.autenticato = True
            salva_backup()
            st.rerun()
        else:
            st.error("❌ Password errata!")
    st.stop()

# ==========================================
# ⚽ MAPPATURE RUOLI E REPARTI SEPARATI
# ==========================================
MAPPA_REPARTI = {
    'Portieri': ['POR'],
    'Difensori': ['DD', 'DS', 'DC', 'B'],
    'Centrocampisti': ['C', 'M', 'E'],
    'Trequartisti': ['T', 'W'],
    'Attaccanti': ['A', 'PC']
}

LISTA_RUOLI_MANTRA = ["Tutti", "POR", "DD", "DS", "DC", "B", "C", "M", "E", "T", "W", "A", "PC"]

SCHEMI_MANTRA = {
    "3-4-2-1": [["POR"], ["DC"], ["DC"], ["DC"], ["E", "W"], ["M", "C"], ["M", "C"], ["E", "W"], ["T", "W"], ["T", "A"], ["PC"]],
    "3-4-1-2": [["POR"], ["DC"], ["DC"], ["DC"], ["E", "W"], ["M", "C"], ["M", "C"], ["E", "W"], ["T"], ["PC", "A"], ["PC"]],
    "3-4-3":   [["POR"], ["DC"], ["DC"], ["DC"], ["E", "W"], ["M", "C"], ["M", "C"], ["E", "W"], ["W", "A"], ["PC"], ["W", "A"]],
    "3-5-2":   [["POR"], ["DC"], ["DC"], ["DC"], ["E", "W"], ["M", "C"], ["M", "C"], ["M", "C"], ["E", "W"], ["PC", "A"], ["PC"]],
    "3-5-1-1": [["POR"], ["DC"], ["DC"], ["DC"], ["E", "W"], ["M", "C"], ["M", "C"], ["M", "C"], ["E", "W"], ["T", "A"], ["PC"]],
    "4-3-3":   [["POR"], ["DD"], ["DC"], ["DC"], ["DS"], ["M"], ["C"], ["C"], ["W", "A"], ["PC"], ["W", "A"]],
    "4-3-1-2": [["POR"], ["DD"], ["DC"], ["DC"], ["DS"], ["M", "C"], ["M", "C"], ["M", "C"], ["T"], ["PC", "A"], ["PC"]],
    "4-2-3-1": [["POR"], ["DD"], ["DC"], ["DC"], ["DS"], ["M"], ["M", "C"], ["W"], ["T"], ["W", "A"], ["PC"]],
    "4-3-2-1": [["POR"], ["DD"], ["DC"], ["DC"], ["DS"], ["M", "C"], ["M", "C"], ["M", "C"], ["T"], ["T", "W"], ["PC"]],
    "4-1-4-1": [["POR"], ["DD"], ["DC"], ["DC"], ["DS"], ["M"], ["E"], ["C", "T"], ["C", "T"], ["E"], ["PC", "A"]],
    "4-4-2":   [["POR"], ["DD"], ["DC"], ["DC"], ["DS"], ["E", "W"], ["M", "C"], ["M", "C"], ["E", "W"], ["PC", "A"], ["PC"]],
}

def get_ruolo_colore(rm_str):
    rm_str = str(rm_str).upper()
    tokens = re.findall(r'\b[A-Z]+\b', rm_str)
    if not tokens: return '#7f8c8d'  
    primo_ruolo = tokens[0]
    if primo_ruolo == 'POR': return '#f39c12'
    elif primo_ruolo in ['DD', 'DS', 'DC', 'B']: return '#27ae60'
    elif primo_ruolo in ['C', 'M', 'E']: return '#2980b9'
    elif primo_ruolo in ['T', 'W', 'A', 'PC']: return '#e74c3c'
    return '#7f8c8d'

def get_reparto(rm_str):
    rm_str = str(rm_str).upper()
    tokens = re.findall(r'\b[A-Z]+\b', rm_str)
    if not tokens: return 'Altri'
    primo_ruolo = tokens[0]
    for reparto, ruoli in MAPPA_REPARTI.items():
        if primo_ruolo in ruoli: return reparto
    return 'Altri'

# MODIFICA 1: Caricamento automatico da GitHub / cartella locale
def carica_dati_unico(sorgente=None):
    file_path = sorgente
    if not file_path:
        for nome in ["Quotazioni_Fantacalcio_Stagione_2026_27.xlsx", "Listone.xlsx", "Quotazioni.xlsx"]:
            if os.path.exists(nome):
                file_path = nome
                break
    if not file_path:
        files_repo = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.csv')) and not f.startswith('~$')]
        if files_repo:
            file_path = files_repo[0]
            
    if not file_path: return None
    is_xlsx = getattr(file_path, "name", str(file_path)).lower().endswith('.xlsx')
    try:
        return pd.read_excel(file_path, sheet_name="Tutti", header=0) if is_xlsx else pd.read_csv(file_path, header=0)
    except Exception:
        try:
            return pd.read_excel(file_path, header=0) if is_xlsx else pd.read_csv(file_path, header=0)
        except Exception:
            return None

SLOT_TOTALI = 32
MAX_TRQ_ATT_COMBINATI = 10

tot_fvm_uscite = sum(v['FVM'] for v in st.session_state.tutti_venduti if v.get('FVM', 0) > 0)
tot_spesa_uscite = sum(v['Prezzo'] for v in st.session_state.tutti_venduti)
coeff_inflazione = (tot_spesa_uscite / tot_fvm_uscite) if tot_fvm_uscite > 0 else 1.0

def ottieni_reparto_principale(ruolo_str):
    if not ruolo_str: return None
    tokens = [r.strip().upper() for r in str(ruolo_str).replace(';', ',').replace('/', ',').split(',')]
    if not tokens: return None
    primo = tokens[0]
    if primo in ['P', 'POR']: return 'P'
    elif primo in ['DC', 'DD', 'DS', 'B', 'D']: return 'D'
    elif primo in ['C', 'M', 'E']: return 'C'
    elif primo in ['T', 'W', 'A', 'PC']: return 'TA'
    return None

def calcola_occasioni(df_completo, tutti_venduti):
    miei_nomi_glob = {str(p['Nome']).strip().lower(): p['Prezzo'] for p in st.session_state.rosa}
    venduti_dict_glob = {str(v['Nome']).strip().lower(): v['Prezzo'] for v in tutti_venduti if not v.get('Mio', False)}
    nomi_venduti_totali_glob = set(miei_nomi_glob.keys()).union(set(venduti_dict_glob.keys()))

    slot_avversari = {'P': 36, 'D': 81, 'C': 81, 'TA': 90}
    acq_avv = {'P': 0, 'D': 0, 'C': 0, 'TA': 0}

    rm_col_c = next((c for c in df_completo.columns if str(c).upper() == 'RM'), 'RM')
    nome_col_c = next((c for c in df_completo.columns if str(c).lower() in ['nome', 'calciatore']), 'Nome')

    for nome_v_l in venduti_dict_glob.keys():
        r_v = df_completo[df_completo[nome_col_c].astype(str).str.strip().str.lower() == nome_v_l]
        if not r_v.empty:
            r_v_ruolo_str = str(r_v.iloc[0][rm_col_c])
            rep_v = ottieni_reparto_principale(r_v_ruolo_str)
            if rep_v in acq_avv: acq_avv[rep_v] += 1

    tit_col_glob = next((c for c in df_completo.columns if str(c).strip().lower() in ['titolarità', 'titolarita', 'stelle']), None)

    set_occasioni = set()
    for _, r_f in df_completo.iterrows():
        g_n = r_f[nome_col_c]
        g_n_lower = str(g_n).strip().lower()
        if g_n_lower not in nomi_venduti_totali_glob:
            r_rm_str = str(r_f[rm_col_c]) if rm_col_c in df_completo.columns else ""
            r_rep = ottieni_reparto_principale(r_rm_str)
            
            if r_rep and r_rep in slot_avversari:
                sat_glob = acq_avv[r_rep] / slot_avversari[r_rep]
                n_st_glob = 0
                if tit_col_glob and pd.notna(r_f[tit_col_glob]):
                    try: n_st_glob = int(float(str(r_f[tit_col_glob]).replace(',', '.')))
                    except (ValueError, TypeError): n_st_glob = 0
                
                if sat_glob >= 0.33 and n_st_glob >= 4:
                    set_occasioni.add(g_n_lower)
                    
    return set_occasioni

# ==========================================
# 🖥️ HEADER COMPATTO PER MOBILE (FISSO SU UN'UNICA RIGA)
# ==========================================
col_head1, col_head2 = st.columns([3.2, 0.8], vertical_alignment="center")
with col_head1: 
    st.markdown('<div class="app-title">⚽ Fanta_Cop <span style="font-size:11px; color:#3b82f6; font-weight:600;">Mantra</span></div>', unsafe_allow_html=True)
with col_head2:
    if st.button("🔒 Esci", use_container_width=True):
        st.session_state.autenticato = False
        salva_backup()
        st.rerun()

st.sidebar.header("⚙️ Configurazione Asta")
budget_iniziale = st.sidebar.number_input("Budget iniziale:", value=1000, step=10)
spesa_totale = sum(p['Prezzo'] for p in st.session_state.rosa)
budget_rimanente = budget_iniziale - spesa_totale
giocatori_mancanti = SLOT_TOTALI - len(st.session_state.rosa)
rilancio_massimo = budget_rimanente - (giocatori_mancanti - 1) if giocatori_mancanti > 0 else 0

st.sidebar.metric(label="Budget Rimanente", value=f"{budget_rimanente} cr", delta=f"-{spesa_totale} cr")
st.sidebar.metric(label="Rilancio MAX", value=f"{rilancio_massimo} cr")

st.sidebar.divider()
file_caricato_unico = st.sidebar.file_uploader("📁 Carica Listone Unico", type=["xlsx", "csv"], key="u_unico")

st.sidebar.divider()
if st.sidebar.button("🗑️ Reset Totale Asta", type="secondary", use_container_width=True, key="btn_reset_asta"):
    st.session_state.rosa = []
    st.session_state.tutti_venduti = []
    salva_backup()
    st.rerun()

# ==========================================
# 📑 GESTIONE DELLE TABS
# ==========================================
tab_asta, tab_rosa, tab_venduti, tab_moduli = st.tabs([
    "🔍 Listone", "📋 Rosa", "🤝 Venduti", "🧩 Moduli"
])

df = carica_dati_unico(file_caricato_unico)

if df is not None:
    try:
        colonne = list(df.columns)
        nome_col = next((c for c in colonne if str(c).lower() in ['nome', 'calciatore']), 'Nome')
        rm_col = next((c for c in colonne if str(c).upper() == 'RM'), 'RM')
        squadra_col = next((c for c in colonne if str(c).lower() in ['squadra', 'club']), 'Squadra')
        
        fvm_col = next((c for c in colonne if str(c).strip().lower() == 'fvm m'), None)
        if not fvm_col: fvm_col = next((c for c in colonne if 'fvm' in str(c).lower()), None)
            
        qta_col = next((c for c in colonne if str(c).strip().lower() in ['qt.a m', 'qta m', 'qt_a_m']), None)
        if not qta_col: qta_col = next((c for c in colonne if 'qt' in str(c).lower()), None)

        tit_col = next((c for c in colonne if str(c).lower() in ['titolarità', 'titolarita', 'tit', 'status']), None)
        fascia_col = next((c for c in colonne if str(c).lower() in ['fascia', 'fasce', 'tier']), None)
        note_col = next((c for c in colonne if str(c).lower() in ['note', 'caratteristiche', 'skill']), None)
        miei_nomi = {p['Nome']: p['Prezzo'] for p in st.session_state.rosa}
        venduti_dict = {v['Nome']: v['Prezzo'] for v in st.session_state.tutti_venduti if not v.get('Mio', False)}
        nomi_venduti_totali = list(miei_nomi.keys()) + list(venduti_dict.keys())
        c_infl = coeff_inflazione

        slot_avversari = {'P': 36, 'D': 81, 'C': 81, 'TA': 90}
        acq_avv = {'P': 0, 'D': 0, 'C': 0, 'TA': 0}
        
        for nome_v in venduti_dict.keys():
            r_v = df[df[nome_col].astype(str).str.strip().str.lower() == str(nome_v).strip().lower()]
            if not r_v.empty:
                rep_v = ottieni_reparto_principale(str(r_v.iloc[0][rm_col]))
                if rep_v in acq_avv: acq_avv[rep_v] += 1
    except Exception as e:
        st.error(f"Errore caricamento dati: {e}")

@st.dialog("⚡ Gestione Asta")
def mostra_modal_chiamata():
    current_idx = st.session_state.get('current_player_idx', 0)
    
    if 'coda_asta' in st.session_state and current_idx >= len(st.session_state['coda_asta']):
        st.warning("🏁 Lista giocatori terminata!")
        if st.button("❌ Chiudi", key="btn_close_end"):
            st.session_state['dialog_open'] = False
            st.rerun()
        return

    # Il nome del giocatore attivo nel carosello
    nome_giocatore = st.session_state['coda_asta'][current_idx]
    
    # Recupera la riga corrispondente dal dataframe principale
    g_sel_row = df[df[nome_col].astype(str).str.lower() == str(nome_giocatore).lower()]
    if g_sel_row.empty:
        st.error(f"Giocatore {nome_giocatore} non trovato.")
        if st.button("❌ Chiudi", key="btn_close_err"):
            st.session_state['dialog_open'] = False
            st.rerun()
        return
    g_sel = g_sel_row.iloc[0]

    gn = g_sel[nome_col]
    grm = str(g_sel[rm_col])
    gsq = str(g_sel[squadra_col])[:3].upper() if squadra_col in g_sel else "-"
    v_base = float(g_sel[fvm_col]) if (fvm_col and pd.notna(g_sel[fvm_col])) else 1.0

    rep_p = ottieni_reparto_principale(grm)

    # 🚨 1. CONTROLLO TUOI SLOT (Valori esatti: 4, 9, 9, 10)
    limiti_miei = {"P": 4, "D": 9, "C": 9, "TA": 10}
    max_miei = limiti_miei.get(rep_p, 99)
    miei_nel_ruolo = len([x for x in st.session_state.rosa if ottieni_reparto_principale(x.get('RM', '')) == rep_p])

    # 🚨 2. CONTROLLO SLOT AVVERSARI (Hanno tutti finito?)
    avv_completati = False
    if rep_p and rep_p in slot_avversari and slot_avversari[rep_p] > 0:
        if acq_avv[rep_p] >= slot_avversari[rep_p]:
            avv_completati = True

    # 🌡️ Calcolo Termometro dell'Inflazione per Ruolo
    venduti_ruolo = [
        v for v in st.session_state.tutti_venduti 
        if ottieni_reparto_principale(v.get('RM', '')) == rep_p and v.get('FVM', 0) > 0
    ]
    spesa_tot_ruolo = sum(v['Prezzo'] for v in venduti_ruolo)
    fvm_tot_ruolo = sum(v['FVM'] for v in venduti_ruolo)
    
    infl_ruolo = (spesa_tot_ruolo / fvm_tot_ruolo) if fvm_tot_ruolo > 0 else c_infl
    p_stim = max(1, round(v_base * infl_ruolo))

    # Calcolo Saturazione
    txt_scarsita = ""
    txt_consiglio = ""
    sat = 0

    if rep_p and rep_p in slot_avversari and slot_avversari[rep_p] > 0:
        sat = (acq_avv[rep_p] / slot_avversari[rep_p]) * 100
        txt_scarsita = f" | Sat: **{sat:.0f}%**"

        if sat >= 33:
            if v_base >= 10: 
                txt_consiglio = "Reparto caldo • Valuta rilancio"
            else:
                txt_consiglio = "Reparto saturo • Evita sovrapprezzo"
        else:
            txt_consiglio = "Reparto freddo • Punta a base d'asta"

    # Stampa l'intestazione
    st.markdown(f"### **{gn}** ({gsq} - `{grm}`) ")
    st.caption(f"FVM: **{int(v_base)}** | Consigliato: **{p_stim} cr** (Infl. {rep_p}: {infl_ruolo:.2f}x){txt_scarsita}")
    
    if txt_consiglio:
        st.caption(f"ℹ️ {txt_consiglio}")

    # --- ALERT VISIVI ---
    if miei_nel_ruolo >= max_miei:
        st.error(f"🛑 **REPARTO COMPLETO!** Hai già {miei_nel_ruolo}/{max_miei} giocatori in questo ruolo ({rep_p}).")
        
    if avv_completati:
        st.success(f"🏆 **AVVERSARI PIENI!** Nessuno ha più slot ({acq_avv[rep_p]}/{slot_avversari[rep_p]}). Chiamalo a 1 credito!")
        p_stim = 1
    # --------------------

    prezzo_input = st.number_input("Prezzo Finale:", min_value=1, value=int(p_stim), key=f"p_input_{gn}")
    
    # I 4 Pulsanti per il carosello continuo
    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
    with col_b1:
        if st.button("✅ MIO", type="primary", use_container_width=True, key=f"btn_acq_{gn}"):
            st.session_state.rosa.append({"Nome": gn, "Squadra": gsq, "RM": grm, "Prezzo": prezzo_input})
            st.session_state.tutti_venduti.append({"Nome": gn, "Squadra": gsq, "RM": grm, "FVM": v_base, "Prezzo": prezzo_input, "Mio": True})
            salva_backup()
            st.session_state['current_player_idx'] += 1
            st.rerun()
    with col_b2:
        if st.button("📌 ALTRI", use_container_width=True, key=f"btn_vend_{gn}"):
            st.session_state.tutti_venduti.append({"Nome": gn, "Squadra": gsq, "RM": grm, "FVM": v_base, "Prezzo": prezzo_input, "Mio": False})
            salva_backup()
            st.session_state['current_player_idx'] += 1
            st.rerun()
    with col_b3:
        if st.button("⏭️ PASSO", use_container_width=True, key=f"btn_passo_{gn}"):
            st.session_state['current_player_idx'] += 1
            st.rerun()
    with col_b4:
        if st.button("❌ CHIUDI", use_container_width=True, key=f"btn_close_{gn}"):
            st.session_state['dialog_open'] = False
            st.rerun()

if st.session_state.get('dialog_open', False):
    mostra_modal_chiamata()

if df is not None:
    # ------------------------------------------
    # 🔍 TAB 1: LISTONE & ASTA
    # ------------------------------------------
    with tab_asta:
        set_occasioni = calcola_occasioni(df, st.session_state.tutti_venduti)
        num_occasioni = len(set_occasioni)

        def reset_ruolo_callback():
            st.session_state["filtro_ruolo_specifico"] = "Tutti"

        cerca_nome = st.text_input("🔎 Cerca Nome:", key="filtro_cerca_nome", placeholder="Es. Lautaro...")

        fascia_col_filtro = next((c for c in df.columns if str(c).lower() in ['fascia', 'fasce', 'tier']), None)
        scelta_fascia = "Tutte le fasce"
        if fascia_col_filtro:
            fasce_disponibili = sorted([str(x).strip() for x in df[fascia_col_filtro].dropna().unique() if str(x).strip() not in ['', '-']])
            if fasce_disponibili:
                mappa_fasce = {'t': 'Top', 'st': 'Semi-top', '3': 'Terza', '4': 'Quarta', 'sc': 'Scommessa', 'tit': 'Tit.scarsi', 'out': 'Outsider'}
                scelta_fascia = st.selectbox("⭐ Fascia:", ["Tutte le fasce"] + fasce_disponibili, format_func=lambda x: mappa_fasce.get(str(x).lower(), x), key="filtro_fascia_selectbox")

        col_f1, col_f2, col_f3 = st.columns([1.2, 1.2, 0.8])
        with col_f1: 
            macro_reparto = st.selectbox("🛡️ Reparto:", ["Tutti", "Portieri", "Difensori", "Centrocampisti", "Trequartisti", "Attaccanti"], key="filtro_macro_reparto", on_change=reset_ruolo_callback)
        with col_f2:
            opzioni_ruoli = LISTA_RUOLI_MANTRA if macro_reparto == "Tutti" else ["Tutti"] + MAPPA_REPARTI.get(macro_reparto, [])
            ruolo_specifico = st.selectbox("🎯 Ruolo:", opzioni_ruoli, key="filtro_ruolo_specifico")
        with col_f3:
            lettera_partenza = st.selectbox("🔤 Inizia:", list(string.ascii_uppercase), key="filtro_lettera_partenza")

        col_cb1, col_cb2 = st.columns(2)
        with col_cb1: 
            mostra_anche_venduti = st.checkbox("👁️ Mostra Venduti", value=False)
        with col_cb2: 
            label_checkbox = f"🔥 Affari ({num_occasioni})" if num_occasioni > 0 else "🔥 Affari"
            solo_occasioni = st.checkbox(label_checkbox, value=False, key="solo_affari")

        st.divider()

        df_filtrato = df.copy() if mostra_anche_venduti else df[~df[nome_col].isin(nomi_venduti_totali)].copy()
        if solo_occasioni: df_filtrato = df_filtrato[df_filtrato[nome_col].astype(str).str.strip().str.lower().isin(set_occasioni)]
        if scelta_fascia != "Tutte le fasce" and fascia_col_filtro: df_filtrato = df_filtrato[df_filtrato[fascia_col_filtro].astype(str).str.strip().str.lower() == scelta_fascia.lower()]
        if macro_reparto != "Tutti": df_filtrato = df_filtrato[df_filtrato[rm_col].apply(lambda x: get_reparto(x) == macro_reparto)]
        if ruolo_specifico != "Tutti": df_filtrato = df_filtrato[df_filtrato[rm_col].astype(str).str.contains(r'\b' + re.escape(ruolo_specifico) + r'\b', case=False, na=False)]
        if cerca_nome: df_filtrato = df_filtrato[df_filtrato[nome_col].astype(str).str.lower().str.contains(cerca_nome.lower())]
        if nome_col in df_filtrato.columns: 
            df_filtrato = df_filtrato.sort_values(by=nome_col, key=lambda col: col.astype(str).str.lower(), ascending=True)
            
            if 'lettera_partenza' in locals() and lettera_partenza != "A":
                mask = df_filtrato[nome_col].astype(str).str.upper() >= lettera_partenza
                df_filtrato = pd.concat([df_filtrato[mask], df_filtrato[~mask]]).reset_index(drop=True)
            
            st.session_state['coda_asta'] = df_filtrato[nome_col].tolist()

        tot_risultati = len(df_filtrato)
        c_pag1, c_pag2 = st.columns(2)
        with c_pag1: righe_per_pagina = st.selectbox("Righe:", [50, 100, 200, 500], index=0)
        num_pagine = max(1, (tot_risultati // righe_per_pagina) + (1 if tot_risultati % righe_per_pagina > 0 else 0))
        with c_pag2: pagina_corrente = st.number_input(f"Pag (1-{num_pagine}):", min_value=1, max_value=num_pagine, value=1, step=1) if num_pagine > 1 else 1

        start_idx = (pagina_corrente - 1) * righe_per_pagina
        df_pagina = df_filtrato.iloc[start_idx:start_idx + righe_per_pagina]
        st.caption(f"Trovati **{tot_risultati}** giocatori (Mostrati {len(df_pagina)})")

        for _, row in df_pagina.iterrows():
            g_nome = row[nome_col]
            g_rm = str(row[rm_col]) if rm_col in row else "N/A"
            g_squadra = str(row[squadra_col])[:3].upper() if squadra_col in row else "SER"
            
            fvm_base_num = int(row[fvm_col]) if (fvm_col and pd.notna(row[fvm_col])) else 1
            val_fvm = int(round(fvm_base_num * c_infl))
            
            if abs(c_infl - 1.0) > 0.001:
                fvm_display_html = f'<div class="fvm-badge-right" title="FVM Originario: {fvm_base_num}">{val_fvm} cr</div>'
            else:
                fvm_display_html = f'<div class="fvm-badge-right">{val_fvm} cr</div>'

            val_qta = int(row[qta_col]) if (qta_col and pd.notna(row[qta_col])) else None

            stelle = "-"
            tit_col_name = next((c for c in df.columns if str(c).strip().lower() in ['titolarità', 'titolarita']), None)
            if tit_col_name and pd.notna(row[tit_col_name]):
                val_t = str(row[tit_col_name]).strip()
                if val_t and val_t not in ['', '-', 'nan']:
                    try: stelle = "⭐" * int(float(val_t.replace(',', '.')))
                    except ValueError: stelle = val_t

            tags_list = []
            fascia_c = next((c for c in df.columns if str(c).lower() in ['fascia', 'fasce', 'tier']), None)
            if fascia_c and pd.notna(row[fascia_c]) and str(row[fascia_c]).strip() not in ['', '-']:
                val_fascia = str(row[fascia_c]).strip()
                mappa_fasce = {'t': 'Top', 'st': 'Semi-top', '3': 'Terza', '4': 'Quarta', 'sc': 'Scommessa', 'tit': 'Tit.scarsi', 'out': 'Outsider'}
                tags_list.append(f'<span class="tag-micro">{mappa_fasce.get(val_fascia.lower(), val_fascia)}</span>')
                
            if val_qta is not None: tags_list.append(f'<span class="tag-micro">Q:{val_qta}</span>')
            if note_col and pd.notna(row[note_col]) and str(row[note_col]).strip() not in ['-', '']:
                for t in str(row[note_col]).split(','): tags_list.append(f'<span class="tag-micro">{t.strip()}</span>')
            
            g_nome_lower = str(g_nome).strip().lower()
            if g_nome_lower not in nomi_venduti_totali and g_nome_lower in set_occasioni:
                tags_list.append(f'<span class="tag-micro tag-affare-style">🔥 AFFARE</span>')

            int_col = next((c for c in df.columns if str(c).lower() in ['interesse', 'target', 'obiettivo']), None)
            if int_col and pd.notna(row[int_col]) and str(row[int_col]).strip().upper() not in ['', '-', '0', 'FALSE']:
                tags_list.insert(0, '<span class="tag-micro tag-interesse-style">🎯 TARGET</span>')
            
            if g_nome in miei_nomi: tags_list.insert(0, f'<span class="tag-micro tag-mio-style">MIO ({miei_nomi[g_nome]}cr)</span>')
            elif g_nome in venduti_dict: tags_list.insert(0, f'<span class="tag-micro tag-venduto-style">VENDUTO ({venduti_dict[g_nome]}cr)</span>')

            tags_html = "".join(tags_list)
            col_bg = get_ruolo_colore(g_rm)

            card_html = (
                f'<div class="player-main-card">'
                f'  <div style="display: flex; align-items: center; gap: 4px; width: 100%;">'
                f'    <div class="role-circle" style="background-color: {col_bg};">{g_rm}</div>'
                f'    <span class="player-name-text">{g_nome}</span>'
                f'    <span class="team-badge">{g_squadra}</span>'
                f'    <span class="stars-text">{stelle}</span>'
                f'    {fvm_display_html}'
                f'  </div>'
                f'  <div style="display: flex; align-items: center; gap: 3px; flex-wrap: wrap;">'
                f'    {tags_html}'
                f'  </div>'
                f'</div>'
            )
            c_card, c_btn = st.columns([1, 1], vertical_alignment="center")
            with c_card: st.markdown(card_html, unsafe_allow_html=True)
            with c_btn:
                if st.button("⚡", key=f"btn_chiama_{g_nome}", use_container_width=True, help="Gestisci"):
                    st.session_state['dialog_open'] = True
                    try:
                        st.session_state['current_player_idx'] = st.session_state['coda_asta'].index(g_nome)
                    except (ValueError, KeyError):
                        st.session_state['current_player_idx'] = 0
                    st.rerun()

    # ------------------------------------------
    # 📋 TAB 2: LA MIA ROSA
    # ------------------------------------------
    with tab_rosa:
        st.subheader("📋 La Mia Rosa")
        if st.session_state.rosa:
            st.dataframe(pd.DataFrame(st.session_state.rosa), use_container_width=True)
            st.divider()
            st.markdown("### 🗑️ Svincola Giocatore")
            col_del_r1, col_del_r2 = st.columns([3, 1])
            with col_del_r1: giocatore_da_rimuovere = st.selectbox("Seleziona:", sorted([p["Nome"] for p in st.session_state.rosa]), key="sel_del_mio")
            with col_del_r2:
                st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
                if st.button("❌ Rimuovi", type="primary", key="btn_del_mio", use_container_width=True): rimuovi_giocatore(giocatore_da_rimuovere)

            st.divider()
            p_por = [p for p in st.session_state.rosa if get_reparto(p['RM']) == 'Portieri']
            p_dif = [p for p in st.session_state.rosa if get_reparto(p['RM']) == 'Difensori']
            p_cen = [p for p in st.session_state.rosa if get_reparto(p['RM']) == 'Centrocampisti']
            p_trq = [p for p in st.session_state.rosa if get_reparto(p['RM']) == 'Trequartisti']
            p_att = [p for p in st.session_state.rosa if get_reparto(p['RM']) == 'Attaccanti']
            
            cols_r = st.columns(5)
            cols_r[0].metric("POR", f"{len(p_por)}/4", f"{sum(p['Prezzo'] for p in p_por)}")
            cols_r[1].metric("DIF", f"{len(p_dif)}/9", f"{sum(p['Prezzo'] for p in p_dif)}")
            cols_r[2].metric("CEN", f"{len(p_cen)}/9", f"{sum(p['Prezzo'] for p in p_cen)}")
            cols_r[3].metric("TRQ", f"{len(p_trq)}", f"{sum(p['Prezzo'] for p in p_trq)}")
            cols_r[4].metric("ATT", f"{len(p_att)}", f"{sum(p['Prezzo'] for p in p_att)}")
        else:
            st.info("Nessun giocatore in rosa.")

    # ------------------------------------------
    # 🤝 TAB 3: TUTTI I VENDUTI
    # ------------------------------------------
    with tab_venduti:
        st.subheader("🤝 Venduti Globali")
        if st.session_state.tutti_venduti:
            df_v = pd.DataFrame(st.session_state.tutti_venduti)
            st.dataframe(df_v[["Nome", "Squadra", "RM", "Prezzo", "Mio"]], use_container_width=True)
            st.divider()
            cerca_venduto = st.text_input("🔎 Cerca venduto:", key="search_venduti")
            lista_tutti = sorted([v["Nome"] for v in st.session_state.tutti_venduti])
            if cerca_venduto: lista_tutti = [n for n in lista_tutti if cerca_venduto.lower() in n.lower()]
            if lista_tutti:
                col_del_v1, col_del_v2 = st.columns([3, 1])
                with col_del_v1: giocatore_da_rimuovere_v = st.selectbox("Giocatore:", lista_tutti, key="sel_del_tutti")
                with col_del_v2:
                    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
                    if st.button("❌ Annulla", type="primary", key="btn_del_tutti", use_container_width=True): rimuovi_giocatore(giocatore_da_rimuovere_v)
        else:
            st.info("Nessun giocatore venduto.")

    # ------------------------------------------
    # 🧩 TAB 4: ANALIZZATORE MODULI
    # ------------------------------------------
    with tab_moduli:
        st.subheader("🧩 Moduli Mantra")
        if not st.session_state.rosa:
            st.warning("Acquista prima qualche giocatore.")
        else:
            ruoli_disponibili = {r: [] for r in LISTA_RUOLI_MANTRA[1:]}
            for p in st.session_state.rosa:
                for r_tok in [t.strip().upper() for t in re.split(r'[;,/\s]+', str(p.get('RM', '')))]:
                    if r_tok in ruoli_disponibili: ruoli_disponibili[r_tok].append(p['Nome'])

            def verifica_schema(schema_reqs, giocatori_rosa):
                p_parsed = [{'Nome': p['Nome'], 'Ruoli': set([t.strip().upper() for t in re.split(r'[;,/\s]+', str(p.get('RM', '')))])} for p in giocatori_rosa]
                usati = set()
                def solve(slot_idx):
                    if slot_idx == len(schema_reqs): return True
                    for idx_p, p in enumerate(p_parsed):
                        if idx_p not in usati and any(r in p['Ruoli'] for r in schema_reqs[slot_idx]):
                            usati.add(idx_p)
                            if solve(slot_idx + 1): return True
                            usati.remove(idx_p)
                    return False
                slot_coperti, test_usati = 0, set()
                for opzioni_ruolo in schema_reqs:
                    for idx_p, p in enumerate(p_parsed):
                        if idx_p not in test_usati and any(r in p['Ruoli'] for r in opzioni_ruolo):
                            test_usati.add(idx_p); slot_coperti += 1; break
                return solve(0), slot_coperti

            res_moduli = []
            for mod_nome, reqs in SCHEMI_MANTRA.items():
                is_ok, n_coperti = verifica_schema(reqs, st.session_state.rosa)
                res_moduli.append({"Modulo": mod_nome, "Status": "🟢 OK" if is_ok else ("🟡 " + str(n_coperti) + "/11" if n_coperti >= 8 else "🔴 NO"), "Titolari": f"{n_coperti}/11", "Giocabile": is_ok})

            st.dataframe(pd.DataFrame(res_moduli)[["Modulo", "Status", "Titolari"]], use_container_width=True, hide_index=True)
            moduli_ok = [m["Modulo"] for m in res_moduli if m["Giocabile"]]
            if moduli_ok: st.success(f"🎉 **Completati:** {', '.join(moduli_ok)}")

else:
    st.info("👈 **Nessun Listone trovato su GitHub o caricato!**\n\nCarica il file `.xlsx` o `.csv` dalla barra laterale a sinistra, oppure verifica di aver caricato il file Excel/CSV nella cartella del repository.")

salva_backup()
