import streamlit as st
import pandas as pd
import requests
import bcrypt
from datetime import datetime

st.set_page_config(page_title="Acolhimento", layout="wide", page_icon="🕊️")

# ===================== CONFIGURAÇÃO =====================
APPS_SCRIPT_URL = st.secrets["apps_script"]["url"]

def call_apps_script(action, payload):
    try:
        response = requests.post(
            APPS_SCRIPT_URL,
            json={"action": action, **payload},
            timeout=25
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro de conexão com Apps Script: {e}")
        return None

# ===================== LOGIN =====================
def login():
    st.title("🕊️ Sistema de Acolhimento")
    st.subheader("Selecione sua igreja e faça login")

    # Carregar igrejas
    igrejas = call_apps_script("getData", {
        "spreadsheetUrl": st.secrets["gsheets"]["master_spreadsheet_url"],
        "sheetName": "Igrejas"
    })

    if not igrejas or isinstance(igrejas, dict) and "error" in igrejas:
        st.error("Não foi possível carregar as igrejas.")
        st.stop()

    df_igrejas = pd.DataFrame(igrejas)
    df_igrejas = df_igrejas[df_igrejas['ativo'] == True]

    igreja_nome = st.selectbox(
        "Igreja",
        options=df_igrejas['nome_igreja'].tolist()
    )

    igreja = df_igrejas[df_igrejas['nome_igreja'] == igreja_nome].iloc[0]

    st.session_state.igreja_nome = igreja['nome_igreja']
    st.session_state.spreadsheet_url = igreja['spreadsheet_url']

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar", type="primary", use_container_width=True):
            if not username or not senha:
                st.error("Preencha usuário e senha")
                st.stop()

            # Buscar usuários
            usuarios = call_apps_script("getData", {
                "spreadsheetUrl": st.session_state.spreadsheet_url,
                "sheetName": "Usuários_App"
            })

            if usuarios:
                df_usuarios = pd.DataFrame(usuarios)
                usuario = df_usuarios[
                    (df_usuarios['username'] == username) & 
                    (df_usuarios.get('ativo') == True)
                ]

                if not usuario.empty:
                    hash_armazenado = str(usuario.iloc[0]['senha_hash'])
                    if bcrypt.checkpw(senha.encode('utf-8'), hash_armazenado.encode('utf-8')):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.nome = usuario.iloc[0]['nome_completo']
                        st.session_state.role = usuario.iloc[0]['role']
                        st.success(f"✅ Bem-vindo(a), {st.session_state.nome}!")
                        st.rerun()
                    else:
                        st.error("❌ Senha incorreta")
                else:
                    st.error("Usuário não encontrado ou inativo")
            else:
                st.error("Erro ao carregar usuários")

# ===================== MAIN APP =====================
def main():
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        login()
        st.stop()

    # Sidebar
    st.sidebar.success(f"🏠 {st.session_state.get('igreja_nome', '')}")
    st.sidebar.success(f"👋 {st.session_state.get('nome', '')}")
    st.sidebar.caption(f"Função: **{st.session_state.get('role', '').upper()}**")

    if st.sidebar.button("Sair"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # Menu
    opcoes = ["Dashboard", "Visitantes", "Novos Membros", "Pessoas Afastadas"]
    if st.session_state.role == "admin":
        opcoes.append("Admin")

    pagina = st.sidebar.selectbox("Módulos", opcoes)

    if pagina == "Dashboard":
        st.title(f"📊 Dashboard - {st.session_state.igreja_nome}")
        st.success("✅ Conectado com Apps Script")
        st.info("Estamos prontos para construir os módulos.")

    elif pagina == "Visitantes":
        st.title("👥 Visitantes")
        st.write("Módulo de Visitantes será implementado agora.")

if __name__ == "__main__":
    main()
