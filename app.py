import streamlit as st
import pandas as pd
import requests
import bcrypt
from datetime import datetime

st.set_page_config(page_title="Acolhimento", layout="wide", page_icon="🕊️")

# ===================== CONFIGURAÇÃO APPS SCRIPT =====================
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxOmy4kMfnshulEpMlt41z8vMSWH6IT7sUnWo3UPXlUiKBIGdiPzlYwI8VMJuVBlyTc/exec"

def call_apps_script(action, payload):
    try:
        response = requests.post(
            APPS_SCRIPT_URL,
            json={"action": action, **payload},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro na API: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

# ===================== LOGIN MULTI-IGREJA =====================
def login():
    st.title("🕊️ Sistema de Acolhimento")
    st.subheader("Bem-vindo!")

    # Carregar igrejas do Master Sheet
    igreja_nome = st.selectbox(
        "Selecione sua Igreja",
        options=["Igreja Teste"]  # Vamos melhorar isso em breve
    )

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        
        if st.button("Entrar", type="primary", use_container_width=True):
            # Por enquanto vamos simular o login
            # Depois conectamos com a aba Usuários_App
            if username and senha:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.nome = "Usuário Teste"
                st.session_state.role = "admin"
                st.session_state.nome_igreja = igreja_nome
                st.success(f"Bem-vindo(a), {username}!")
                st.rerun()
            else:
                st.error("Preencha usuário e senha")

# ===================== MAIN =====================
def main():
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        login()
        st.stop()

    st.sidebar.success(f"🏠 {st.session_state.get('nome_igreja', 'Igreja')}")
    st.sidebar.success(f"👋 {st.session_state.get('nome', 'Usuário')}")

    if st.sidebar.button("Sair"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    pagina = st.sidebar.selectbox(
        "Módulos", 
        ["Dashboard", "Visitantes", "Novos Membros", "Pessoas Afastadas"]
    )

    if pagina == "Dashboard":
        st.title("📊 Dashboard")
        st.info("Sistema conectado via Apps Script ✅")
        st.write("Pronto para começar a implementar os módulos.")

    elif pagina == "Visitantes":
        st.title("👥 Visitantes")
        st.success("Módulo Visitantes - Vamos implementar agora?")
        
        if st.button("Testar conexão com Planilha"):
            resultado = call_apps_script("getData", {
                "spreadsheetUrl": st.secrets.get("gsheets", {}).get("spreadsheet_url", ""),
                "sheetName": "Visitantes"
            })
            st.write(resultado)

if __name__ == "__main__":
    main()
