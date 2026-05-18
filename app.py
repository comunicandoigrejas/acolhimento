import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import bcrypt
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="Acolhimento", layout="wide", page_icon="🕊️")

# ===================== CONEXÃO DINÂMICA =====================
@st.cache_resource
def get_gspread_client():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return gspread.authorize(creds)

def get_worksheet(aba_nome):
    """Pega aba da planilha da igreja logada"""
    if 'spreadsheet_url' not in st.session_state:
        st.error("Nenhuma igreja selecionada")
        st.stop()
    
    client = get_gspread_client()
    spreadsheet = client.open_by_url(st.session_state.spreadsheet_url)
    return spreadsheet.worksheet(aba_nome)

# ===================== LOGIN MULTI-IGREJA =====================
def login():
    st.title("🕊️ Sistema de Acolhimento")
    st.subheader("Bem-vindo!")

    # Carrega igrejas
    try:
        df_igrejas = pd.DataFrame(get_gspread_client().open_by_url(
            st.secrets["gsheets"]["master_spreadsheet_url"]
        ).worksheet("Igrejas").get_all_records())
        
        df_igrejas = df_igrejas[df_igrejas['ativo'] == True]
        
        igreja_nome = st.selectbox(
            "Selecione sua Igreja",
            options=df_igrejas['nome_igreja'].tolist()
        )
        
        igreja = df_igrejas[df_igrejas['nome_igreja'] == igreja_nome].iloc[0]
        
        st.session_state.igreja_id = int(igreja['igreja_id'])
        st.session_state.nome_igreja = igreja['nome_igreja']
        st.session_state.spreadsheet_url = igreja['spreadsheet_url']
        st.session_state.cor_principal = igreja.get('cor_principal', '#1E3A8A')
        
    except Exception as e:
        st.error("Erro ao carregar igrejas. Verifique a aba 'Igrejas'.")
        st.stop()

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        
        if st.button("Entrar", type="primary", use_container_width=True):
            try:
                df_usuarios = pd.DataFrame(get_worksheet("Usuários_App").get_all_records())
                usuario = df_usuarios[(df_usuarios['username'] == username) & 
                                    (df_usuarios['ativo'] == True)]
                
                if not usuario.empty:
                    hash_armazenado = usuario.iloc[0]['senha_hash']
                    if bcrypt.checkpw(senha.encode('utf-8'), hash_armazenado.encode('utf-8')):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.nome = usuario.iloc[0]['nome_completo']
                        st.session_state.role = usuario.iloc[0]['role']
                        st.success(f"✅ Bem-vindo(a), {st.session_state.nome}!")
                        st.rerun()
                    else:
                        st.error("Senha incorreta")
                else:
                    st.error("Usuário não encontrado")
            except Exception as e:
                st.error(f"Erro: {str(e)}")

# ===================== CONTROLE DE ACESSO =====================
def tem_acesso(role_necessario):
    if st.session_state.get('role') == 'admin':
        return True
    return st.session_state.get('role') == role_necessario

# ===================== MAIN =====================
def main():
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        login()
        st.stop()

    # Sidebar
    st.sidebar.success(f"🏠 {st.session_state.nome_igreja}")
    st.sidebar.success(f"👋 {st.session_state.nome}")
    st.sidebar.caption(f"Função: **{st.session_state.role.upper()}**")

    if st.sidebar.button("Sair"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # Menu dinâmico
    opcoes = ["Dashboard"]
    if tem_acesso("visitantes") or st.session_state.role == "admin":
        opcoes.append("Visitantes")
    if tem_acesso("novos_membros") or st.session_state.role == "admin":
        opcoes.append("Novos Membros")
    if tem_acesso("afastados") or st.session_state.role == "admin":
        opcoes.append("Pessoas Afastadas")
    if st.session_state.role == "admin":
        opcoes.append("Admin")

    pagina = st.sidebar.selectbox("Módulos", opcoes)

    if pagina == "Dashboard":
        st.title(f"📊 Dashboard - {st.session_state.nome_igreja}")
        st.info("Dashboard em desenvolvimento...")

    elif pagina == "Visitantes":
        st.title("👥 Visitantes")
        st.write("Módulo em construção...")

    # Demais módulos (vamos implementar um por um)

if __name__ == "__main__":
    main()
