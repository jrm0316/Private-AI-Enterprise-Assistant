import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Resume Assistant", layout="wide")

st.title("🤖 AI Resume Assistant")

# =========================
# STATE INIT
# =========================

for key, default in {
    "token": None,
    "messages": [],
    "history_loaded": False,
    "doc_loaded": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# =========================
# SIDEBAR
# =========================

with st.sidebar:

    st.subheader("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")

    if st.button("Login"):

        res = requests.post(
            f"{API_URL}/login",
            json={"email": email, "password": password}
        )

        if res.status_code != 200:

            try:
                st.error(res.json().get("error"))
            except Exception:
                st.error(res.text)

            st.stop()

        response = res.json()

        token = (
            response.get("data", {}).get("access_token")
            or response.get("access_token")
            or response.get("token")
        )

        if not token:
            st.error("Token não recebido da API")
            st.stop()

        st.session_state.token = token
        st.session_state.messages = []
        st.session_state.history_loaded = False
        st.session_state.doc_loaded = False

        st.success("Login realizado!")
        st.rerun()

    if st.button("🗑 Limpar Histórico"):

        res = requests.delete(
            f"{API_URL}/clear-history",
            headers={
                "Authorization": f"Bearer {st.session_state.token}"
            }
        )

        # LIMPA CHAT LOCAL
        st.session_state.messages = []

        # BLOQUEIA RELOAD DO HISTÓRICO
        st.session_state.history_loaded = True

        st.success("Histórico apagado!")

        st.rerun()

    st.divider()

    option = st.radio(
        "Menu",
        ["Chat com Documento", "Analisar Currículo", "Comparar com Vaga"]
    )

# =========================================================
# CHAT COM DOCUMENTO (RAG)
# =========================================================

if option == "Chat com Documento":

    if not st.session_state.token:
        st.warning("Faça login primeiro")
        st.stop()

    st.header("📄 Chat com Documento (RAG)")

    # =========================
    # UPLOAD
    # =========================

    uploaded_files = st.file_uploader(
        "Upload de documentos",
        type=["pdf", "txt"],
        accept_multiple_files=True
    )

    if uploaded_files and st.button("Processar documentos"):

        files = []

        for f in uploaded_files:
            file_type = "application/pdf" if f.name.endswith(".pdf") else "text/plain"
            files.append(("files", (f.name, f.getvalue(), file_type)))

        res = requests.post(
            f"{API_URL}/upload",
            files=files,
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )

        if res.status_code == 200:
            st.success("Documentos processados!")
            st.session_state.doc_loaded = True
            st.session_state.messages = []
            st.session_state.history_loaded = False
        else:
            st.error(res.text)

    # =========================
    # LOAD HISTORY
    # =========================

    if (
    st.session_state.doc_loaded
    and not st.session_state.history_loaded
    and st.session_state.token
    ):

        history_res = requests.get(
            f"{API_URL}/history",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )

        if history_res.status_code == 200:
            st.session_state.messages = history_res.json().get("data", [])
            st.session_state.history_loaded = True

    # =========================
    # CHAT DISPLAY
    # =========================

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("Faça uma pergunta")

    if question:

        if not st.session_state.token:
            st.error("Sem login")
            st.stop()

        st.session_state.messages.append({"role": "user", "content": question})

        with st.chat_message("user"):
            st.markdown(question)

        res = requests.post(
            f"{API_URL}/chat",
            json={
                "question": question,
                "selected_document": "Todos"
            },
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )

        if res.status_code != 200:

            try:
                st.error(res.json().get("error"))
            except Exception:
                st.error(res.text)

            st.stop()

        response_json = res.json()

        # =========================
        # CHECK ERROR
        # =========================

        if not response_json.get("success"):
            st.error(response_json.get("error"))
            st.stop()

        # =========================
        # DATA
        # =========================

        data = response_json.get("data") or {}

        answer = data.get("answer", "Sem resposta")

        st.session_state.messages.append({"role": "assistant", "content": answer})

        with st.chat_message("assistant"):
            st.markdown(answer)

# =========================================================
# ANALYZE
# =========================================================

elif option == "Analisar Currículo":

    st.header("📊 Analisar Currículo")

    text = st.text_area("Cole seu currículo aqui:")

    if st.button("Analisar"):

        res = requests.post(
            f"{API_URL}/analyze",
            json={"text": text}
        )

        st.write(res.json().get("data", {}))

# =========================================================
# COMPARE
# =========================================================

elif option == "Comparar com Vaga":

    st.header("⚔️ Comparar com Vaga")

    resume = st.text_area("Currículo")
    job = st.text_area("Vaga")

    if st.button("Comparar"):

        res = requests.post(
            f"{API_URL}/compare",
            json={"resume": resume, "job": job}
        )

        st.write(res.json().get("data", {}))