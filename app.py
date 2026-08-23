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
        overscroll-behavior-y: contain !important;
        background-color: #0e1117;
    }
    
    .player-card {
        background-color: #161a23;
        border: 1px solid #282e3d;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: white;
    }
    
    .player-left {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    
    .role-badge-circle {
        width: 44px;
        height: 44px;
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
    
    .tag-pill {
        background-color: #232936;
        color: #a0aec0;
        font-size: 11px;
        padding: 3px 8px;
        border-radius: 6px;
        border: 1px solid #323b4e;
    }
    
    .fvm-box {
        background-color: #1d6bf3;
        color: white;
        border-radius: 8px;
        padding: 6px 12px;
        text-align: center;
        min-width: 75px;
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
# 💾 GESTIONE BACKUP
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
if 'giocatore_selezionato' not in st.session_state:
    st.session_state.giocatore_selezionato = None

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

def get_ruolo_colore(rm_str):
    rm_upper = str(rm_str).upper()
    if any(r in rm_upper for r in ['PC', 'A', 'W']):
        return '#e74c3c'  # Rosso (Attacco)
    elif any(r in rm_upper for r in ['T', 'C', 'M', 'E']):
        return '#2980b9'  # Blu (Centrocampo)
    elif any(r in rm_upper for r in ['DD', 'DS', 'DC', 'B']):
        return '#27ae60'  # Verde (Difesa)
    return '#f39c12'      # Giallo (Porta)

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

def carica_df_principale(file_caricato_user):
    if file_caricato_user is not None:
        return leggi_file_intelligente(file_caricato_user)
    
    possibili_nomi = [
        "Quotazioni_Fantacalcio_Stagione_2026_27.xlsx",
        "Quotazioni_Fantacalcio_Stagione_2026_27.csv",
        "Listone.xlsx", "Quotazioni.xlsx"
    ]
    for nome in possibili_nomi:
        if os.path.exists(nome):
            df_loc = leggi_file_intelligente(nome)
            if df_loc is not None:
                return df_loc

    try:
        for f in os.listdir("."):
            f_lower = f.lower()
            if (f_lower.startswith("quotazioni") or f_lower.startswith("listone")) and (f_lower.endswith(".xlsx") or f_lower.endswith(".csv")):
                df_loc = leggi_file_intelligente(f)
                if df_loc is not None:
                    return df_loc
    except Exception:
        pass
    return None

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
file_caricato = st.sidebar.file_uploader("📁 Carica Quotazioni (.xlsx/.csv)", type=["xlsx", "csv"])

tab_asta, tab_rosa, tab_moduli = st.tabs(["🔍 Listone A-Z & Asta", "📋 La Mia Rosa", "🧩 Analizzatore Moduli Mantra"])

df = carica_df_principale(file_caricato)

if df is not None:
    try:
        colonne = list(df.columns)
        nome_col = next((c for c in colonne if str(c).lower() in ['nome', 'calciatore']), 'Nome')
        rm_col = next((c for c in colonne if str(c).upper() == 'RM'), 'RM')
        squadra_col = next((c for c in colonne if str(c).lower() in ['squadra', 'club']), 'Squadra')
        
        valore_col = next((c for c in colonne if str(c).lower() in ['fvm m', 'fvm_m', 'fvm mantra', 'fvm', 'qt.a m', 'qt.a']), None)
        tit_col = next((c for c in colonne if str(c).lower() in ['titolarità', 'titolarita', 'tit', 'status']), None)
        fascia_col = next((c for c in colonne if str(c).lower() in ['fascia', 'fasce', 'tier']), None)
        rig_col = next((c for c in colonne if str(c).lower() in ['rigorista', 'rigoristi', 'rig']), None)

        miei_nomi = {p['Nome']: p['Prezzo'] for p in st.session_state.rosa}
        venduti_dict = {v['Nome']: v['Prezzo'] for v in st.session_state.tutti_venduti if not v.get('Mio', False)}

        nomi_venduti_totali = list(miei_nomi.keys()) + list(venduti_dict.keys())
        
        with tab_asta:
            col_f1, col_f2, col_f3, col_f4 = st.columns([2, 2, 2, 1])
            with col_f1:
                macro_reparto = st.selectbox("🛡️ Reparto:", options=["Tutti", "Portieri", "Difensori", "Centrocampisti", "Trequartisti/Attaccanti"])
            with col_f2:
                ruolo_specifico = st.selectbox("🎯 Ruolo Mantra:", options=LISTA_RUOLI_MANTRA)
            with col_f3:
                cerca_nome = st.text_input("🔎 Cerca Nome:")
            with col_f4:
                mostra_anche_venduti = st.checkbox("👁️ Venduti", value=False)

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

            df_filtrato = df_filtrato.head(40)

            st.write(f"Mostrando **{len(df_filtrato)}** giocatori:")

            for _, row in df_filtrato.iterrows():
                g_nome = row[nome_col]
                g_rm = str(row[rm_col]) if rm_col in row else "N/A"
                g_squadra = str(row[squadra_col])[:3].upper() if squadra_col in row else "SER"
                val_fvm = int(row[valore_col]) if (valore_col and pd.notna(row[valore_col])) else 1
                
                tit_val = int(row[tit_col]) if (tit_col and pd.notna(row[tit_col])) else 3
                stelle = "★" * min(max(tit_val, 1), 5)

                tags_html = ""
                if fascia_col and pd.notna(row[fascia_col]) and str(row[fascia_col]) != '-':
                    tags_html += f'<span class="tag-pill">{row[fascia_col]}</span> '
                if rig_col and pd.notna(row[rig_col]) and str(row[rig_col]) in ['⚽', 'SI', '1']:
                    tags_html += '<span class="tag-pill">Rigorista</span> '

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
<span style="font-size:11px; color:#f1c40f;">{stelle}</span>
{stato_tag}
</div>
<div style="font-size:18px; font-weight:700; margin:2px 0;">{g_nome}</div>
<div style="display:flex; gap:5px; margin-top:3px;">{tags_html}</div>
</div>
</div>
<div class="fvm-box">
<div class="fvm-val">{val_fvm}</div>
<div class="fvm-label">MANTRA</div>
</div>
</div>"""
                    st.markdown(card_html, unsafe_allow_html=True)

                with col_btn:
                    if st.button("⚡ Chiama", key=f"btn_{g_nome}"):
                        st.session_state.giocatore_selezionato = row.to_dict()

            if st.session_state.giocatore_selezionato:
                st.divider()
                g_sel = st.session_state.giocatore_selezionato
                gn = g_sel[nome_col]
                grm = g_sel[rm_col]
                gsq = g_sel[squadra_col] if squadra_col in g_sel else "-"
                v_base = float(g_sel[valore_col]) if (valore_col and pd.notna(g_sel[valore_col])) else 1
                p_stim = max(1, round(v_base * coeff_inflazione))
                rep_g = get_reparto(grm)

                st.markdown(f"### ⚡ Gestione Asta per: **{gn}** ({gsq} - {grm})")
                
                col_i1, col_i2 = st.columns([2, 1])
                with col_i1:
                    prezzo_input = st.number_input("Prezzo Finale d'Asta:", min_value=1, value=int(p_stim), key="p_input_scheda")
                
                with col_i2:
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button("✅ ACQUISTA (MIO)", type="primary", use_container_width=True):
                            st.session_state.rosa.append({"Nome": gn, "Squadra": gsq, "RM": grm, "Prezzo": prezzo_input})
                            st.session_state.tutti_venduti.append({"Nome": gn, "FVM": v_base, "Prezzo": prezzo_input, "Mio": True})
                            st.session_state.giocatore_selezionato = None
                            salva_backup()
                            st.rerun()
                    with col_b2:
                        if st.button("📌 VENDUTO AD ALTRI", use_container_width=True):
                            st.session_state.tutti_venduti.append({"Nome": gn, "FVM": v_base, "Prezzo": prezzo_input, "Mio": False})
                            st.session_state.giocatore_selezionato = None
                            salva_backup()
                            st.rerun()

        with tab_rosa:
            st.subheader("📋 La Mia Rosa")
            if st.session_state.rosa:
                st.dataframe(pd.DataFrame(st.session_state.rosa), use_container_width=True)
            else:
                st.info("Nessun giocatore acquistato.")

    except Exception as e:
        st.error(f"Errore nella lettura dei dati: {e}")

salva_backup()
