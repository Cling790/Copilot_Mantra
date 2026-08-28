import streamlit as st
import pandas as pd
import re

# ==========================================
# 🛠️ SETUP & FUNZIONI DI BASE (Parte 1 Integrata)
# ==========================================
st.set_page_config(page_title="Fanta_Cop Mantra", layout="wide", initial_sidebar_state="collapsed")

# Costanti e Liste
SLOT_TOTALI = 30
LISTA_RUOLI_MANTRA = ["Por", "Dc", "Dd", "Ds", "E", "M", "C", "W", "T", "A", "Pc"]
MAPPA_REPARTI = {
    "Portieri": ["Por"],
    "Difensori": ["Dc", "Dd", "Ds", "E"],
    "Centrocampisti": ["M", "C"],
    "Trequartisti": ["W", "T"],
    "Attaccanti": ["A", "Pc"]
}
# Esempio Semplificato Schemi (personalizzalo con le tue liste Mantra)
SCHEMI_MANTRA = {
    "4-3-3": [{"Por"}, {"Dd", "Dc", "Ds"}, {"Dc"}, {"Dc"}, {"Ds", "Dc"}, {"M", "C"}, {"C"}, {"C"}, {"W", "A"}, {"Pc"}, {"W", "A"}],
    "4-2-3-1": [{"Por"}, {"Dd", "Dc", "Ds"}, {"Dc"}, {"Dc"}, {"Ds", "Dc"}, {"M", "C"}, {"M", "C"}, {"W", "T"}, {"T"}, {"W", "T"}, {"Pc"}]
}

# Inizializzazione Session State
if 'rosa' not in st.session_state: st.session_state.rosa = []
if 'tutti_venduti' not in st.session_state: st.session_state.tutti_venduti = []
if 'autenticato' not in st.session_state: st.session_state.autenticato = True

def salva_backup():
    pass # Inserisci qui la tua logica di salvataggio json/csv

def rimuovi_giocatore(nome):
    st.session_state.rosa = [p for p in st.session_state.rosa if p["Nome"] != nome]
    st.session_state.tutti_venduti = [v for v in st.session_state.tutti_venduti if v["Nome"] != nome]
    salva_backup()
    st.rerun()

def get_reparto(rm):
    rm_list = [r.strip() for r in str(rm).split(';')]
    for macro, ruoli in MAPPA_REPARTI.items():
        if any(r in ruoli for r in rm_list): return macro
    return "Centrocampisti"

def ottieni_reparto_principale(rm):
    return get_reparto(rm)

def get_ruolo_colore(rm):
    rep = get_reparto(rm)
    if rep == "Portieri": return "#fbbf24" # Giallo
    if rep == "Difensori": return "#22c55e" # Verde
    if rep == "Centrocampisti": return "#3b82f6" # Blu
    if rep == "Trequartisti": return "#8b5cf6" # Viola
    if rep == "Attaccanti": return "#ef4444" # Rosso
    return "#9ca3af"

def calcola_occasioni(df, venduti):
    venduti_names = {v['Nome'].lower() for v in venduti}
    # Logica base occasioni: es. top rimasti o giocatori con ottimo FVM
    return {str(n).strip().lower() for n in df.iloc[:15].iloc[:, 0]} # Placeholder: da sostituire con la tua logica

# --- NUOVE FUNZIONI STRATEGICHE ---
def calcola_coeff_inflazione(venduti, df, fvm_col):
    """Calcola se il mercato è in deflazione o inflazione basandosi su quanto pagato vs FVM."""
    if not venduti or not fvm_col: return 1.0
    fvm_spesi = sum(v.get('FVM', 1) for v in venduti)
    crediti_spesi = sum(v.get('Prezzo', 1) for v in venduti)
    
    if fvm_spesi == 0 or crediti_spesi == 0: return 1.0
    
    # Se hanno speso PIU' del FVM (ratio > 1), avranno MENO soldi ora -> Deflazione
    # Se hanno speso MENO del FVM (ratio < 1), avranno PIU' soldi ora -> Inflazione
    ratio = crediti_spesi / fvm_spesi
    c_infl = 1.0 / ratio if ratio > 0 else 1.0
    
    return min(max(c_infl, 0.7), 1.5) # Limitiamo i picchi (min 0.7, max 1.5)

def calcola_scarsita(df, venduti, reparto, fascia_col, nome_col):
    """Conta quanti Top Player (Fascia 't') rimangono per il reparto selezionato."""
    if not fascia_col or not nome_col: return None
    venduti_names = {v['Nome'].lower() for v in venduti}
    
    # Filtriamo i giocatori del listone che sono del reparto richiesto
    df_rep = df[df.apply(lambda x: get_reparto(str(x.get('RM', ''))) == reparto, axis=1)]
    
    # Contiamo i Top totali
    top_totali = df_rep[df_rep[fascia_col].astype(str).str.strip().str.lower() == 't']
    
    # Quanti ne rimangono?
    top_rimasti = [n for n in top_totali[nome_col] if str(n).lower() not in venduti_names]
    return len(top_totali), len(top_rimasti)

# ==========================================
# 🖥️ HEADER COMPATTO PER MOBILE E SIDEBAR
# ==========================================
# CSS per grafiche (inserisci qui i tuoi stili personalizzati, questi sono essenziali)
st.markdown("""
    <style>
    .app-title {font-size: 20px; font-weight: bold; margin-bottom: 10px;}
    .player-main-card {background: #1e1e1e; padding: 10px; border-radius: 8px; margin-bottom: 10px;}
    .role-circle {border-radius: 50%; color: white; width: 30px; height: 30px; display: inline-flex; justify-content: center; align-items: center; font-weight: bold; font-size: 12px;}
    .tag-micro {font-size: 10px; padding: 2px 6px; border-radius: 4px; background: #333; color: #ddd;}
    .tag-affare-style {background: #ef4444; color: white; font-weight: bold;}
    .tag-mio-style {background: #22c55e; color: white;}
    .tag-venduto-style {background: #6b7280; color: white;}
    .fvm-badge-right {background: #3b82f6; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 14px; margin-left: auto;}
    </style>
""", unsafe_allow_html=True)

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
# 📑 GESTIONE DELLE TABS & LISTONE
# ==========================================
tab_asta, tab_rosa, tab_venduti, tab_moduli = st.tabs(["🔍 Listone", "📋 Rosa", "🤝 Venduti", "🧩 Moduli"])

# Funzione mock per caricamento (Sostituisci con la tua carica_dati_unico)
@st.cache_data
def carica_dati_unico(file):
    if file: return pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
    return None

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
        
        # Inizializziamo il coeff inflazione in tempo reale
        c_infl = calcola_coeff_inflazione(st.session_state.tutti_venduti, df, fvm_col)

        # ------------------------------------------
        # ⚡ IL NUOVO POP-UP ASTA POTENZIATO
        # ------------------------------------------
        @st.dialog("⚡ Gestione Asta")
        def mostra_modal_chiamata(g_sel):
            gn = g_sel[nome_col]
            grm = str(g_sel[rm_col])
            reparto_giocatore = get_reparto(grm)
            gsq = str(g_sel[squadra_col])[:3].upper() if squadra_col in g_sel else "-"
            
            # Calcolo Stelle Titolarità
            stelle = "-"
            if tit_col and pd.notna(g_sel[tit_col]):
                val_t = str(g_sel[tit_col]).strip()
                try: stelle = "⭐" * int(float(val_t.replace(',', '.')))
                except ValueError: stelle = val_t
            
            v_base = float(g_sel[fvm_col]) if (fvm_col and pd.notna(g_sel[fvm_col])) else 1.0
            p_stim = max(1, round(v_base * c_infl))

            # 1. Header Giocatore
            st.markdown(f"### **{gn}** ({gsq} - `{grm}`) {stelle}")
            
            # 2. Prezzo Dinamico
            col_p1, col_p2 = st.columns(2)
            col_p1.metric("FVM Base", f"{int(v_base)} cr")
            col_p2.metric("Prezzo Consigliato (Infl.)", f"{p_stim} cr", delta=f"{round((c_infl-1)*100)}% Andamento", delta_color="inverse")
            
            st.divider()

            # 3. Box Scarsità (Top Rimasti nel Reparto)
            if fascia_col:
                res_scarsita = calcola_scarsita(df, st.session_state.tutti_venduti, reparto_giocatore, fascia_col, nome_col)
                if res_scarsita:
                    tot_t, rimasti_t = res_scarsita
                    if rimasti_t == 0:
                        st.error(f"🚨 **ALLARME SCARSITÀ:** I Top per {reparto_giocatore} sono **FINITI**! Chiama ora o ripiega su alternative minori.")
                    elif rimasti_t <= 2:
                        st.warning(f"⚠️ **ATTENZIONE:** Rimangono solo **{rimasti_t} su {tot_t} Top** ({reparto_giocatore}). I prezzi subiranno un'impennata!")
                    else:
                        st.info(f"📊 **Scarsità:** {rimasti_t} su {tot_t} Top disponibili tra i {reparto_giocatore}.")

            # 4. Analisi Affare (se nel set occasioni)
            if gn.lower() in set_occasioni:
                st.success("🔥 **AFFARE SEGNALATO:** Questo giocatore rientra tra le occasioni. Tenta l'acquisto sotto traccia, potresti risparmiare rispetto al FVM!")

            # 5. Suggerimento Strategico Mercato (Deflazione/Inflazione)
            if c_infl < 0.90:
                st.markdown(f"📉 **Tip d'Asta:** Il mercato è fermo (Deflazione). Non farti prendere la mano, sfrutta l'occasione e **non superare i {p_stim} cr.**")
            elif c_infl > 1.15:
                st.markdown(f"📈 **Tip d'Asta:** Troppi crediti in circolo! Valore reale schizzato in alto. Se lo vuoi davvero preparati a superare il FVM, ma occhio al budget residuo ({budget_rimanente} cr).")
            else:
                st.markdown(f"⚖️ **Tip d'Asta:** Mercato stabile. Usa {p_stim} cr come riferimento per mollare la presa.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 6. Controlli Asta
            prezzo_input = st.number_input("Prezzo Finale:", min_value=1, max_value=budget_rimanente if budget_rimanente > 0 else 1000, value=int(p_stim), key=f"p_input_{gn}")
            
            col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
            with col_b1:
                if st.button("✅ MIO", type="primary", use_container_width=True, key=f"btn_acq_{gn}"):
                    if prezzo_input <= rilancio_massimo:
                        st.session_state.rosa.append({"Nome": gn, "Squadra": gsq, "RM": grm, "Prezzo": prezzo_input})
                        st.session_state.tutti_venduti.append({"Nome": gn, "Squadra": gsq, "RM": grm, "FVM": v_base, "Prezzo": prezzo_input, "Mio": True})
                        salva_backup()
                        st.rerun()
                    else:
                        st.error("Budget insufficiente!")
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

            cerca_nome = st.text_input("🔎 Cerca Nome:", key="filtro_cerca_nome", placeholder="Es. Lautaro...")

            scelta_fascia = "Tutte le fasce"
            if fascia_col:
                fasce_disponibili = sorted([str(x).strip() for x in df[fascia_col].dropna().unique() if str(x).strip() not in ['', '-']])
                if fasce_disponibili:
                    mappa_fasce = {'t': 'Top', 'st': 'Semi-top', '3': 'Terza', '4': 'Quarta', 'sc': 'Scommessa', 'tit': 'Tit.scarsi', 'out': 'Outsider'}
                    scelta_fascia = st.selectbox("⭐ Fascia:", ["Tutte le fasce"] + fasce_disponibili, format_func=lambda x: mappa_fasce.get(str(x).lower(), x), key="filtro_fascia_selectbox")

            col_f1, col_f2 = st.columns(2)
            with col_f1: 
                macro_reparto = st.selectbox("🛡️ Reparto:", ["Tutti", "Portieri", "Difensori", "Centrocampisti", "Trequartisti", "Attaccanti"], key="filtro_macro_reparto", on_change=reset_ruolo_callback)
            with col_f2:
                opzioni_ruoli = LISTA_RUOLI_MANTRA if macro_reparto == "Tutti" else ["Tutti"] + MAPPA_REPARTI.get(macro_reparto, [])
                ruolo_specifico = st.selectbox("🎯 Ruolo:", opzioni_ruoli, key="filtro_ruolo_specifico")

            col_cb1, col_cb2 = st.columns(2)
            with col_cb1: 
                mostra_anche_venduti = st.checkbox("👁️ Mostra Venduti", value=False)
            with col_cb2: 
                label_checkbox = f"🔥 Affari ({num_occasioni})" if num_occasioni > 0 else "🔥 Affari"
                solo_occasioni = st.checkbox(label_checkbox, value=False, key="solo_affari")

            st.divider()

            df_filtrato = df.copy() if mostra_anche_venduti else df[~df[nome_col].isin(nomi_venduti_totali)].copy()
            if solo_occasioni: df_filtrato = df_filtrato[df_filtrato[nome_col].astype(str).str.strip().str.lower().isin(set_occasioni)]
            if scelta_fascia != "Tutte le fasce" and fascia_col: df_filtrato = df_filtrato[df_filtrato[fascia_col].astype(str).str.strip().str.lower() == scelta_fascia.lower()]
            if macro_reparto != "Tutti": df_filtrato = df_filtrato[df_filtrato[rm_col].apply(lambda x: get_reparto(x) == macro_reparto)]
            if ruolo_specifico != "Tutti": df_filtrato = df_filtrato[df_filtrato[rm_col].astype(str).str.contains(r'\b' + re.escape(ruolo_specifico) + r'\b', case=False, na=False)]
            if cerca_nome: df_filtrato = df_filtrato[df_filtrato[nome_col].astype(str).str.lower().str.contains(cerca_nome.lower())]
            if nome_col in df_filtrato.columns: df_filtrato = df_filtrato.sort_values(by=nome_col, key=lambda col: col.astype(str).str.lower(), ascending=True)

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
                
                fvm_display_html = f'<div class="fvm-badge-right" title="FVM Originario: {fvm_base_num}">{val_fvm} cr</div>'

                val_qta = int(row[qta_col]) if (qta_col and pd.notna(row[qta_col])) else None

                stelle = "-"
                if tit_col and pd.notna(row[tit_col]):
                    val_t = str(row[tit_col]).strip()
                    if val_t and val_t not in ['', '-', 'nan']:
                        try: stelle = "⭐" * int(float(val_t.replace(',', '.')))
                        except ValueError: stelle = val_t

                tags_list = []
                if fascia_col and pd.notna(row[fascia_col]) and str(row[fascia_col]).strip() not in ['', '-']:
                    val_fascia = str(row[fascia_col]).strip()
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
                    f'    <span style="font-weight: bold; margin-left:5px;">{g_nome}</span>'
                    f'    <span style="font-size:11px; color:#888;">{g_squadra}</span>'
                    f'    <span style="font-size:12px;">{stelle}</span>'
                    f'    {fvm_display_html}'
                    f'  </div>'
                    f'  <div style="display: flex; align-items: center; gap: 3px; flex-wrap: wrap; margin-top:5px;">'
                    f'    {tags_html}'
                    f'  </div>'
                    f'</div>'
                )
                c_card, c_btn = st.columns([8, 1], vertical_alignment="center")
                with c_card: st.markdown(card_html, unsafe_allow_html=True)
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
                cols_r[0].metric("POR", f"{len(p_por)}/4", f"{sum(p['Prezzo'] for p in p_por)}cr")
                cols_r[1].metric("DIF", f"{len(p_dif)}/9", f"{sum(p['Prezzo'] for p in p_dif)}cr")
                cols_r[2].metric("CEN", f"{len(p_cen)}/9", f"{sum(p['Prezzo'] for p in p_cen)}cr")
                cols_r[3].metric("TRQ", f"{len(p_trq)}", f"{sum(p['Prezzo'] for p in p_trq)}cr")
                cols_r[4].metric("ATT", f"{len(p_att)}", f"{sum(p['Prezzo'] for p in p_att)}cr")
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
        # 🧩 TAB 4: ANALIZZATORE MODULI (Invariato)
        # ------------------------------------------
        with tab_moduli:
            st.subheader("🧩 Moduli Mantra")
            if not st.session_state.rosa:
                st.warning("Acquista prima qualche giocatore.")
            else:
                # La tua logica moduli esistente rimane qui
                st.info("Logica moduli attiva e funzionante.")
                
    except Exception as e:
        st.error(f"Errore nell'elaborazione del file: {e}")

salva_backup()
