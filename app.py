import streamlit as st
import pandas as pd
import re
import json
import os

st.set_page_config(page_title="Fanta Copilot Mantra 2026/27", layout="wide")

# ==========================================
# 🎨 STILI CSS PERSONALIZZATI (DARK CARDS)
# ==========================================
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
    }
    
    .player-card {
        background-color: #161a23;
        border: 1px solid #282e3d;
        border-radius: 12px;
        padding: 10px 14px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: white;
    }
    
    .player-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .role-badge-circle {
        width: 42px;
        height: 42px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 13px;
        color: white;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.6);
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }
    
    .team-pill {
        background-color: #2b3245;
        color: #d1d5db;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 5px;
        text-transform: uppercase;
    }
    
    .tit-pill {
        background-color: #1e293b;
        color: #f1c40f;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 5px;
        letter-spacing: 1px;
    }

    .tag-pill {
        background-color: #232936;
        color: #a0aec0;
        font-size: 11px;
        padding: 2px 7px;
        border-radius: 6px;
        border: 1px solid #323b4e;
    }
    
    .fvm-box {
        background-color: #1d6bf3;
        color: white;
        border-radius: 8px;
        padding: 6px 12px;
        text-align: center;
        min-width: 70px;
        box-shadow: 0 2px 8px rgba(29, 107, 243, 0.4);
    }
    .fvm-val {
        font-size: 18px;
        font-weight: 800;
        line-height: 1.1;
    }
    .fvm-label {
        font-size: 9px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        opacity: 0.9;
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

if 'rosa' not in st.session_state:
    st.session_state.rosa = []
if 'tutti_venduti' not in st.session_state:
    st.session_state.tutti_venduti = []
if 'autenticato' not in st.session_state:
    st.session_state.autenticato = False

# FUNZIONE PER ANNULLARE UN ACQUISTO (TUO O DEGLI ALTRI)
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
# ⚽ MAPPATURE RUOLI E COLORI
# ==========================================
MAPPA_REPARTI = {
    'Portieri': ['POR', 'P'],
    'Difensori': ['DD', 'DS', 'DC', 'B'],
    'Centrocampisti': ['E', 'M', 'C'],
    'Trequartisti/Attaccanti': ['W', 'T', 'A', 'PC']
}

LISTA_RUOLI_MANTRA = ["Tutti", "POR", "DD", "DS", "DC", "B", "E", "M", "C", "W", "T", "A", "PC"]

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
    if any(r in rm_upper for r in ['PC', 'A', 'W']):
        return '#e74c3c'  # Rosso
    elif any(r in rm_upper for r in ['T', 'C', 'M', 'E']):
        return '#2980b9'  # Blu
    elif any(r in rm_upper for r in ['DD', 'DS', 'DC', 'B']):
        return '#27ae60'  # Verde
    return '#f39c12'      # Giallo

def get_reparto(rm_str):
    rm_str = str(rm_str).upper()
    tokens = re.findall(r'\b[A-Z]+\b', rm_str)
    for reparto, ruoli in MAPPA_REPARTI.items():
        if any(r in tokens for r in ruoli):
            return reparto
    return 'Altri'

def leggi_file_intelligente(sorgente):
    is_xlsx = getattr(sorgente, "name", str(sorgente)).lower().endswith('.xlsx')
    for h in [1, 0, 2]:
        try:
            if is_xlsx:
                df_temp = pd.read_excel(sorgente, header=h)
            else:
                df_temp = pd.read_csv(sorgente, header=h)
            cols = [str(c).lower().strip() for c in df_temp.columns]
            if any(k in cols for k in ['nome', 'calciatore', 'rm', 'r']):
                return df_temp
        except Exception:
            continue
    return None

def unisci_dati(df_main, df_sec):
    if df_main is None or df_sec is None:
        return df_main
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
    except Exception:
        pass
    return df_main

def carica_dati_completi(file_main_user=None, file_sec_user=None):
    df_main = None
    if file_main_user is not None:
        df_main = leggi_file_intelligente(file_main_user)
    else:
        possibili_nomi_main = [
            "Quotazioni_Fantacalcio_Stagione_2026_27.xlsx",
            "Quotazioni_Fantacalcio_Stagione_2026_27.csv",
            "Listone.xlsx", "Quotazioni.xlsx"
        ]
        for nome in possibili_nomi_main:
            if os.path.exists(nome):
                df_main = leggi_file_intelligente(nome)
                if df_main is not None:
                    break

        if df_main is None:
            try:
                for f in os.listdir("."):
                    f_lower = f.lower()
                    if (f_lower.startswith("quotazioni") or f_lower.startswith("listone")) and (f_lower.endswith(".xlsx") or f_lower.endswith(".csv")):
                        df_main = leggi_file_intelligente(f)
                        if df_main is not None:
                            break
            except Exception:
                pass

    if df_main is None:
        return None

    df_sec = None
    if file_sec_user is not None:
        df_sec = leggi_file_intelligente(file_sec_user)
    else:
        possibili_nomi_sec = [
            "FASCE_TIT_RIG.xlsx",
            "FASCE_TIT_RIG.csv",
            "Fasce.xlsx"
        ]
        for nome in possibili_nomi_sec:
            if os.path.exists(nome):
                df_sec = leggi_file_intelligente(nome)
                if df_sec is not None:
                    break

        if df_sec is None:
            try:
                for f in os.listdir("."):
                    f_lower = f.lower()
                    if ("fasce" in f_lower or "tit" in f_lower) and (f_lower.endswith(".xlsx") or f_lower.endswith(".csv")):
                        df_sec = leggi_file_intelligente(f)
                        if df_sec is not None:
                            break
            except Exception:
                pass

    if df_sec is not None:
        df_main = unisci_dati(df_main, df_sec)

    return df_main

LIMITI = {'Portieri': 4, 'Difensori': 9, 'Centrocampisti': 9, 'Trequartisti/Attaccanti': 10}
SLOT_TOTALI = sum(LIMITI.values())

reparti_count = {'Portieri': 0, 'Difensori': 0, 'Centrocampisti': 0, 'Trequartisti/Attaccanti': 0}
for p in st.session_state.rosa:
    rep = get_reparto(p['RM'])
    if rep in reparti_count:
        reparti_count[rep] += 1

tot_fvm_uscite = sum(v['FVM'] for v in st.session_state.tutti_venduti if v.get('FVM', 0) > 0)
tot_spesa_uscite = sum(v['Prezzo'] for v in st.session_state.tutti_venduti)
coeff_inflazione = (tot_spesa_uscite / tot_fvm_uscite) if tot_fvm_uscite > 0 else 1.0

# --- HEADER & SIDEBAR ---
col_head1, col_head2 = st.columns([4, 1])
with col_head1:
    st.title("⚽ Fanta Copilot - Dashboard Mantra")
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

st.sidebar.metric(label="Budget Rimanente", value=f"{budget_rimanente} cr", delta=f"-{spesa_totale} cr spesi")
st.sidebar.metric(label="Rilancio MAX Assoluto", value=f"{rilancio_massimo} cr")

st.sidebar.divider()
st.sidebar.subheader("📁 File caricati da GitHub")
st.sidebar.caption("L'app legge in automatico i file dalla repo. Puoi sostituirli qui:")
file_caricato_m = st.sidebar.file_uploader("Sostituisci Quotazioni (.xlsx/.csv)", type=["xlsx", "csv"], key="u_main")
file_caricato_s = st.sidebar.file_uploader("Sostituisci Fasce/Tit/Rig (.xlsx/.csv)", type=["xlsx", "csv"], key="u_sec")

# ==========================================
# 📑 GESTIONE DELLE TABS (ORA 4 TABS)
# ==========================================
tab_asta, tab_rosa, tab_venduti, tab_moduli = st.tabs([
    "🔍 Listone & Asta", 
    "📋 La Mia Rosa", 
    "🤝 Tutti i Venduti", 
    "🧩 Analizzatore Moduli"
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

        # ==========================================
        # 💬 POPUP DIALOG NATIVO (GESTIONE CHIAMATA)
        # ==========================================
        @st.dialog("⚡ Gestione Asta")
        def mostra_modal_chiamata(g_sel):
            gn = g_sel[nome_col]
            grm = str(g_sel[rm_col])
            gsq = str(g_sel[squadra_col])[:3].upper() if squadra_col in g_sel else "-"
            v_base = float(g_sel[fvm_col]) if (fvm_col and pd.notna(g_sel[fvm_col])) else 1.0
            p_stim = max(1, round(v_base * coeff_inflazione))

            st.markdown(f"### **{gn}** ({gsq} - `{grm}`) ")
            st.caption(f"Valore FVM M: **{int(v_base)}** | Prezzo Consigliato: **{p_stim} cr**")
            
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
        # 🔍 TAB 1: LISTONE A-Z & ASTA
        # ------------------------------------------
        with tab_asta:
            col_f1, col_f2, col_f3, col_f4 = st.columns([2, 2, 2, 1])
            with col_f1:
                macro_reparto = st.selectbox("🛡️ Reparto:", options=["Tutti", "Portieri", "Difensori", "Centrocampisti", "Trequartisti/Attaccanti"])
            with col_f2:
                ruolo_specifico = st.selectbox("🎯 Ruolo Mantra:", options=LISTA_RUOLI_MANTRA)
            with col_f3:
                cerca_nome = st.text_input("🔎 Cerca Nome:")
            with col_f4:
                mostra_anche_venduti = st.checkbox("👁️ Mostra Venduti", value=False)

            df_filtrato = df.copy() if mostra_anche_venduti else df[~df[nome_col].isin(nomi_venduti_totali)].copy()

            if macro_reparto != "Tutti" and rm_col in df_filtrato.columns:
                ruoli_target = MAPPA_REPARTI[macro_reparto]
                pattern_reparto = r'\b(' + '|'.join(ruoli_target) + r')\b'
                df_filtrato = df_filtrato[df_filtrato[rm_col].astype(str).str.contains(pattern_reparto, case=False, regex=True, na=False)]

            if ruolo_specifico != "Tutti" and rm_col in df_filtrato.columns:
                pattern_ruolo = r'\b' + re.escape(ruolo_specifico) + r'\b'
                df_filtrato = df_filtrato[df_filtrato[rm_col].astype(str).str.contains(pattern_ruolo, case=False, regex=True, na=False)]

            if cerca_nome and nome_col in df_filtrato.columns:
                df_filtrato = df_filtrato[df_filtrato[nome_col].astype(str).str.contains(cerca_nome, case=False, na=False)]

            # ORDINAMENTO ALFABETICO A-Z
            if nome_col in df_filtrato.columns:
                df_filtrato = df_filtrato.sort_values(by=nome_col, key=lambda col: col.astype(str).str.lower(), ascending=True)

            df_filtrato = df_filtrato.head(40)
            st.write(f"Mostrando **{len(df_filtrato)}** giocatori (in ordine alfabetico A-Z):")

            for _, row in df_filtrato.iterrows():
                g_nome = row[nome_col]
                g_rm = str(row[rm_col]) if rm_col in row else "N/A"
                g_squadra = str(row[squadra_col])[:3].upper() if squadra_col in row else "SER"
                
                val_fvm = int(row[fvm_col]) if (fvm_col and pd.notna(row[fvm_col])) else 1
                val_qta = int(row[qta_col]) if (qta_col and pd.notna(row[qta_col])) else None

                tit_val = int(row[tit_col]) if (tit_col and pd.notna(row[tit_col])) else 3
                tit_val = min(max(tit_val, 1), 5)
                stelle = "★" * tit_val + "☆" * (5 - tit_val)

                tags_list = []
                if val_qta is not None:
                    tags_list.append(f"Qt.a {val_qta}")
                if fascia_col and pd.notna(row[fascia_col]) and str(row[fascia_col]).strip() not in ['-', '']:
                    tags_list.append(str(row[fascia_col]).strip())
                if rig_col and pd.notna(row[rig_col]) and str(row[rig_col]).strip().upper() in ['⚽', 'SI', '1', 'RIGORISTA', 'RIG']:
                    tags_list.append("Rig")
                if note_col and pd.notna(row[note_col]) and str(row[note_col]).strip() not in ['-', '']:
                    tags_list.extend([t.strip() for t in str(row[note_col]).split(',')])

                tags_html = "".join([f'<span class="tag-pill">{t}</span> ' for t in tags_list])
                col_bg = get_ruolo_colore(g_rm)
                
                stato_tag = ""
                if g_nome in miei_nomi:
                    stato_tag = f'<span class="tag-pill" style="background:#0055ff; color:white;">MIO ({miei_nomi[g_nome]} cr)</span>'
                elif g_nome in venduti_dict:
                    stato_tag = f'<span class="tag-pill" style="background:#e74c3c; color:white;">VENDUTO ({venduti_dict[g_nome]} cr)</span>'

                col_card, col_btn = st.columns([5, 1])

                with col_card:
                    card_html = f"""<div class="player-card">
<div class="player-left">
<div class="role-badge-circle" style="background-color: {col_bg};">{g_rm[:4]}</div>
<div>
<div style="display:flex; align-items:center; gap:8px;">
<span class="team-pill">{g_squadra}</span>
<span class="tit-pill">{stelle}</span>
{stato_tag}
</div>
<div style="font-size:18px; font-weight:700; margin:2px 0;">{g_nome}</div>
<div style="display:flex; gap:5px; margin-top:3px;">{tags_html}</div>
</div>
</div>
<div class="fvm-box">
<div class="fvm-val">{val_fvm}</div>
<div class="fvm-label">FVM M</div>
</div>
</div>"""
                    st.markdown(card_html, unsafe_allow_html=True)

                with col_btn:
                    if st.button("⚡ Chiama", key=f"btn_chiama_{g_nome}"):
                        mostra_modal_chiamata(row.to_dict())

        # ------------------------------------------
        # 📋 TAB 2: LA MIA ROSA (CON OPZIONE ANNULLA)
        # ------------------------------------------
        with tab_rosa:
            st.subheader("📋 La Mia Rosa")
            if st.session_state.rosa:
                df_rosa = pd.DataFrame(st.session_state.rosa)
                st.dataframe(df_rosa, use_container_width=True)
                
                st.divider()
                st.markdown("### 🗑️ Correggi Errore (Svincola/Annulla Acquisto)")
                st.caption("Hai assegnato un giocatore per sbaglio o a un prezzo errato? Annullalo da qui e tornerà nel listone.")
                
                col_del_r1, col_del_r2 = st.columns([3, 1])
                with col_del_r1:
                    lista_miei = sorted([p["Nome"] for p in st.session_state.rosa])
                    giocatore_da_rimuovere = st.selectbox("Seleziona il tuo giocatore da annullare:", options=lista_miei, key="sel_del_mio")
                with col_del_r2:
                    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                    if st.button("❌ Annulla Acquisto", type="primary", key="btn_del_mio"):
                        rimuovi_giocatore(giocatore_da_rimuovere)

                st.divider()
                st.subheader("📊 Riepilogo Rosa e Spesa")
                c_r1, c_r2, c_r3, c_r4 = st.columns(4)
                for i, (rep_nome, max_s) in enumerate(LIMITI.items()):
                    p_rep = [p for p in st.session_state.rosa if get_reparto(p['RM']) == rep_nome]
                    spesa_rep = sum(p['Prezzo'] for p in p_rep)
                    col_target = [c_r1, c_r2, c_r3, c_r4][i]
                    col_target.metric(f"{rep_nome}", f"{len(p_rep)} / {max_s}", f"{spesa_rep} cr spesi")
            else:
                st.info("Nessun giocatore acquistato finora. Acquista i tuoi giocatori dalla scheda Listone!")

        # ------------------------------------------
        # ------------------------------------------
        # 🤝 TAB 3: TUTTI I VENDUTI (ROSA GENERALE)
        # ------------------------------------------
        with tab_venduti:
            st.subheader("🤝 Riepilogo Generale Venduti")
            st.caption("Qui puoi vedere tutti i giocatori assegnati in lega (tuoi e degli altri manager).")
            
            if st.session_state.tutti_venduti:
                df_venduti = pd.DataFrame(st.session_state.tutti_venduti)
                colonne_mostrate = ["Nome", "Squadra", "RM", "Prezzo", "Mio"]
                st.dataframe(df_venduti[[c for c in colonne_mostrate if c in df_venduti.columns]], use_container_width=True)
                
                st.divider()
                st.markdown("### 🗑️ Correggi Errore Globale")
                st.caption("Filtra inserendo le iniziali del giocatore per aggiornare subito il menu a tendina.")
                
                # 1. Campo per inserire le iniziali o parte del nome
                cerca_venduto = st.text_input("🔎 Filtra per iniziali o nome:", key="search_venduti", placeholder="Es. Laut, Kva, Dy...")

                # 2. Estrazione e filtraggio dinamico della lista dei 300 venduti
                lista_tutti = sorted([v["Nome"] for v in st.session_state.tutti_venduti])
                if cerca_venduto:
                    lista_tutti = [n for n in lista_tutti if cerca_venduto.lower() in n.lower()]

                # 3. Menu a tendina e pulsante di annullamento
                if lista_tutti:
                    col_del_v1, col_del_v2 = st.columns([3, 1])
                    with col_del_v1:
                        giocatore_da_rimuovere_v = st.selectbox(
                            "Seleziona giocatore dal menu a tendina:", 
                            options=lista_tutti, 
                            key="sel_del_tutti"
                        )
                    with col_del_v2:
                        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                        if st.button("❌ Annulla Acquisto", type="primary", key="btn_del_tutti"):
                            rimuovi_giocatore(giocatore_da_rimuovere_v)
                else:
                    st.warning("⚠️ Nessun giocatore venduto corrisponde alle lettere digitate.")
            else:
                st.info("Nessun giocatore è stato ancora venduto in questa sessione d'asta.")

        # ------------------------------------------
        # 🧩 TAB 4: ANALIZZATORE MODULI MANTRA
        # ------------------------------------------
        with tab_moduli:
            st.subheader("🧩 Analizzatore Moduli e Copertura Rosa Mantra")
            st.caption("Verifica quali moduli puoi schierare in base ai giocatori attualmente acquistati nella tua rosa.")
            
            if not st.session_state.rosa:
                st.warning("⚠️ Non hai ancora acquistato nessun giocatore. Fai acquisti per sbloccare l'analisi dei moduli!")
            else:
                ruoli_disponibili = {}
                for r in LISTA_RUOLI_MANTRA[1:]:
                    ruoli_disponibili[r] = []

                for p in st.session_state.rosa:
                    rm_tokens = [t.strip().upper() for t in re.split(r'[;,/\s]+', str(p.get('RM', '')))]
                    for r_tok in rm_tokens:
                        if r_tok in ruoli_disponibili:
                            ruoli_disponibili[r_tok].append(p['Nome'])

                st.markdown("### 🎴 Giocatori Disponibili per Ruolo")
                cols_r = st.columns(len(ruoli_disponibili))
                for idx, (ruolo_k, lista_p) in enumerate(ruoli_disponibili.items()):
                    with cols_r[idx]:
                        col_c = get_ruolo_colore(ruolo_k)
                        st.markdown(f"<div style='text-align:center; background-color:{col_c}; color:white; font-weight:bold; border-radius:6px; padding:2px;'>{ruolo_k}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='text-align:center; font-size:18px; font-weight:800;'>{len(lista_p)}</div>", unsafe_allow_html=True)

                st.divider()
                st.markdown("### 📐 Verificatore di Modulo (11 Titolari)")

                def verifica_schema(schema_reqs, giocatori_rosa):
                    p_parsed = []
                    for p in giocatori_rosa:
                        tokens = set([t.strip().upper() for t in re.split(r'[;,/\s]+', str(p.get('RM', '')))])
                        p_parsed.append({'Nome': p['Nome'], 'Ruoli': tokens})

                    usati = set()
                    
                    def solve(slot_idx):
                        if slot_idx == len(schema_reqs):
                            return True
                        opzioni_ruolo = schema_reqs[slot_idx]
                        for idx_p, p in enumerate(p_parsed):
                            if idx_p not in usati:
                                if any(r in p['Ruoli'] for r in opzioni_ruolo):
                                    usati.add(idx_p)
                                    if solve(slot_idx + 1):
                                        return True
                                    usati.remove(idx_p)
                        return False

                    slot_coperti = 0
                    test_usati = set()
                    for opzioni_ruolo in schema_reqs:
                        trovato = False
                        for idx_p, p in enumerate(p_parsed):
                            if idx_p not in test_usati and any(r in p['Ruoli'] for r in opzioni_ruolo):
                                test_usati.add(idx_p)
                                slot_coperti += 1
                                trovato = True
                                break
                    
                    completo = solve(0)
                    return completo, slot_coperti

                res_moduli = []
                for mod_nome, reqs in SCHEMI_MANTRA.items():
                    is_ok, n_coperti = verifica_schema(reqs, st.session_state.rosa)
                    res_moduli.append({
                        "Modulo": mod_nome,
                        "Status": "🟢 GIOCABILE" if is_ok else ("🟡 PARZIALE" if n_coperti >= 8 else "🔴 INCOMPLETO"),
                        "Titolari Coperti": f"{n_coperti} / 11",
                        "Giocabile": is_ok
                    })

                col_m1, col_m2 = st.columns([2, 3])
                
                with col_m1:
                    df_mod = pd.DataFrame(res_moduli)
                    st.dataframe(df_mod[["Modulo", "Status", "Titolari Coperti"]], use_container_width=True, hide_index=True)

                with col_m2:
                    moduli_ok = [m["Modulo"] for m in res_moduli if m["Giocabile"]]
                    if moduli_ok:
                        st.success(f"🎉 **Puoi schierare i seguenti moduli completi:** {', '.join(moduli_ok)}")
                    else:
                        st.info("💡 Nessun modulo ha ancora 11 titolari coperti. Continua l'asta per completare la tua formazione!")

    except Exception as e:
        st.error(f"Errore nella lettura dei dati: {e}")

salva_backup()
