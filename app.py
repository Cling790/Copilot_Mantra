import streamlit as st
import pandas as pd
import re
import os
st.set_page_config(page_title="Fanta Copilot Mantra 2026/27", layout="wide")

# ==========================================
# 🔐 CONFIGURAZIONE SICUREZZA / ACCESSO
# ==========================================
PASSWORD_CORRETTA = "Pf703.d-s"  # <-- CAMBIA QUI LA TUA PASSWORD PERSONALE!

if 'autenticato' not in st.session_state:
    st.session_state.autenticato = False

if not st.session_state.autenticato:
    st.title("🔐 Accesso Riservato - Fanta Copilot")
    st.info("Questa applicazione è ad accesso privato. Inserisci la password per accedere alla tua dashboard d'asta.")
    
    col_pwd1, col_pwd2 = st.columns([2, 1])
    with col_pwd1:
        pwd_input = st.text_input("Password di sblocco:", type="password", key="pwd_field")
    
    if st.button("🔓 Accedi all'App", type="primary"):
        if pwd_input == PASSWORD_CORRETTA:
            st.session_state.autenticato = True
            st.success("Accesso autorizzato!")
            st.rerun()
        else:
            st.error("❌ Password errata! Contatta l'amministratore per richiedere il codice di accesso.")
    
    st.stop()  # FERMA L'ESECUZIONE DEL CODICE FINCHÉ NON SI È AUTENTICATI

# ==========================================
# ⚽ INIZIO APPLICAZIONE FANTA COPILOT
# ==========================================

if 'rosa' not in st.session_state:
    st.session_state.rosa = []

if 'tutti_venduti' not in st.session_state:
    st.session_state.tutti_venduti = []

MAPPA_REPARTI = {
    'Portieri': ['POR', 'P'],
    'Difensori': ['DD', 'DS', 'DC', 'B'],
    'Centrocampisti': ['E', 'M', 'C'],
    'Trequartisti/Attaccanti': ['W', 'T', 'A', 'PC']
}

LISTA_RUOLI_MANTRA = ["Tutti", "POR", "DD", "DS", "DC", "B", "E", "M", "C", "W", "T", "A", "PC"]

# DIZIONARI DI CONVERSIONE Dati -> Tabella / Scheda
MAPPA_TITOLARITA = {
    1: "🔴 1 - Non gioca mai",
    2: "🔴 2 - Subentra raramente",
    3: "🟡 3 - Nelle rotazioni",
    4: "🟢 4 - Titolare con concorrenza",
    5: "❇️ 5 - Titolare inamovibile"
}

MAPPA_FASCE_SHORT = {
    'TOP': 'T', 'T': 'T',
    'SEMI-TOP': 'ST', 'SEMITOP': 'ST', 'ST': 'ST',
    'TERZA': 'TX', '3A': 'TX', 'TX': 'TX', '3': 'TX',
    'QUARTA': '4', '4A': '4', '4': '4',
    'SCOMMESSA': 'SC', 'SCOM': 'SC', 'SC': 'SC'
}

MAPPA_FASCE_LONG = {
    'T': '🌟 TOP',
    'ST': '⭐ SEMI-TOP',
    'TX': '🥉 TERZA FASCIA',
    '4': '4️⃣ QUARTA FASCIA',
    'SC': '🎲 SCOMMESSA'
}

def normalizza_fascia_breve(val):
    if pd.isna(val) or str(val).strip() == '':
        return '-'
    v = str(val).strip().upper()
    return MAPPA_FASCE_SHORT.get(v, v)

def normalizza_rigorista_breve(val):
    if pd.isna(val) or str(val).strip() in ['', '-', '0', 'NO', 'no', 'False', 'false']:
        return '-'
    v = str(val).strip()
    if v.upper() in ['SI', 'SÌ', 'YES', '1', 'TRUE', 'RIGORISTA']:
        return '⚽'
    return v

def get_reparto(rm_str):
    rm_str = str(rm_str).upper()
    tokens = re.findall(r'\b[A-Z]+\b', rm_str)
    for reparto, ruoli in MAPPA_REPARTI.items():
        if any(r in tokens for r in ruoli):
            return reparto
    return 'Altri'

LIMITI = {
    'Portieri': 4,
    'Difensori': 9,
    'Centrocampisti': 9,
    'Trequartisti/Attaccanti': 10
}
SLOT_TOTALI = sum(LIMITI.values())

reparti_count = {'Portieri': 0, 'Difensori': 0, 'Centrocampisti': 0, 'Trequartisti/Attaccanti': 0}
for p in st.session_state.rosa:
    rep = get_reparto(p['RM'])
    if rep in reparti_count:
        reparti_count[rep] += 1

# CALCOLO INFLAZIONE / DEFLAZIONE MERCATO
tot_fvm_uscite = sum(v['FVM'] for v in st.session_state.tutti_venduti if v['FVM'] > 0)
tot_spesa_uscite = sum(v['Prezzo'] for v in st.session_state.tutti_venduti)
coeff_inflazione = (tot_spesa_uscite / tot_fvm_uscite) if tot_fvm_uscite > 0 else 1.0

# --- INTESTAZIONE APP ---
col_head1, col_head2 = st.columns([4, 1])
with col_head1:
    st.title("⚽ Fanta Copilot - Dashboard Mantra 2026/27")
with col_head2:
    if st.button("🔒 Esci / Blocco App"):
        st.session_state.autenticato = False
        st.rerun()

# --- BARRA LATERALE ---
st.sidebar.header("⚙️ Configurazione Asta")

budget_iniziale = st.sidebar.number_input("Budget iniziale:", value=1000, step=10)
spesa_totale = sum(p['Prezzo'] for p in st.session_state.rosa)
budget_rimanente = budget_iniziale - spesa_totale
giocatori_mancanti = SLOT_TOTALI - len(st.session_state.rosa)

rilancio_massimo = budget_rimanente - (giocatori_mancanti - 1) if giocatori_mancanti > 0 else 0

st.sidebar.metric(label="Budget Rimanente", value=f"{budget_rimanente} cr", delta=f"-{spesa_totale} cr spesi")
st.sidebar.metric(label="Rilancio MAX Assoluto", value=f"{rilancio_massimo} cr")

var_pct = (coeff_inflazione - 1.0) * 100
if var_pct > 2:
    st.sidebar.metric(label="🔥 Trend Asta", value=f"+{var_pct:.1f}%", delta="Mercato Caldo")
elif var_pct < -2:
    st.sidebar.metric(label="❄️ Trend Asta", value=f"{var_pct:.1f}%", delta="Mercato Freddo")
else:
    st.sidebar.metric(label="⚖️ Trend Asta", value="In Linea", delta="Prezzi stabili")

st.sidebar.divider()

st.sidebar.subheader("📊 Limiti Reparti")
for rep, max_val in LIMITI.items():
    curr = reparti_count[rep]
    mancanti = max_val - curr
    st.sidebar.write(f"**{rep}**: {curr}/{max_val} (Mancano: **{mancanti}**)")
    st.sidebar.progress(min(curr / max_val, 1.0))

st.sidebar.divider()
st.sidebar.subheader("📁 Caricamento File")
file_caricato = st.sidebar.file_uploader("1. Listone Principale (.xlsx/.csv)", type=["xlsx", "csv"])
file_titolarita = st.sidebar.file_uploader("2. File Note / Titolarità / Fasce / Rigoristi", help="Excel con colonne: Nome, Titolarità (1-5), Fascia, Rigorista")

tab_asta, tab_rosa, tab_moduli = st.tabs(["🔍 Listone A-Z & Asta", "📋 La Mia Rosa", "🧩 Analizzatore Moduli Mantra"])

if file_caricato is not None:
    try:
        if file_caricato.name.endswith('.xlsx'):
            df = pd.read_excel(file_caricato, header=1)
        else:
            df = pd.read_csv(file_caricato)

        df.columns = [str(col).strip() for col in df.columns]
        colonne = list(df.columns)
        
        nome_col = next((c for c in colonne if c.lower() in ['nome', 'calciatore']), 'Nome')
        r_col = next((c for c in colonne if c.upper() == 'R'), 'R')
        rm_col = next((c for c in colonne if c.upper() == 'RM'), 'RM')
        squadra_col = next((c for c in colonne if c.lower() in ['squadra', 'club']), 'Squadra')
        
        valore_col = next((c for c in colonne if c.lower() in ['fvm m', 'fvm_m', 'fvm mantra', 'fvm', 'prezzo medio', 'pm']), None)
        if not valore_col:
            valore_col = next((c for c in colonne if c.lower() in ['qt.a m', 'qt.a', 'quotazione']), None)

        tit_col = next((c for c in colonne if c.lower() in ['titolarità', 'titolarita', 'tit', 'status']), None)
        fascia_col = next((c for c in colonne if c.lower() in ['fascia', 'fasce', 'tier']), None)
        rig_col = next((c for c in colonne if c.lower() in ['rigorista', 'rigoristi', 'rig']), None)

       # UNIONE SECONDO FILE (TITOLARITÀ, FASCE, RIGORISTI)
        df_tit = None
        if file_titolarita is not None:
            try:
                if file_titolarita.name.endswith('.xlsx'):
                    df_tit = pd.read_excel(file_titolarita)
                else:
                    df_tit = pd.read_csv(file_titolarita)
            except Exception as ex_tit:
                st.sidebar.error(f"Errore nel file caricato: {ex_tit}")
        elif os.path.exists("FASCE_TIT_RIG.xlsx"):
            # Se non carichi nulla a mano, usa in automatico il file presente su GitHub!
            df_tit = pd.read_excel("FASCE_TIT_RIG.xlsx")

        if df_tit is not None:
            try:
                df_tit.columns = [str(c).strip() for c in df_tit.columns]
                col_tit_nome = next((c for c in df_tit.columns if c.lower() in ['nome', 'calciatore']), df_tit.columns[0])
                
                col_tit_val = next((c for c in df_tit.columns if c.lower() in ['titolarità', 'titolarita', 'tit', 'status', 'voto']), None)
                col_fascia_val = next((c for c in df_tit.columns if c.lower() in ['fascia', 'fasce', 'tier']), None)
                col_rig_val = next((c for c in df_tit.columns if c.lower() in ['rigorista', 'rigoristi', 'rig']), None)

                cols_to_use = [col_tit_nome]
                if col_tit_val: cols_to_use.append(col_tit_val)
                if col_fascia_val: cols_to_use.append(col_fascia_val)
                if col_rig_val: cols_to_use.append(col_rig_val)

                df_tit_clean = df_tit[cols_to_use].drop_duplicates(subset=[col_tit_nome]).copy()
                
                rename_dict = {col_tit_nome: '_Nome_Match_'}
                if col_tit_val: rename_dict[col_tit_val] = 'Titolarità'
                if col_fascia_val: rename_dict[col_fascia_val] = 'Fascia'
                if col_rig_val: rename_dict[col_rig_val] = 'Rigorista'
                
                df_tit_clean.rename(columns=rename_dict, inplace=True)
                
                df = pd.merge(df, df_tit_clean, left_on=nome_col, right_on='_Nome_Match_', how='left')
                if '_Nome_Match_' in df.columns:
                    df.drop(columns=['_Nome_Match_'], inplace=True)
                
                if 'Titolarità' in df.columns: tit_col = 'Titolarità'
                if 'Fascia' in df.columns: fascia_col = 'Fascia'
                if 'Rigorista' in df.columns: rig_col = 'Rigorista'

            except Exception as ex_tit:
                st.sidebar.error(f"Errore nella lettura note/titolarità: {ex_tit}")

        miei_nomi = {p['Nome']: p['Prezzo'] for p in st.session_state.rosa}
        venduti_dict = {v['Nome']: v['Prezzo'] for v in st.session_state.tutti_venduti if not v.get('Mio', False)}

        def calcola_stato(nome):
            if nome in miei_nomi:
                return f"🔵 MIO ({miei_nomi[nome]} cr)"
            elif nome in venduti_dict:
                return f"🔴 VENDUTO ({venduti_dict[nome]} cr)"
            return "🟢 LIBERO"

        df['Stato'] = df[nome_col].apply(calcola_stato)

        # Pulizia e formattazione per la TABELLA
        if tit_col and tit_col in df.columns:
            df[tit_col] = pd.to_numeric(df[tit_col], errors='coerce').fillna(0).astype(int)

        if fascia_col and fascia_col in df.columns:
            df[fascia_col] = df[fascia_col].apply(normalizza_fascia_breve)

        if rig_col and rig_col in df.columns:
            df[rig_col] = df[rig_col].apply(normalizza_rigorista_breve)

        # Ordine colonne: Stato, Tit, Fascia, Rigorista, Nome, restanti
        cols_base = ['Stato']
        if tit_col and tit_col in df.columns: cols_base.append(tit_col)
        if fascia_col and fascia_col in df.columns: cols_base.append(fascia_col)
        if rig_col and rig_col in df.columns: cols_base.append(rig_col)
        
        cols_order = cols_base + [c for c in df.columns if c not in cols_base]
        df = df[cols_order].sort_values(by=nome_col, ascending=True)

        nomi_venduti_totali = list(miei_nomi.keys()) + list(venduti_dict.keys())
        df_disponibili = df[~df[nome_col].isin(nomi_venduti_totali)].copy()

        with tab_asta:
            st.subheader("🎯 Filtri Chiamata & Ruoli")
            col_f1, col_f2, col_f3, col_f4 = st.columns([2, 2, 2, 1])

            with col_f1:
                macro_reparto = st.selectbox("🛡️ Macro-Reparto:", options=["Tutti", "Portieri", "Difensori", "Centrocampisti", "Trequartisti/Attaccanti"])
            with col_f2:
                ruolo_specifico = st.selectbox("🎯 Ruolo Mantra Specifico:", options=LISTA_RUOLI_MANTRA)
            with col_f3:
                cerca_nome = st.text_input("🔎 Cerca Nome o Ruolo:")
            with col_f4:
                mostra_anche_venduti = st.checkbox("👁️ Venduti", value=False)

            df_filtrato = df.copy() if mostra_anche_venduti else df_disponibili.copy()

            # Filtro 1: Macro Reparto
            if macro_reparto != "Tutti" and rm_col in df_filtrato.columns:
                ruoli_target = MAPPA_REPARTI[macro_reparto]
                pattern_reparto = r'\b(' + '|'.join(ruoli_target) + r')\b'
                df_filtrato = df_filtrato[df_filtrato[rm_col].astype(str).str.contains(pattern_reparto, case=False, regex=True, na=False)]

            # Filtro 2: Ruolo Mantra Specifico (es. DD, DC, E...)
            if ruolo_specifico != "Tutti" and rm_col in df_filtrato.columns:
                pattern_ruolo = r'\b' + re.escape(ruolo_specifico) + r'\b'
                df_filtrato = df_filtrato[df_filtrato[rm_col].astype(str).str.contains(pattern_ruolo, case=False, regex=True, na=False)]

            # Filtro 3: Ricerca per Testo
            if cerca_nome and nome_col in df_filtrato.columns:
                mask_nome = df_filtrato[nome_col].astype(str).str.contains(cerca_nome, case=False, na=False)
                mask_rm = df_filtrato[rm_col].astype(str).str.contains(cerca_nome, case=False, na=False) if rm_col in df_filtrato.columns else False
                df_filtrato = df_filtrato[mask_nome | mask_rm]

            df_filtrato = df_filtrato.sort_values(by=nome_col, ascending=True)

            st.info("👇 **TOCCA UN GIOCATORE SULLA TABELLA** per aprire la scheda d'acquisto:")

            event = st.dataframe(
                df_filtrato,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row"
            )

            selected_rows = event.selection.rows if (hasattr(event, 'selection') and event.selection) else []

            if selected_rows:
                st.divider()
                idx_sel = selected_rows[0]
                if idx_sel < len(df_filtrato):
                    info_g = df_filtrato.iloc[idx_sel]
                    g_nome = info_g[nome_col]
                    g_rm = info_g[rm_col]
                    g_squadra = info_g[squadra_col] if squadra_col in df.columns else "-"
                    valore_base = float(info_g[valore_col]) if (valore_col and pd.notna(info_g[valore_col])) else 1
                    prezzo_stimato = max(1, round(valore_base * coeff_inflazione))
                    rep_g = get_reparto(g_rm)
                    
                    # DECODIFICA DATI PER SCHEDA ESTESA
                    num_tit = int(info_g[tit_col]) if (tit_col and pd.notna(info_g[tit_col])) else 0
                    testo_titolarita = MAPPA_TITOLARITA.get(num_tit, "❓ Non specificata")

                    cod_fascia = str(info_g[fascia_col]) if (fascia_col and pd.notna(info_g[fascia_col])) else "-"
                    testo_fascia = MAPPA_FASCE_LONG.get(cod_fascia, cod_fascia if cod_fascia != '-' else 'Non specificata')

                    val_rig = str(info_g[rig_col]) if (rig_col and pd.notna(info_g[rig_col])) else "-"
                    testo_rigorista = f"⚽ Rigorista ({val_rig})" if val_rig != '-' else "❌ No Rigorista"

                    st.markdown(f"### ⚡ Scheda Giocatore: **{g_nome}** ({g_squadra})")
                    
                    col_card1, col_card2 = st.columns([1, 1])

                    with col_card1:
                        st.write(f"🎯 Ruoli Mantra: **{g_rm}** | Reparto: **{rep_g}**")
                        st.write(f"👑 Titolarità: **{testo_titolarita}**")
                        st.write(f"🏷️ Fascia: **{testo_fascia}** | {testo_rigorista}")
                        st.write(f"📊 FVM M Base: **{valore_base:.0f}** cr ➔ **Stimato Asta: {prezzo_stimato} cr**")
                        
                        if prezzo_stimato > rilancio_massimo:
                            st.error("⛔ FUORI BUDGET PER LA TUA ROSA")
                        elif prezzo_stimato > (budget_rimanente * 0.35):
                            st.warning("⚠️ ALTO IMPATTO SUL BUDGET")
                        else:
                            st.success("✅ ACQUISTO CONSIGLIATO/SOSTENIBILE")

                    with col_card2:
                        prezzo_input = st.number_input("Prezzo finale d'asta:", min_value=1, max_value=1000, value=int(prezzo_stimato), key="input_prezzo_tap")
                        
                        btn_col1, btn_col2 = st.columns(2)
                        
                        with btn_col1:
                            gia_mio = g_nome in miei_nomi
                            if reparti_count[rep_g] >= LIMITI[rep_g]:
                                st.error(f"❌ Limite {rep_g} pieno")
                            elif gia_mio:
                                st.info("Già nella tua rosa")
                            else:
                                if st.button("✅ MIO! (Acquista)", use_container_width=True, type="primary"):
                                    st.session_state.rosa.append({
                                        "Nome": g_nome,
                                        "Squadra": g_squadra,
                                        "RM": g_rm,
                                        "Prezzo": prezzo_input
                                    })
                                    st.session_state.tutti_venduti.append({
                                        "Nome": g_nome,
                                        "FVM": valore_base,
                                        "Prezzo": prezzo_input,
                                        "Mio": True
                                    })
                                    st.success(f"{g_nome} acquistato a {prezzo_input} cr!")
                                    st.rerun()

                        with btn_col2:
                            if st.button("📌 VENDUTO AD ALTRI", use_container_width=True):
                                st.session_state.tutti_venduti.append({
                                    "Nome": g_nome,
                                    "FVM": valore_base,
                                    "Prezzo": prezzo_input,
                                    "Mio": False
                                })
                                st.success(f"Registrata vendita di {g_nome} a {prezzo_input} cr!")
                                st.rerun()

        with tab_rosa:
            st.subheader("📋 Giocatori Acquistati da Me")
            if st.session_state.rosa:
                df_rosa = pd.DataFrame(st.session_state.rosa)
                st.dataframe(df_rosa, use_container_width=True)
                if st.button("🗑️ Annulla Ultimo Mio Acquisto"):
                    ultimo = st.session_state.rosa.pop()
                    st.session_state.tutti_venduti = [v for v in st.session_state.tutti_venduti if v['Nome'] != ultimo['Nome']]
                    st.rerun()
            else:
                st.info("Nessun giocatore acquistato finora.")

        with tab_moduli:
            st.subheader("🧩 Analizzatore Moduli Mantra")
            st.info("Traccia la copertura dei ruoli titolari in base agli acquisti della tua rosa.")

    except Exception as e:
        st.error(f"Errore nella lettura del file: {e}")

else:
    st.info("👈 Carica il file del listone nella barra laterale per iniziare.")
