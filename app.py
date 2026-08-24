import streamlit as st
import pandas as pd
import re
import json
import os

st.set_page_config(page_title="Fanta Copilot Mantra 2026/27", layout="wide")

# ==========================================
# 🎨 STILI CSS PERSONALIZZATI (OTTIMIZZATI PER MOBILE)
# ==========================================
st.markdown("""
<style>
/* AZZERA IL GAP VERTICALE TRA ELEMENTI */
[data-testid="stVerticalBlock"] { gap: 2px !important; }
.element-container { margin-bottom: 0px !important; margin-top: 0px !important; }

/* BOTTONE "CHIAMA" GIGANTE E QUADRATO PER MOBILE */
div.stButton > button {
    height: 100% !important;
    min-height: 48px !important; /* Molto comodo per il tap col dito */
    font-size: 22px !important;  /* Icona grande */
    padding: 0px !important;
    margin: 0px !important;
    border-radius: 8px !important;
}

/* RIGA NERA PRINCIPALE DEL GIOCATORE */
.player-main-card {
    background-color: #1a1b20 !important;
    border: 1px solid #343a40 !important;
    border-radius: 8px !important;
    padding: 8px !important;
    margin-bottom: 0px !important;
    width: 100% !important;
    box-sizing: border-box !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 6px !important;
    overflow: hidden !important; /* Previene sbavature */
}

/* Badge Ruolo Adattivo (Capsula) */
.role-circle {
    min-width: 32px; 
    height: 20px; 
    padding: 0 5px;
    border-radius: 6px; 
    display: flex; 
    align-items: center; 
    justify-content: center;
    font-size: 9px; 
    font-weight: 800; 
    color: #ffffff !important; 
    flex-shrink: 0;
    white-space: nowrap;
}

/* Nome Giocatore - con min-width: 0 per permettere l'ellipsis su flexbox */
.player-name-text {
    font-size: 14px; font-weight: 700; color: #ffffff !important;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; 
    flex-grow: 1; flex-shrink: 1; min-width: 0;
}

/* Badge Squadra */
.team-badge {
    font-size: 9px; font-weight: 700; background: #343a40; color: #e0e0e0 !important;
    padding: 2px 4px; border-radius: 3px; flex-shrink: 0;
}

/* Stelle */
.stars-text { font-size: 10px; color: #f1c40f !important; flex-shrink: 0; letter-spacing: -1px; }

/* Badge FVM */
.fvm-badge-right {
    font-size: 10px; font-weight: 700; background: #0f381e; color: #2ecc71 !important;
    border: 1px solid #27ae60; padding: 2px 5px; border-radius: 4px;
    text-align: center; white-space: nowrap; flex-shrink: 0;
}

/* Tag micro inferiori */
.tag-micro {
    font-size: 9px; padding: 2px 5px; border-radius: 3px; background: #2b2c34;
    color: #b0b0b0 !important; border: 1px solid #3d3e48; white-space: nowrap;
}
.tag-mio-style { background: #0055ff !important; color: #ffffff !important; font-weight: bold; border: none !important; }
.tag-venduto-style { background: #c0392b !important; color: #ffffff !important; font-weight: bold; border: none !important; }
.tag-affare-style { background: #d35400 !important; color: #ffffff !important; font-weight: bold; border: none !important; }

/* STILE TAB */
.stTabs [data-baseweb="tab-list"] { gap: 6px !important; background-color: #1e1f26 !important; padding: 6px !important; border-radius: 8px !important; }
.stTabs [data-baseweb="tab"] { background-color: #2e3039 !important; color: #b0b0b0 !important; border-radius: 6px !important; padding: 6px 12px !important; font-size: 12px !important; border: none !important; }
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

if 'rosa' not in st.session_state:
    st.session_state.rosa = []
if 'tutti_venduti' not in st.session_state:
    st.session_state.tutti_venduti = []
if 'autenticato' not in st.session_state:
    st.session_state.autenticato = False

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
# ⚽ MAPPATURE RUOLI E REPARTI
# ==========================================
MAPPA_REPARTI = {
    'Portieri': ['POR', 'P'],
    'Difensori': ['DD', 'DS', 'DC', 'B'],
    'Centrocampisti': ['C', 'M', 'E'],
    'Trequartisti/Attaccanti': ['T', 'W', 'A', 'PC']
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
    rm_upper = str(rm_str).upper()
    if any(r in rm_upper for r in ['PC', 'A', 'W']): return '#e74c3c'  # Rosso
    elif any(r in rm_upper for r in ['T', 'C', 'M', 'E']): return '#2980b9'  # Blu
    elif any(r in rm_upper for r in ['DD', 'DS', 'DC', 'B']): return '#27ae60'  # Verde
    return '#f39c12'  # Giallo

def get_reparto(rm_str):
    rm_str = str(rm_str).upper()
    tokens = re.findall(r'\b[A-Z]+\b', rm_str)
    if not tokens: return 'Altri'
    primo_ruolo = tokens[0]
    for reparto, ruoli in MAPPA_REPARTI.items():
        if primo_ruolo in ruoli: return reparto
    return 'Altri'

def leggi_file_intelligente(sorgente):
    is_xlsx = getattr(sorgente, "name", str(sorgente)).lower().endswith('.xlsx')
    for h in [1, 0, 2]:
        try:
            df_temp = pd.read_excel(sorgente, header=h) if is_xlsx else pd.read_csv(sorgente, header=h)
            cols = [str(c).lower().strip() for c in df_temp.columns]
            if any(k in cols for k in ['nome', 'calciatore', 'rm', 'r']): return df_temp
        except Exception: continue
    return None

def unisci_dati(df_main, df_sec):
    if df_main is None or df_sec is None: return df_main
    try:
        col_nome_main = next((c for c in df_main.columns if str(c).lower().strip() in ['nome', 'calciatore']), None)
        col_nome_sec = next((c for c in df_sec.columns if str(c).lower().strip() in ['nome', 'calciatore']), None)
        if col_nome_main and col_nome_sec:
            df_main['_key_nome'] = df_main[col_nome_main].astype(str).str.lower().str.strip()
            df_sec['_key_nome'] = df_sec[col_nome_sec].astype(str).str.lower().str.strip()
            colonne_utili = [c for c in df_sec.columns if c not in df_main.columns or c == '_key_nome']
            df_sec_clean = df_sec[colonne_utili].drop_duplicates(subset=['_key_nome'])
            df_merged = pd.merge(df_main, df_sec_clean, on='_key_nome', how='left', suffixes=('', '_sec'))
            df_merged.drop(columns=['_key_nome'], inplace=True, errors='ignore')
            return df_merged
    except Exception: pass
    return df_main

def carica_dati_completi(file_main_user=None, file_sec_user=None):
    df_main = leggi_file_intelligente(file_main_user) if file_main_user else None
    if not df_main:
        for nome in ["Quotazioni_Fantacalcio_Stagione_2026_27.xlsx", "Quotazioni_Fantacalcio_Stagione_2026_27.csv", "Listone.xlsx", "Quotazioni.xlsx"]:
            if os.path.exists(nome):
                df_main = leggi_file_intelligente(nome)
                if df_main is not None: break
    df_sec = leggi_file_intelligente(file_sec_user) if file_sec_user else None
    if not df_sec:
        for nome in ["FASCE_TIT_RIG.xlsx", "FASCE_TIT_RIG.csv", "Fasce.xlsx"]:
            if os.path.exists(nome):
                df_sec = leggi_file_intelligente(nome)
                if df_sec is not None: break
    return unisci_dati(df_main, df_sec) if df_sec is not None else df_main

LIMITI = {'Portieri': 4, 'Difensori': 9, 'Centrocampisti': 9, 'Trequartisti/Attaccanti': 10}
SLOT_TOTALI = sum(LIMITI.values())

tot_fvm_uscite = sum(v['FVM'] for v in st.session_state.tutti_venduti if v.get('FVM', 0) > 0)
tot_spesa_uscite = sum(v['Prezzo'] for v in st.session_state.tutti_venduti)
coeff_inflazione = (tot_spesa_uscite / tot_fvm_uscite) if tot_fvm_uscite > 0 else 1.0

def calcola_occasioni(df_completo, tutti_venduti):
    nomi_venduti = set(v['Nome'] for v in tutti_venduti)
    fvm_col = next((c for c in df_completo.columns if str(c).lower() in ['fvm m', 'fvm_m', 'fvm mantra', 'fvm']), None)
    df_top = df_completo[pd.to_numeric(df_completo[fvm_col], errors='coerce') >= 12].copy() if fvm_col else df_completo.copy()
    occasioni_set = set()
    rm_col = next((c for c in df_completo.columns if str(c).upper() == 'RM'), 'RM')
    for ruolo in LISTA_RUOLI_MANTRA[1:]:
        df_ruolo = df_top[df_top[rm_col].astype(str).str.contains(r'\b' + re.escape(ruolo) + r'\b', case=False, na=False)]
        if len(df_ruolo) >= 3:
            if (len(df_ruolo[df_ruolo['Nome'].isin(nomi_venduti)]) / len(df_ruolo)) >= 0.60:
                for n in df_ruolo[~df_ruolo['Nome'].isin(nomi_venduti)]['Nome']: occasioni_set.add(n)
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
file_caricato_m = st.sidebar.file_uploader("Sostituisci Quotazioni", type=["xlsx", "csv"], key="u_main")
file_caricato_s = st.sidebar.file_uploader("Sostituisci Fasce/Tit/Rig", type=["xlsx", "csv"], key="u_sec")

# ==========================================
# 📑 GESTIONE DELLE TABS (4 TABS)
# ==========================================
tab_asta, tab_rosa, tab_venduti, tab_moduli = st.tabs([
    "🔍 Listone & Asta", "📋 La Mia Rosa", "🤝 Tutti i Venduti", "🧩 Analizzatore Moduli"
])

df = carica_dati_completi(file_caricato_m, file_caricato_s)

if df is not None:
    try:
        colonne = list(df.columns)
        nome_col = next((c for c in colonne if str(c).lower() in ['nome', 'calciatore']), 'Nome')
        rm_col = next((c for c in colonne if str(c).upper() == 'RM'), 'RM')
        squadra_col = next((c for c in colonne if str(c).lower() in ['squadra', 'club']), 'Squadra')
        fvm_col = next((c for c in colonne if str(c).lower() in ['fvm m', 'fvm_m', 'fvm mantra', 'fvm']), None)
        qta_col = next((c for c in colonne if str(c).lower() in ['qt.a m', 'qt.a', 'qta m', 'qta', 'quotazione']), None)
        tit_col = next((c for c in colonne if str(c).lower() in ['titolarità', 'titolarita', 'tit', 'status']), None)
        fascia_col = next((c for c in colonne if str(c).lower() in ['fascia', 'fasce', 'tier']), None)
        rig_col = next((c for c in colonne if str(c).lower() in ['rigorista', 'rigoristi', 'rig']), None)
        note_col = next((c for c in colonne if str(c).lower() in ['note', 'caratteristiche', 'skill']), None)

        miei_nomi = {p['Nome']: p['Prezzo'] for p in st.session_state.rosa}
        venduti_dict = {v['Nome']: v['Prezzo'] for v in st.session_state.tutti_venduti if not v.get('Mio', False)}
        nomi_venduti_totali = list(miei_nomi.keys()) + list(venduti_dict.keys())
        c_infl = coeff_inflazione

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
            
            def reset_ruolo_callback():
                st.session_state["filtro_ruolo_specifico"] = "Tutti"

            col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns([2, 2, 2, 1, 1])
            with col_f1: macro_reparto = st.selectbox("🛡️ Reparto:", ["Tutti", "Portieri", "Difensori", "Centrocampisti", "Trequartisti/Attaccanti"], key="filtro_macro_reparto", on_change=reset_ruolo_callback)
            with col_f2:
                opzioni_ruoli = LISTA_RUOLI_MANTRA if macro_reparto == "Tutti" else ["Tutti"] + MAPPA_REPARTI.get(macro_reparto, [])
                ruolo_specifico = st.selectbox("🎯 Ruolo:", opzioni_ruoli, key="filtro_ruolo_specifico")
            with col_f3: cerca_nome = st.text_input("🔎 Cerca Nome:", key="filtro_cerca_nome")
            with col_f4: mostra_anche_venduti = st.checkbox("👁️ Mostra Venduti", value=False)
            with col_f5: solo_occasioni = st.checkbox("🔥 Affari", value=False)

            df_filtrato = df.copy() if mostra_anche_venduti else df[~df[nome_col].isin(nomi_venduti_totali)].copy()
            if solo_occasioni: df_filtrato = df_filtrato[df_filtrato[nome_col].isin(set_occasioni)]
            if macro_reparto != "Tutti": df_filtrato = df_filtrato[df_filtrato[rm_col].apply(lambda x: get_reparto(x) == macro_reparto)]
            if ruolo_specifico != "Tutti": df_filtrato = df_filtrato[df_filtrato[rm_col].astype(str).str.contains(r'\b' + re.escape(ruolo_specifico) + r'\b', case=False, na=False)]
            if cerca_nome: df_filtrato = df_filtrato[df_filtrato[nome_col].astype(str).str.lower().str.contains(cerca_nome.lower())]
            if nome_col in df_filtrato.columns: df_filtrato = df_filtrato.sort_values(by=nome_col, key=lambda col: col.astype(str).str.lower(), ascending=True)

            tot_risultati = len(df_filtrato)
            c_pag1, c_pag2 = st.columns([2, 3])
            with c_pag1: righe_per_pagina = st.selectbox("Righe pagina:", [50, 100, 200, 500], index=0)
            num_pagine = max(1, (tot_risultati // righe_per_pagina) + (1 if tot_risultati % righe_per_pagina > 0 else 0))
            with c_pag2: pagina_corrente = st.number_input(f"Pagina (1 - {num_pagine}):", min_value=1, max_value=num_pagine, value=1, step=1) if num_pagine > 1 else 1

            start_idx = (pagina_corrente - 1) * righe_per_pagina
            df_pagina = df_filtrato.iloc[start_idx:start_idx + righe_per_pagina]

            st.write(f"Mostrando **{len(df_pagina)}** di **{tot_risultati}** giocatori:")

            for _, row in df_pagina.iterrows():
                g_nome = row[nome_col]
                g_rm = str(row[rm_col]) if rm_col in row else "N/A"
                g_squadra = str(row[squadra_col])[:3].upper() if squadra_col in row else "SER"
                val_fvm = int(row[fvm_col]) if (fvm_col and pd.notna(row[fvm_col])) else 1
                val_qta = int(row[qta_col]) if (qta_col and pd.notna(row[qta_col])) else None

                tit_val = int(row[tit_col]) if (tit_col and pd.notna(row[tit_col])) else 3
                tit_val = min(max(tit_val, 1), 5)
                stelle = "★" * tit_val + "☆" * (5 - tit_val)

                tags_list = []
                if val_qta is not None: tags_list.append(f'<span class="tag-micro">Qt.a {val_qta}</span>')
                if fascia_col and pd.notna(row[fascia_col]) and str(row[fascia_col]).strip() not in ['-', '']: tags_list.append(f'<span class="tag-micro">{str(row[fascia_col]).strip()}</span>')
                if rig_col and pd.notna(row[rig_col]) and str(row[rig_col]).strip().upper() in ['⚽', 'SI', '1', 'RIGORISTA', 'RIG']: tags_list.append('<span class="tag-micro">⚽ Rig</span>')
                if note_col and pd.notna(row[note_col]) and str(row[note_col]).strip() not in ['-', '']:
                    for t in str(row[note_col]).split(','): tags_list.append(f'<span class="tag-micro">{t.strip()}</span>')
                if g_nome in set_occasioni and g_nome not in nomi_venduti_totali: tags_list.append('<span class="tag-micro tag-affare-style">🔥 AFFARE</span>')
                
                if g_nome in miei_nomi: tags_list.insert(0, f'<span class="tag-micro tag-mio-style">MIO ({miei_nomi[g_nome]} cr)</span>')
                elif g_nome in venduti_dict: tags_list.insert(0, f'<span class="tag-micro tag-venduto-style">VENDUTO ({venduti_dict[g_nome]} cr)</span>')

                tags_html = "".join(tags_list)
                col_bg = get_ruolo_colore(g_rm)

                # NOTA: flex-wrap: wrap inserito qui sotto per evitare lo scorrimento orizzontale dei tag
                card_html = (
                    f'<div class="player-main-card">'
                    f'  <div style="display: flex; align-items: center; gap: 6px; width: 100%;">'
                    f'    <div class="role-circle" style="background-color: {col_bg};">{g_rm}</div>'
                    f'    <span class="player-name-text">{g_nome}</span>'
                    f'    <span class="team-badge">{g_squadra}</span>'
                    f'    <span class="stars-text">{stelle}</span>'
                    f'    <div class="fvm-badge-right">{val_fvm} FVM</div>'
                    f'  </div>'
                    f'  <div style="display: flex; align-items: center; gap: 4px; flex-wrap: wrap;">'
                    f'    {tags_html}'
                    f'  </div>'
                    f'</div>'
                )

                # Layout ottimizzato: 88% alla card, 12% al bottone "⚡" senza etichetta di testo
                c_card, c_btn = st.columns([0.88, 0.12], vertical_alignment="center")
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
                c_r1, c_r2, c_r3, c_r4 = st.columns(4)
                for i, (rep_nome, max_s) in enumerate(LIMITI.items()):
                    p_rep = [p for p in st.session_state.rosa if get_reparto(p['RM']) == rep_nome]
                    [c_r1, c_r2, c_r3, c_r4][i].metric(f"{rep_nome}", f"{len(p_rep)} / {max_s}", f"{sum(p['Prezzo'] for p in p_rep)} cr")
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
