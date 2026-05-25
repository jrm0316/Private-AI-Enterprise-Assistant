import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Resume Assistant", layout="wide")

st.title("🤖 AI Resume Assistant")

# =========================
# LOGIN
# =========================

if "token" not in st.session_state:
    st.session_state.token = None

with st.sidebar:
    if st.button("🗑 Limpar Histórico"):

        res = requests.delete(
            f"{API_URL}/clear-history",
            headers={
                "Authorization": f"Bearer {st.session_state.token}"
            }
        )

        print("CLEAR STATUS:", res.status_code)
        print("CLEAR RESPONSE:", res.text)

        # LIMPA MEMÓRIA CHAT
        st.session_state.messages = []

        # RESET FLAGS
        st.session_state.history_loaded = False

        # BLOQUEIA RELOAD
        st.session_state.history_cleared = True

        st.success("Histórico apagado!")

        st.rerun()

    st.subheader("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")

    if st.button("Login"):

        res = requests.post(
            f"{API_URL}/login",
            json={
                "email": email,
                "password": password
            }
        )
        response = res.json()
        if res.status_code == 200:

            token = (
                response.get("data", {}).get("access_token")
                or response.get("access_token")
                or response.get("token")
            )
            if not token:
                st.error("Token não recebido da API")
                st.stop()

            st.session_state.token = token
            st.write("TOKEN:", st.session_state.token)
            st.success("Login realizado!")

        else:
            st.error(response)

# =========================
# MEMÓRIA CHAT
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "history_loaded" not in st.session_state:
    st.session_state.history_loaded = False

if "history_cleared" not in st.session_state:
    st.session_state.history_cleared = False

# =========================
# SIDEBAR
# =========================
st.sidebar.title("Menu")

option = st.sidebar.radio(
    "Escolha uma opção:",
    ["Chat com Documento", "Analisar Currículo", "Comparar com Vaga"]
)

# =========================
# 1. CHAT (RAG)
# =========================
if option == "Chat com Documento":
    st.header("📄 Chat com Documento (RAG)")

    if "doc_loaded" not in st.session_state:
        st.session_state.doc_loaded = False

    uploaded_files = st.file_uploader(
        "Upload de documentos",
        type=["pdf", "txt"],
        accept_multiple_files=True
    )

    if uploaded_files:

        if st.button("Processar documentos"):

            with st.spinner("Processando..."):

                files = []

                for uploaded_file in uploaded_files:

                    file_type = (
                        "application/pdf"
                        if uploaded_file.name.endswith(".pdf")
                        else "text/plain"
                    )

                    files.append(
                        (
                            "files",
                            (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                file_type
                            )
                        )
                    )
                
                res = requests.post(
                    f"{API_URL}/upload",
                    files=files,
                    headers={
                        "Authorization": f"Bearer {st.session_state.token}"
                    }
                )

                if res.status_code == 200:

                    st.success("Documentos processados!")

                    st.session_state.doc_loaded = True

                    # =========================
                    # RESET CHAT MEMORY
                    # =========================

                    st.session_state.messages = []

                    st.session_state.history_loaded = True
                else:
                    st.error(f"Erro: {res.text}")

    if st.session_state.doc_loaded:
        # =========================
        # LOAD METADATA
        # =========================

        metadata = []

        try:

            metadata_res = requests.get(
                f"{API_URL}/documents",
                headers={
                    "Authorization": f"Bearer {st.session_state.token}"
                }
            )

            if metadata_res.status_code == 200:

                metadata = metadata_res.json().get(
                    "data",
                    []
                )

        except Exception as e:
            print(e)
        
        # =========================
        # DOCUMENT FILTER
        # =========================

        selected_document = st.selectbox(
            "Filtrar documento",
            ["Todos"] + [
                item["filename"]
                for item in metadata
            ]
        )

        # =========================
        # LIST DOCUMENTS
        # =========================

        docs_res = requests.get(
            f"{API_URL}/documents",
            headers={
                "Authorization": f"Bearer {st.session_state.token}"
            }
        )

        if docs_res.status_code == 200:

            docs_data = docs_res.json()

            documents = docs_data.get("data", [])

            if documents:

                st.subheader("📂 Seus documentos")

                for doc in documents:

                    col1, col2 = st.columns([8, 1])

                    with col1:

                        st.write(
                            f"📄 {doc['filename']} "
                            f"({doc['uploaded_at']})"
                        )

                    with col2:

                        if st.button(
                            "❌",
                            key=f"delete_{doc['filename']}"
                        ):

                            delete_res = requests.delete(
                                f"{API_URL}/documents/{doc['filename']}",
                                headers={
                                    "Authorization": f"Bearer {st.session_state.token}"
                                }
                            )

                            if delete_res.status_code == 200:

                                st.success(
                                    f"{doc['filename']} removido!"
                                )

                                st.rerun()

                            else:

                                st.error("Erro ao remover documento")

        # =========================
        # LOAD HISTORY
        # =========================
        if (
            not st.session_state.history_loaded
            and not st.session_state.history_cleared
        ):

            try:

                history_res = requests.get(
                    f"{API_URL}/history",
                    headers={
                        "Authorization": f"Bearer {st.session_state.token}"
                    }
                )

                if history_res.status_code == 200:

                    history_data = history_res.json()

                    loaded_messages = history_data.get(
                        "data",
                        []
                    )

                    st.session_state.messages = loaded_messages
                    st.session_state.history_cleared = False

            except Exception as e:
                print(e)
                

        # =========================
        # SHOW CHAT
        # =========================
        for message in st.session_state.messages:

            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        question = st.chat_input("Faça uma pergunta")

        if question:
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": question
                }
            )

            with st.chat_message("user"):
                st.markdown(question)

            # =========================
            # REQUEST CHAT API
            # =========================

            res = requests.post(
                f"{API_URL}/chat",
                json={
                    "question": question,
                    "selected_document": selected_document
                },

                headers={
                    "Authorization": f"Bearer {st.session_state.token}"
                }
            )

            # =========================
            # STATUS CHECK
            # =========================

            if res.status_code != 200:
                st.error(f"Erro na API: {res.text}")
                st.stop()

            # =========================
            # JSON
            # =========================

            try:
                response_json = res.json()
            except Exception:
                st.error("Resposta inválida da API")
                st.stop()

            # =========================
            # DATA
            # =========================

            data = response_json.get("data", {})

            answer = data.get("answer", "Sem resposta")
            sources = data.get("sources", []) or []
            confidence = data.get("confidence", 0)

            # =========================
            # SAVE CHAT HISTORY
            # =========================

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )    

            with st.chat_message("assistant"):
                st.markdown(answer)

            st.subheader("Fontes:")

            shown_snippets = set()

            for src in data.get("sources", []):

                snippet = src.get("snippet", "Conteúdo não encontrado")

                # Evita fontes repetidas
                if snippet in shown_snippets:
                    continue

                shown_snippets.add(snippet)

                relevance = src.get("relevance", "N/A")
                source = src.get("source", "Desconhecido")
                page = src.get("page", "-")

                st.write(f"📄 Fonte: {source} | Página: {page}")
                st.write(f"📌 {snippet}")
                if relevance == "Alta":
                    st.success(f"🟢 Relevância: {relevance}")

                elif relevance == "Média":
                    st.warning(f"🟡 Relevância: {relevance}")

                else:
                    st.error(f"🔴 Relevância: {relevance}")

                st.write("---")
    else:
        st.warning("⚠️ Faça upload e processe o documento primeiro.")


# =========================
# 2. ANALYZE
# =========================
elif option == "Analisar Currículo":
    st.header("📊 Analisar Currículo")

    text = st.text_area("Cole seu currículo aqui:", key="cv_interview")

    if st.button("Analisar"):
        res = requests.post(
            f"{API_URL}/analyze",
            json={"text": text}
        )

        res_json = res.json()

        if not res_json.get("success"):
            st.error(res_json.get("error", "Erro desconhecido"))
            st.stop()

        data = res_json.get("data", {})

        answer = data.get("answer", "Sem resposta")
        sources = data.get("sources", [])

        st.success(f"Nível: {data['level']}")

        for item in data.get("strengths", []):
            st.write(item)

        for item in data.get("weaknesses", []):
            st.write(item)

        for item in data.get("suggestions", []):
            st.write(item)

        if "erro" in data:
            st.error(data["erro"])
            st.write(data.get("raw", ""))
        else:
            st.success(f"Nível: {data['nivel']}")

            for item in data.get("pontos_fortes", []):
                st.write(f"✅ {item}")

            for item in data.get("pontos_fracos", []):
                st.write(f"❌ {item}")

            st.subheader("Sugestões")
            for item in data["sugestoes"]:
                st.write(f"💡 {item}")


# =========================
# 3. COMPARE
# =========================
elif option == "Comparar com Vaga":
    st.header("⚔️ Comparar com Vaga")

    resume = st.text_area("Currículo", key="cv_match")
    job = st.text_area("Descrição da vaga", key="job_match")

    if st.button("Comparar"):
        res = requests.post(
            f"{API_URL}/compare",
            json={
                "resume": resume,
                "job": job
            }
        )

        res_json = res.json()

        if not res_json.get("success"):
            st.error(res_json.get("error", "Erro desconhecido"))
            st.stop()

        data = res_json.get("data", {})

        answer = data.get("answer", "Sem resposta")
        sources = data.get("sources", [])

        st.metric("Match", f"{data['match']}%")

        st.subheader("Fortes")
        for item in data.get("strengths", []):
            st.write(f"🟢 {item}")

        st.subheader("Faltando")
        for item in data.get("missing", []):
            st.write(f"🔴 {item}")

        st.write(data.get("analysis", ""))

        if "erro" in data:
            st.error(data["erro"])
            st.write(data.get("raw", ""))
        else:
            st.metric("Match", f"{data['match']}%")

            st.subheader("Faltando (Obrigatório)")
            for item in data.get("faltando_obrigatorio", []):
                st.write(f"🔴 {item}")

            st.subheader("Faltando (Desejável)")
            for item in data.get("faltando_desejavel", []):
                st.write(f"🟡 {item}")

            for item in data.get("pontos_fortes", []):
                st.write(f"🟢 {item}")

            st.subheader("Resumo")
            st.write(data["resumo"])