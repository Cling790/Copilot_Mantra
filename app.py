import streamlit as st
import pandas as pd
import re
import json
import os

st.set_page_config(page_title="Fanta Copilot Mantra 2026/27", layout="wide")

# ==========================================
# 🎨 STILI CSS PERSONALIZZATI (ISOLATI E AMICI DEL MOBILE)
# ==========================================
st.markdown("""
<style>
/* 1. AZZERA I MARGINI DI PAGINA STREAMLIT */
.main .block-container {
    padding-left: 6px !important;
    padding-right: 6px !important;
    padding-top: 1.5rem !important;
    max-width: 100vw !important;
    overflow-x: hidden !important;
}

/* 2. GAP VERTICALI CONTENUTI */
[data-testid="stVerticalBlock"] { gap: 4px !important; }
.element-container { margin-bottom: 0px !important; margin-top: 0px !important; }

/* 3. LARGHEZZA RIGIDA SOLO PER LA RIGA CARD GIOCATORE + TASTO FULMINE */
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

/* DISABILITA MIN-WIDTH GENERALE SULLE COLONNE */
[data-testid="stColumn"], [data-testid="column"] {
    min-width: 0 !important;
}

/* CONTENITORE E STILE BOTTONE */
div.stButton {
    width: 100% !important;
    height: 100% !important;
    display: flex !important;
}

div.stButton > button {
    height: 100% !important;
    width: 100% !important;
    min-height: 44px !important; 
    font-size: 18px !important;  
    padding: 0px !important;
    margin: 0px !important;
    border-radius: 6px !important;
}

/* RIGA NERA PRINCIPALE DEL GIOCATORE */
.player-main-card {
    background-color: #1a1b20 !important;
    border: 1px solid #343a40 !important;
    border-radius: 8px !important;
    padding: 4px 6px !important;
    width: 100% !important;
    box-sizing: border-box !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 2px !important;
    overflow: hidden !important; 
}

/* Badge Ruolo Adattivo (Capsula) */
.role-circle {
    min-width: 28px; 
    height: 18px; 
    padding: 0 3px;
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
    padding: 1px 3px; border-radius: 3px; flex-shrink: 0;
}

/* Stelle */
.stars-text { font-size: 8px; color: #f1c40f !important; flex-shrink: 0; letter-spacing: -1px; }

/* Badge FVM */
.fvm-badge-right {
    font-size: 9px; font-weight: 700; background: #0f381e; color: #2ecc71 !important;
    border: 1px solid #27ae60; padding: 1px 4px; border-radius: 4px;
    text-align: center; white-space: nowrap; flex-shrink: 0;
}

/* Tag micro inferiori (Grigio chiaro / Sfondo pulito con scritta nera) - VERIFICATO E CORRETTO */
.tag-micro {
    font-size: 8px !important; 
    padding: 1px 4px !important; 
    border-radius: 4px !important; 
    background-color: #e2e8f0 !important;   /* Grigio chiaro */
    color: #1a202c !important;        /* Scritta Nera */
    font-weight: 700 !important;      /* Grassetto */
    border: 1px solid #cbd5e1 !important; 
    white-space: nowrap !important;
    margin-right: 2px !important; 
    margin-bottom: 2px !important;
}
.tag-mio-style { background: #0055ff !important; color: #ffffff !important; font-weight: bold; border: none !important; }
.tag-venduto-style { background: #c0392b !important; color: #ffffff !important; font-weight: bold; border: none !important; }
.tag-affare-style { background: #d35400 !important; color: #ffffff !important; font-weight: bold; border: none !important; }
/* Stile per il tag dei giocatori d'interesse (Target) */
.tag-interesse-style { 
    background: #ea580c !important; /* Arancione deciso */ 
    color: #ffffff !important;      /* Scritta bianca in evidenza */ 
    font-weight: 800 !important; 
    border: 1px solid #c2410c !important; 
}
/* STILE TAB */
.stTabs [data-baseweb="tab-list"] { gap: 4px !important; background-color: #1e1f26 !important; padding: 4px !important; border-radius: 8px !important; }
.stTabs [data-baseweb="tab"] { background-color: #2e3039 !important; color: #b0b0b0 !important; border-radius: 6px !important; padding: 4px 8px !important; font-size: 11px !important; border: none !important; }
.stTabs [aria-selected="true"] { background-color: #52545f !important; color: #ffffff !important; font-weight: bold !important; }
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
    st.title("🔐 Accesso Riservato - Fanta Copilot")
    st.info("Inserisci la password per accedere alla tua dashboard d'asta.")
    
    col_pwd1, col_pwd2 = st.columns([2, 1])
    with col_pwd1:
        pwd_input = st.text_input("Password di sblocco:", type="password", key="pwd_field")
    
    if st.button("🔓 Accedi all'App", type="primary"):
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
    if not tokens:
        return '#7f8c8d'  
    
    primo_ruolo = tokens[0]
    if primo_ruolo == 'POR':
        return '#f39c12'
    elif primo_ruolo in ['DD', 'DS', 'DC', 'B']:
        return '#27ae60'
    elif primo_ruolo in ['C', 'M', 'E']:
        return '#2980b9'
    elif primo_ruolo in ['T', 'W', 'A', 'PC']:
        return '#e74c3c'
    
    return '#7f8c8d'

def get_reparto(rm_str):
    rm_str = str(rm_str).upper()
    tokens = re.findall(r'\b[A-Z]+\b', rm_str)
    if not tokens: return 'Altri'
    primo_ruolo = tokens[0]
    for reparto, ruoli in MAPPA_REPARTI.items():
        if primo_ruolo in ruoli: return reparto
    return 'Altri'

def carica_dati_unico(sorgente=None):
    file_path = sorgente
    if not file_path:
        for nome in ["Quotazioni_Fantacalcio_Stagione_2026_27.xlsx", "Listone.xlsx", "Quotazioni.xlsx"]:
            if os.path.exists(nome):
                file_path = nome
                break
    if not file_path:
        return None
        
    is_xlsx = getattr(file_path, "name", str(file_path)).lower().endswith('.xlsx')
    try:
        if is_xlsx:
            df = pd.read_excel(file_path, sheet_name="Tutti", header=0)
        else:
            df = pd.read_csv(file_path, header=0)
        return df
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

def calcola_occasioni(df_completo, tutti_venduti):
    nomi_venduti = set(v['Nome'] for v in tutti_venduti)
    
    fvm_col = next((c for c in df_completo.columns if str(c).lower() in ['fvm m', 'fvm_m', 'fvm mantra', 'fvm']), None)
    fascia_col = next((c for c in df_completo.columns if str(c).lower() in ['fascia', 'fasce', 'tier']), None)
    tit_col = next((c for c in df_completo.columns if str(c).lower() in ['titolarità', 'titolarita', 'tit', 'status']), None)
    rm_col = next((c for c in df_completo.columns if str(c).upper() == 'RM'), 'RM')
    
    occasioni_set = set()
    
    # Funzione di supporto per estrarre la "categoria" (Fascia o Stelle) del giocatore
    def get_categoria_strategica(row):
        # 1. Controlliamo se ha una fascia scritta (es. Top, Semi-top, Titolare, ecc.)
        if fascia_col and pd.notna(row[fascia_col]):
            f_txt = str(row[fascia_col]).strip()
            if f_txt and f_txt not in ['-', '']:
                return f_txt.lower() # Es. 'top', 'semi-top', ecc.
        
        # 2. Se non ha una fascia testuale, usiamo le stelle di titolarità come categoria (es. '4 stelle', '5 stelle')
        if tit_col and pd.notna(row[tit_col]):
            val_tit = str(row[tit_col]).strip()
            num_stelle = val_tit.count('⭐')
            if num_stelle >= 4:
                return f'{num_stelle}_stelle'
            else:
                try:
                    num_val = float(val_tit.replace(',', '.'))
                    if num_val >= 4:
                        return f'{int(num_val)}_stelle'
                except ValueError:
                    pass
                    
        return None # Giocatori di fascia bassa o meno importanti che non attivano gli affari di fascia

    # Aggiungiamo temporaneamente la colonna della categoria al dataframe di lavoro
    df_lavoro = df_completo.copy()
    df_lavoro['categoria_affare'] = df_lavoro.apply(get_categoria_strategica, axis=1)
    
    # Scorriamo ogni ruolo Mantra (es. Por, Dc, Dd, Ds, E, C, W, T, A, Pc)
    for ruolo in LISTA_RUOLI_MANTRA[1:]:
        df_ruolo = df_lavoro[df_lavoro[rm_col].astype(str).str.contains(r'\b' + re.escape(ruolo) + r'\b', case=False, na=False)]
        
        # Isoliamo solo i giocatori che appartengono a una fascia/categoria strategica valida
        df_strategici = df_ruolo[df_ruolo['categoria_affare'].notna()]
        
        # Analizziamo il consumo del 60% DIVISO PER SINGOLA FASCIA all'interno del ruolo
        for categoria, df_fascia in df_strategici.groupby('categoria_affare'):
            # Vogliamo che ci sia un numero minimo di giocatori in quella fascia (es. almeno 2 o 3) per far scattare la percentuale
            if len(df_fascia) >= 2:
                venduti_in_fascia = df_fascia[df_fascia['Nome'].isin(nomi_venduti)]
                
                # Se il 60% (o più) di QUELLA SPECIFICA FASCIA è stato venduto...
                if (len(venduti_in_fascia) / len(df_fascia)) >= 0.60:
                    # ...allora tutti i superstiti di quella fascia diventano un AFFARE 🔥
                    rimasti_in_fascia = df_fascia[~df_fascia['Nome'].isin(nomi_venduti)]
                    for n in rimasti_in_fascia['Nome']:
                        occasioni_set.add(n)
                        
    return occasioni_set
    
# --- HEADER & SIDEBAR ---
col_head1, col_head2 = st.columns([4, 1])
with col_head1: st.title("⚽ Fanta Copilot - Dashboard Mantra")
with col_head2:
    if st.button("🔒 Esci"):
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
st.sidebar.metric(label="Rilancio MAX Assoluto", value=f"{rilancio_massimo} cr")

st.sidebar.divider()
st.sidebar.subheader("📁 File caricati")
file_caricato_unico = st.sidebar.file_uploader("Carica Listone Unico (con Titolarità/Fasce/Rig)", type=["xlsx", "csv"], key="u_unico")

st.sidebar.divider()
if st.sidebar.button("🗑️ Reset Totale Asta", type="secondary", use_container_width=True, key="btn_reset_asta"):
    st.session_state.rosa = []
    st.session_state.tutti_venduti = []
    salva_backup()
    st.rerun()

# ==========================================
# 📑 GESTIONE DELLE TABS (4 TABS)
# ==========================================
tab_asta, tab_rosa, tab_venduti, tab_moduli = st.tabs([
    "🔍 Listone & Asta", "📋 La Mia Rosa", "🤝 Tutti i Venduti", "🧩 Analizzatore Moduli"
])

df = carica_dati_unico(file_caricato_unico)

if df is not None:
    try:
        colonne = list(df.columns)
        nome_col = next((c for c in colonne if str(c).lower() in ['nome', 'calciatore']), 'Nome')
        rm_col = next((c for c in colonne if str(c).upper() == 'RM'), 'RM')
        squadra_col = next((c for c in colonne if str(c).lower() in ['squadra', 'club']), 'Squadra')
        
        # Forziamo la lettura dei valori specifici Mantra
        fvm_col = next((c for c in colonne if str(c).strip().lower() == 'fvm m'), None)
        if not fvm_col: 
            fvm_col = next((c for c in colonne if 'fvm' in str(c).lower()), None)
            
        qta_col = next((c for c in colonne if str(c).strip().lower() in ['qt.a m', 'qta m', 'qt_a_m']), None)
        if not qta_col: 
            qta_col = next((c for c in colonne if 'qt' in str(c).lower()), None)

        tit_col = next((c for c in colonne if str(c).lower() in ['titolarità', 'titolarita', 'tit', 'status']), None)
        fascia_col = next((c for c in colonne if str(c).lower() in ['fascia', 'fasce', 'tier']), None)
        rig_col = next((c for c in colonne if str(c).lower() in ['rigorista', 'rigoristi', 'rig']), None)
        note_col = next((c for c in colonne if str(c).lower() in ['note', 'caratteristiche', 'skill']), None)
        miei_nomi = {p['Nome']: p['Prezzo'] for p in st.session_state.rosa}
        venduti_dict = {v['Nome']: v['Prezzo'] for v in st.session_state.tutti_venduti if not v.get('Mio', False)}
        nomi_venduti_totali = list(miei_nomi.keys()) + list(venduti_dict.keys())
        c_infl = coeff_inflazione
        interesse_col = next((c for c in colonne if str(c).lower() in ['interesse', 'preferito', 'watchlist', 'pref']), None)

        # ==========================================
        # 💬 POPUP DIALOG NATIVO (GESTIONE CHIAMATA)
        # ==========================================
        @st.dialog("⚡ Gestione Asta")
        def mostra_modal_chiamata(g_sel):
            gn = g_sel[nome_col]
            grm = str(g_sel[rm_col])
            gsq = str(g_sel[squadra_col])[:3].upper() if squadra_col in g_sel else "-"
            v_base = float(g_sel[fvm_col]) if (fvm_col and pd.notna(g_sel[fvm_col])) else 1.0
            p_stim = max(1, round(v_base * c_infl))

            st.markdown(f"### **{gn}** ({gsq} - `{grm}`) ")
            st.caption(f"Valore FVM: **{int(v_base)}** | Prezzo Consigliato: **{p_stim} cr**")
            prezzo_input = st.number_input("Prezzo Finale d'Asta:", min_value=1, value=int(p_stim), key=f"p_input_{gn}")
            
            col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
            with col_b1:
                if st.button("✅ MIO", type="primary", use_container_width=True, key=f"btn_acq_{gn}"):
                    st.session_state.rosa.append({"Nome": gn, "Squadra": gsq, "RM": grm, "Prezzo": prezzo_input})
                    st.session_state.tutti_venduti.append({"Nome": gn, "Squadra": gsq, "RM": grm, "FVM": v_base, "Prezzo": prezzo_input, "Mio": True})
                    salva_backup()
                    st.rerun()
            with col_b2:
                if st.button("📌 ALTRI", use_container_width=True, key=f"btn_vend_{gn}"):
                    st.session_state.tutti_venduti.append({"Nome": gn, "Squadra": gsq, "RM": grm, "FVM": v_base, "Prezzo": prezzo_input, "Mio": False})
                    salva_backup()
                    st.rerun()
            with col_b3:
                if st.button("❌ CHIUDI", use_container_width=True, key=f"btn_close_{gn}"):
                    st.rerun()

       # ------------------------------------------
        # 🔍 TAB 1: LISTONE & ASTA
        # ------------------------------------------
        with tab_asta:
            set_occasioni = calcola_occasioni(df, st.session_state.tutti_venduti)
            num_occasioni = len(set_occasioni)

            def reset_ruolo_callback():
                st.session_state["filtro_ruolo_specifico"] = "Tutti"

            cerca_nome = st.text_input("🔎 Cerca Nome:", key="filtro_cerca_nome", placeholder="Es. Lautaro, Dybala...")

           # --- FILTRO PER FASCIA ---
            fascia_col_filtro = next((c for c in df.columns if str(c).lower() in ['fascia', 'fasce', 'tier']), None)
            scelta_fascia = "Tutte le fasce"
            if fascia_col_filtro:
                fasce_disponibili = sorted([str(x).strip() for x in df[fascia_col_filtro].dropna().unique() if str(x).strip() not in ['', '-']])
                if fasce_disponibili:
                    # Mappatura per mostrare i nomi estesi nel menu del filtro
                    mappa_fasce = {
                        't': 'Top',
                        'st': 'Semi-top',
                        '3': 'Terza',
                        '4': 'Quarta',
                        'sc': 'Scommessa',
                        'tit': 'Tit.scarsi',
                        'out': 'Outsider'
                    }
                    scelta_fascia = st.selectbox(
                        "⭐ Filtra per Fascia:", 
                        ["Tutte le fasce"] + fasce_disponibili,
                        format_func=lambda x: mappa_fasce.get(str(x).lower(), x),
                        key="filtro_fascia_selectbox"
                    )
            # -------------------------

            col_f1, col_f2 = st.columns(2)
            with col_f1: 
                macro_reparto = st.selectbox(
                    "🛡️ Reparto:", 
                    ["Tutti", "Portieri", "Difensori", "Centrocampisti", "Trequartisti", "Attaccanti"], 
                    key="filtro_macro_reparto", 
                    on_change=reset_ruolo_callback
                )
            with col_f2:
                opzioni_ruoli = LISTA_RUOLI_MANTRA if macro_reparto == "Tutti" else ["Tutti"] + MAPPA_REPARTI.get(macro_reparto, [])
                ruolo_specifico = st.selectbox("🎯 Ruolo:", opzioni_ruoli, key="filtro_ruolo_specifico")

            col_cb1, col_cb2 = st.columns(2)
            with col_cb1: 
                mostra_anche_venduti = st.checkbox("👁️ Mostra anche Venduti", value=False)
            with col_cb2: 
                label_checkbox = f"🔥 Solo Affari / Occasioni ({num_occasioni})" if num_occasioni > 0 else "🔥 Solo Affari / Occasioni"
                solo_occasioni = st.checkbox(label_checkbox, value=False)

            st.divider()

            df_filtrato = df.copy() if mostra_anche_venduti else df[~df[nome_col].isin(nomi_venduti_totali)].copy()
            
            if solo_occasioni: 
                df_filtrato = df_filtrato[df_filtrato[nome_col].isin(set_occasioni)]
            
            # Applicazione del filtro fascia al dataframe
            if scelta_fascia != "Tutte le fasce" and fascia_col_filtro:
                df_filtrato = df_filtrato[df_filtrato[fascia_col_filtro].astype(str).str.strip().str.lower() == scelta_fascia.lower()]
            
            if macro_reparto != "Tutti": 
                df_filtrato = df_filtrato[df_filtrato[rm_col].apply(lambda x: get_reparto(x) == macro_reparto)]
            if ruolo_specifico != "Tutti": 
                df_filtrato = df_filtrato[df_filtrato[rm_col].astype(str).str.contains(r'\b' + re.escape(ruolo_specifico) + r'\b', case=False, na=False)]
            if cerca_nome: 
                df_filtrato = df_filtrato[df_filtrato[nome_col].astype(str).str.lower().str.contains(cerca_nome.lower())]
            if nome_col in df_filtrato.columns: 
                df_filtrato = df_filtrato.sort_values(by=nome_col, key=lambda col: col.astype(str).str.lower(), ascending=True)

            tot_risultati = len(df_filtrato)
            c_pag1, c_pag2 = st.columns(2)
            with c_pag1: 
                righe_per_pagina = st.selectbox("Righe per pagina:", [50, 100, 200, 500], index=0)
            num_pagine = max(1, (tot_risultati // righe_per_pagina) + (1 if tot_risultati % righe_per_pagina > 0 else 0))
            with c_pag2: 
                pagina_corrente = st.number_input(f"Pagina (1 - {num_pagine}):", min_value=1, max_value=num_pagine, value=1, step=1) if num_pagine > 1 else 1

            start_idx = (pagina_corrente - 1) * righe_per_pagina
            df_pagina = df_filtrato.iloc[start_idx:start_idx + righe_per_pagina]
            st.write(f"Mostrando **{len(df_pagina)}** di **{tot_risultati}** giocatori:")
        
# --- CALCOLO GLOBALE AFFARI (Definitivo - Regole Rigorose) ---
        miei_list_glob = st.session_state.get('miei_acquisti', [])
        altri_list_glob = st.session_state.get('altri_acquisti', [])

        miei_nomi_glob = {str(a['nome']).strip().lower(): a['prezzo'] for a in miei_list_glob if isinstance(a, dict) and 'nome' in a}
        venduti_dict_glob = {str(a['nome']).strip().lower(): a['prezzo'] for a in altri_list_glob if isinstance(a, dict) and 'nome' in a}
        nomi_venduti_totali_glob = set(miei_nomi_glob.keys()).union(set(venduti_dict_glob.keys()))

        # Slot avversari esatti: P(36), D(81), C(81), TA(90)
        slot_avversari = {'P': 36, 'D': 81, 'C': 81, 'TA': 90}
        acq_avv_glob = {'P': 0, 'D': 0, 'C': 0, 'TA': 0}

        def ottieni_reparto_principale(ruolo_str):
            if not ruolo_str:
                return None
            # Legge chirurgicamente il PRIMO RUOLO prima di slash o virgole
            tokens = [r.strip().upper() for r in str(ruolo_str).replace(';', ',').replace('/', ',').split(',')]
            if not tokens:
                return None
            
            primo = tokens[0]
            if primo in ['P', 'POR']:
                return 'P'
            elif primo in ['DC', 'DD', 'DS', 'B', 'D']:
                return 'D'  # Difensori
            elif primo in ['C', 'M', 'E']:
                return 'C'  # Centrocampisti (incluso E)
            elif primo in ['T', 'W', 'A', 'PC']:
                return 'TA' # Trequartisti + Attaccanti
            return None

        # Conta gli acquisti degli avversari basandosi unicamente sul primo ruolo
        for nome_v_l in venduti_dict_glob.keys():
            r_v = df[df[nome_col].astype(str).str.strip().str.lower() == nome_v_l]
            if not r_v.empty:
                r_v_ruolo_str = str(r_v.iloc[0][rm_col])
                rep_v = ottieni_reparto_principale(r_v_ruolo_str)
                if rep_v:
                    acq_avv_glob[rep_v] += 1

        # Ricerca della colonna Titolarità con i numeri
        tit_col_glob = next((c for c in df.columns if str(c).strip().lower() in ['titolarità', 'titolarita', 'titolarit\u00e0']), None)
        if not tit_col_glob:
            tit_col_glob = next((c for c in df.columns if 'titolar' in str(c).strip().lower() or 'stelle' in str(c).strip().lower()), None)

        set_occasioni = set()
        for _, r_f in df.iterrows():
            g_n = r_f[nome_col]
            g_n_lower = str(g_n).strip().lower()
            if g_n_lower not in nomi_venduti_totali_glob:
                r_rm_str = str(r_f[rm_col]) if rm_col in df.columns else ""
                r_rep = ottieni_reparto_principale(r_rm_str)
                
                if r_rep:
                    # Calcola la saturazione del reparto del giocatore
                    sat_glob = acq_avv_glob[r_rep] / slot_avversari[r_rep]
                    
                    n_st_glob = 0
                    if tit_col_glob and pd.notna(r_f[tit_col_glob]):
                        try:
                            n_st_glob = int(float(str(r_f[tit_col_glob]).replace(',', '.')))
                        except (ValueError, TypeError):
                            n_st_glob = 0
                    
                    # L'affare scatta SOLO se il reparto supera il 40% E il giocatore ha >= 4 stelle
                    if sat_glob >= 0.40 and n_st_glob >= 4:
                        set_occasioni.add(g_n_lower)
        # --------------------------------------------------------------------------------
        
        for _, row in df_pagina.iterrows():
            g_nome = row[nome_col]
            g_rm = str(row[rm_col]) if rm_col in row else "N/A"
            g_squadra = str(row[squadra_col])[:3].upper() if squadra_col in row else "SER"
            
            # --- GESTIONE FVM ORIGINARIO E INFLAZIONE (Unica novità inserita) ---
            fvm_base_num = int(row[fvm_col]) if (fvm_col and pd.notna(row[fvm_col])) else 1
            val_fvm = int(round(fvm_base_num * c_infl))
            
            if abs(c_infl - 1.0) > 0.001:
                fvm_display_html = f'<div class="fvm-badge-right" title="FVM Originario: {fvm_base_num} cr">{val_fvm} cr <span style="font-size: 10px; opacity: 0.8; text-decoration: line-through;">({fvm_base_num})</span></div>'
            else:
                fvm_display_html = f'<div class="fvm-badge-right">{val_fvm} cr</div>'
            # -------------------------------------------------------------------

            val_qta = int(row[qta_col]) if (qta_col and pd.notna(row[qta_col])) else None

            # --- GESTIONE STELLE DA COLONNA "Titolarità" (Sostituisce l'errore di prima) ---
            stelle = "-"
            tit_col_name = next((c for c in df.columns if str(c).strip().lower() in ['titolarità', 'titolarita']), None)
            if tit_col_name and pd.notna(row[tit_col_name]):
                val_t = str(row[tit_col_name]).strip()
                if val_t and val_t not in ['', '-', 'nan', 'None']:
                    try:
                        num_s = int(float(val_t.replace(',', '.')))
                        stelle = "⭐" * num_s
                    except ValueError:
                        stelle = val_t
            # -------------------------------------------------------------------------------

            # --- IL TUO CODICE ORIGINALE PER I TAG (Intatto) ---
           # --- COSTRUZIONE DEI TAG COMPLETA ---
            tags_list = []
            
            # 1. TAG FASCIA
            fascia_c = next((c for c in df.columns if str(c).lower() in ['fascia', 'fasce', 'tier']), None)
            if fascia_c and pd.notna(row[fascia_c]) and str(row[fascia_c]).strip() not in ['', '-']:
                val_fascia = str(row[fascia_c]).strip()
                
                # Mappatura personalizzata delle fasce
                mappa_fasce = {
                    't': 'Top',
                    'st': 'Semi-top',
                    '3': 'Terza',
                    '4': 'Quarta',
                    'sc': 'Scommessa',
                    'tit': 'Tit.scarsi',
                    'out': 'Outsider'
                }
                
                # Traduce la sigla (convertita in minuscolo per sicurezza), se non la trova lascia l'originale
                nome_fascia = mappa_fasce.get(val_fascia.lower(), val_fascia)
                
                tags_list.append(f'<span class="tag-micro">{nome_fascia}</span>')
                
            # 2. TAG QUOTAZIONE (Q.ta)
            if val_qta is not None:
                tags_list.append(f'<span class="tag-micro">Q.ta: {val_qta}</span>')

            # 3. TAG NOTE (Altre info)
            if note_col and pd.notna(row[note_col]) and str(row[note_col]).strip() not in ['-', '']:
                for t in str(row[note_col]).split(','): 
                    tags_list.append(f'<span class="tag-micro">{t.strip()}</span>')
            
           # 4. TAG VERO AFFARE (Sincronizzato con il filtro e il contatore)
            g_nome_lower = str(g_nome).strip().lower()
            if g_nome_lower not in nomi_venduti_totali and g_nome in set_occasioni:
                ruoli_g = str(g_rm).upper()
                rep_g = 'P' if ('POR' in ruoli_g or ruoli_g == 'P') else ('D' if any(r in ruoli_g for r in ['DC', 'DD', 'DS', 'E', 'D']) else ('C' if any(r in ruoli_g for r in ['M', 'C']) else 'A'))
                
                # Recuperiamo la percentuale di saturazione e le stelle per il tooltip
                perc_sat = int((acq_avv[rep_g] / slot_avversari[rep_g]) * 100)
                num_stelle = stelle.count('⭐')
                
                tags_list.append(f'<span class="tag-micro tag-affare-style" title="Reparto {rep_g} saturo al {perc_sat}% ({num_stelle} Stelle)">🔥 VERO AFFARE</span>')
            # 5. TAG TARGET / INTERESSE
            is_interesse = False
            int_col = next((c for c in df.columns if str(c).lower() in ['interesse', 'target', 'obiettivo']), None)
            if int_col and pd.notna(row[int_col]):
                val_int = str(row[int_col]).strip().upper()
                if val_int in ['X', 'SI', 'SÌ', '1', 'TRUE', 'YES'] or (val_int != '' and val_int != '-'):
                    is_interesse = True

            if is_interesse:
                tags_list.insert(0, '<span class="tag-micro tag-interesse-style">🎯 TARGET</span>')
            
            # 6. TAG MIO / VENDUTO
            if g_nome in miei_nomi: 
                tags_list.insert(0, f'<span class="tag-micro tag-mio-style">MIO ({miei_nomi[g_nome]} cr)</span>')
            elif g_nome in venduti_dict: 
                tags_list.insert(0, f'<span class="tag-micro tag-venduto-style">VENDUTO ({venduti_dict[g_nome]} cr)</span>')

            tags_html = "".join(tags_list)
            # ------------------------------------

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
            with c_card:
                st.markdown(card_html, unsafe_allow_html=True)
            with c_btn:
                if st.button("⚡", key=f"btn_chiama_{g_nome}", use_container_width=True, help="Gestisci Giocatore"):
                    mostra_modal_chiamata(row.to_dict())
        # ------------------------------------------
        # 📋 TAB 2: LA MIA ROSA
        # ------------------------------------------
        with tab_rosa:
            st.subheader("📋 La Mia Rosa")
            if st.session_state.rosa:
                st.dataframe(pd.DataFrame(st.session_state.rosa), use_container_width=True)
                st.divider()
                st.markdown("### 🗑️ Correggi Errore (Svincola/Annulla Acquisto)")
                col_del_r1, col_del_r2 = st.columns([3, 1])
                with col_del_r1: giocatore_da_rimuovere = st.selectbox("Seleziona il tuo giocatore da annullare:", sorted([p["Nome"] for p in st.session_state.rosa]), key="sel_del_mio")
                with col_del_r2:
                    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                    if st.button("❌ Annulla Acquisto", type="primary", key="btn_del_mio"): rimuovi_giocatore(giocatore_da_rimuovere)

                st.divider()
                st.subheader("📊 Riepilogo Rosa")
                
                p_por = [p for p in st.session_state.rosa if get_reparto(p['RM']) == 'Portieri']
                p_dif = [p for p in st.session_state.rosa if get_reparto(p['RM']) == 'Difensori']
                p_cen = [p for p in st.session_state.rosa if get_reparto(p['RM']) == 'Centrocampisti']
                p_trq = [p for p in st.session_state.rosa if get_reparto(p['RM']) == 'Trequartisti']
                p_att = [p for p in st.session_state.rosa if get_reparto(p['RM']) == 'Attaccanti']
                
                tot_trq_att = len(p_trq) + len(p_att)

                cols_r = st.columns(5)
                cols_r[0].metric("Portieri", f"{len(p_por)} / 4", f"{sum(p['Prezzo'] for p in p_por)} cr")
                cols_r[1].metric("Difensori", f"{len(p_dif)} / 9", f"{sum(p['Prezzo'] for p in p_dif)} cr")
                cols_r[2].metric("Centrocampisti", f"{len(p_cen)} / 9", f"{sum(p['Prezzo'] for p in p_cen)} cr")
                cols_r[3].metric("Trequartisti", f"{len(p_trq)}", f"{sum(p['Prezzo'] for p in p_trq)} cr")
                cols_r[4].metric("Attaccanti", f"{len(p_att)}", f"{sum(p['Prezzo'] for p in p_att)} cr")
                
                st.caption(f"🎯 **Trequartisti + Attaccanti:** {tot_trq_att} / {MAX_TRQ_ATT_COMBINATI} slot complessivi occupati.")
            else:
                st.info("Nessun giocatore acquistato finora.")

        # ------------------------------------------
        # 🤝 TAB 3: TUTTI I VENDUTI
        # ------------------------------------------
        with tab_venduti:
            st.subheader("🤝 Riepilogo Generale Venduti")
            if st.session_state.tutti_venduti:
                df_v = pd.DataFrame(st.session_state.tutti_venduti)
                st.dataframe(df_v[["Nome", "Squadra", "RM", "Prezzo", "Mio"]], use_container_width=True)
                st.divider()
                st.markdown("### 🗑️ Correggi Errore Globale")
                cerca_venduto = st.text_input("🔎 Filtra per iniziali o nome:", key="search_venduti")
                lista_tutti = sorted([v["Nome"] for v in st.session_state.tutti_venduti])
                if cerca_venduto: lista_tutti = [n for n in lista_tutti if cerca_venduto.lower() in n.lower()]
                if lista_tutti:
                    col_del_v1, col_del_v2 = st.columns([3, 1])
                    with col_del_v1: giocatore_da_rimuovere_v = st.selectbox("Seleziona giocatore:", lista_tutti, key="sel_del_tutti")
                    with col_del_v2:
                        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                        if st.button("❌ Annulla Acquisto", type="primary", key="btn_del_tutti"): rimuovi_giocatore(giocatore_da_rimuovere_v)
                else: st.warning("⚠️ Nessun giocatore corrisponde.")
            else:
                st.info("Nessun giocatore venduto.")

        # ------------------------------------------
        # 🧩 TAB 4: ANALIZZATORE MODULI
        # ------------------------------------------
        with tab_moduli:
            st.subheader("🧩 Analizzatore Moduli Mantra")
            if not st.session_state.rosa:
                st.warning("⚠️ Non hai ancora acquistato giocatori.")
            else:
                ruoli_disponibili = {r: [] for r in LISTA_RUOLI_MANTRA[1:]}
                for p in st.session_state.rosa:
                    for r_tok in [t.strip().upper() for t in re.split(r'[;,/\s]+', str(p.get('RM', '')))]:
                        if r_tok in ruoli_disponibili: ruoli_disponibili[r_tok].append(p['Nome'])

                st.markdown("### 🎴 Giocatori per Ruolo")
                cols_r = st.columns(len(ruoli_disponibili))
                for idx, (ruolo_k, lista_p) in enumerate(ruoli_disponibili.items()):
                    with cols_r[idx]:
                        col_c = get_ruolo_colore(ruolo_k)
                        st.markdown(f"<div style='text-align:center; background-color:{col_c}; color:white; font-weight:bold; border-radius:6px; padding:2px;'>{ruolo_k}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='text-align:center; font-size:18px; font-weight:800;'>{len(lista_p)}</div>", unsafe_allow_html=True)

                st.divider()
                st.markdown("### 📐 Verificatore Moduli")

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
                    res_moduli.append({"Modulo": mod_nome, "Status": "🟢 GIOCABILE" if is_ok else ("🟡 PARZIALE" if n_coperti >= 8 else "🔴 INCOMPLETO"), "Titolari Coperti": f"{n_coperti} / 11", "Giocabile": is_ok})

                ch_mod1, ch_mod2 = st.columns([2, 3])
                with ch_mod1: st.dataframe(pd.DataFrame(res_moduli)[["Modulo", "Status", "Titolari Coperti"]], use_container_width=True, hide_index=True)
                with ch_mod2:
                    moduli_ok = [m["Modulo"] for m in res_moduli if m["Giocabile"]]
                    if moduli_ok: st.success(f"🎉 **Moduli completi:** {', '.join(moduli_ok)}")
                    else: st.info("💡 Nessun modulo completo.")

    except Exception as e:
        st.error(f"Errore: {e}")

salva_backup()
