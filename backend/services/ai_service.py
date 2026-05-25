import numpy as np
import os
import re
import traceback
import os
import json

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.1-8b-instant"
)

VECTORSTORE_DIR = "vectorstores"
CHAT_HISTORY_DIR = "chat_history"

os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)
os.makedirs(VECTORSTORE_DIR, exist_ok=True)

VECTORSTORE_PATH = "vectorstore"

# =========================
# VECTORSTORE
# =========================
def update_vectorstore(user_id, documents):

    try:
        print("SALVANDO VECTORSTORE")

        from langchain_community.vectorstores import FAISS

        user_path = os.path.join(
            VECTORSTORE_DIR,
            str(user_id)
        )
        print("SALVANDO VECTORSTORE")

        os.makedirs(user_path, exist_ok=True)

        # =========================
        # EXISTE VECTORSTORE?
        # =========================

        if os.path.exists(
            os.path.join(user_path, "index.faiss")
        ):
            print("CARREGANDO VECTORSTORE")
            vectorstore = FAISS.load_local(
                user_path,
                embeddings,
                allow_dangerous_deserialization=True
            )
            print("ADICIONANDO DOCUMENTOS")
            vectorstore.add_documents(documents)

        else:
            print("CRIANDO NOVO VECTORSTORE")
            vectorstore = FAISS.from_documents(
                documents,
                embeddings
            )
        print("SALVANDO VECTORSTORE")

        # =========================
        # SAVE
        # =========================

        vectorstore.save_local(user_path)

        print(f"VECTORSTORE SALVO: {user_id}")

        return True

    except Exception as e:

        traceback.print_exc()

        return False

# =========================
# REBUILD VECTORSTORE
# =========================
def rebuild_vectorstore(user_id):

    try:

        from langchain_community.vectorstores import FAISS
        from langchain_core.documents import Document

        user_path = os.path.join(
            VECTORSTORE_DIR,
            str(user_id)
        )

        documents_path = os.path.join(
            user_path,
            "documents.json"
        )

        if not os.path.exists(documents_path):

            return False

        # LOAD DOCUMENTS
        import json

        with open(
            documents_path,
            "r",
            encoding="utf-8"
        ) as f:

            saved_docs = json.load(f)

        documents = []

        for item in saved_docs:

            documents.append(
                Document(
                    page_content=item["content"],
                    metadata=item["metadata"]
                )
            )

        # CREATE NEW VECTORSTORE
        vectorstore = FAISS.from_documents(
            documents,
            embeddings
        )

        # SAVE
        vectorstore.save_local(user_path)

        print("VECTORSTORE REBUILDADO")

        return True

    except Exception as e:

        traceback.print_exc()

        return False

# =========================
# SAVE CHAT HISTORY
# =========================
def save_chat_history(user_id, history):

    try:

        user_file = os.path.join(
            CHAT_HISTORY_DIR,
            f"{user_id}.json"
        )

        with open(user_file, "w", encoding="utf-8") as f:
            json.dump(
                history,
                f,
                ensure_ascii=False,
                indent=2
            )

    except Exception:
        traceback.print_exc()


# =========================
# LOAD CHAT HISTORY
# =========================

def load_chat_history(user_id):

    try:

        user_file = os.path.join(
            CHAT_HISTORY_DIR,
            f"{user_id}.json"
        )

        if not os.path.exists(user_file):
            return []

        with open(user_file, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:
        traceback.print_exc()
        return []

# =========================
# CHAT RAG
# =========================
def compare_documents(
    user_id,
    question,
    history=None,
    selected_document=None
):

    stored_history = load_chat_history(user_id)

    if history is None:
        history = []

    history = stored_history + history

    try:

        print("PERGUNTA:", question)
        print("HISTORY:", history)

        # =========================
        # LOAD USER VECTORSTORE
        # =========================

        user_path = os.path.join(
            VECTORSTORE_DIR,
            str(user_id)
        )

        index_path = os.path.join(
            user_path,
            "index.faiss"
        )

        if not os.path.exists(index_path):
            return {
                "answer": "Nenhum documento carregado.",
                "confidence": 0,
                "sources": []
            }

        vectorstore = FAISS.load_local(
            user_path,
            embeddings,
            allow_dangerous_deserialization=True
        )

        # =========================
        # SEARCH
        # =========================

        results = vectorstore.similarity_search_with_score(
            question,
            k=10
        )

        # =========================
        # FILTER DOCUMENT
        # =========================

        if (
            selected_document
            and selected_document != "Todos"
        ):

            filtered_results = []

            for doc, score in results:

                source = doc.metadata.get("source")

                if source == selected_document:

                    filtered_results.append(
                        (doc, score)
                    )

            results = filtered_results

        print("RESULTS TYPE:", type(results))

        if results:
            print("FIRST RESULT:", results[0])

        if not results:
            return {
                "answer": "Nenhum documento encontrado.",
                "confidence": 0,
                "sources": []
            }

        # =========================
        # HYBRID SEARCH BOOST
        # =========================

        question_lower = question.lower()

        boosted_results = []

        for doc, score in results:

            content_lower = doc.page_content.lower()

            keyword_bonus = 0

            # BOOST KEYWORD MATCH
            if question_lower in content_lower:
                keyword_bonus = 0.3

            boosted_score = score - keyword_bonus

            boosted_results.append(
                (doc, boosted_score)
            )

        # SORT BEST RESULTS
        boosted_results.sort(
            key=lambda x: x[1]
        )

        results = boosted_results[:5]

        # =========================
        # CONTEXT
        # =========================

        context = ""

        for doc, score in results:

            context += f"""
Arquivo: {doc.metadata.get('source')}
Página: {doc.metadata.get('page')}

{doc.page_content}

-------------------------
"""

        # =========================
        # HISTORY
        # =========================

        chat_history = ""

        for msg in history[-6:]:

            role = msg.get("role", "")
            content = msg.get("content", "")

            chat_history += f"{role}: {content}\n"

        # =========================
        # PROMPT
        # =========================

        prompt = f"""
Você é um assistente RAG.

Use SOMENTE o contexto fornecido.

Regras:
- Não invente informações
- Seja objetivo
- Responda em português
- Considere o histórico da conversa

Histórico:
{chat_history}

Contexto:
{context}

Pergunta:
{question}
"""

        response = llm.invoke(prompt)

        # =========================
        # SAVE HISTORY
        # =========================

        history.append({
            "role": "user",
            "content": question
        })

        history.append({
            "role": "assistant",
            "content": response.content
        })

        save_chat_history(user_id, history)

        # =========================
        # SOURCES
        # =========================

        sources = []

        for doc, score in results:

            try:
                score_value = float(score)
            except Exception:
                score_value = 0.0

            # =========================
            # RELEVANCE LABEL
            # =========================

            if score_value < 0.3:
                relevance = "Alta"

            elif score_value < 0.7:
                relevance = "Média"

            else:
                relevance = "Baixa"

            sources.append({
                "source": doc.metadata.get("source"),
                "page": doc.metadata.get("page"),
                "snippet": doc.page_content[:300],
                "score": round(score_value, 2),
                "relevance": relevance
            })

        # =========================
        # CONFIDENCE
        # =========================

        try:
            best_score = float(results[0][1]) if results else 999
        except Exception:
            best_score = 999

        confidence = 1 / (1 + best_score)

        confidence = round(
            max(0.0, min(1.0, confidence)),
            2
        )

        # =========================
        # RETURN FINAL
        # =========================

        return {
            "answer": response.content,
            "confidence": confidence,
            "sources": sources
        }

    except Exception as e:

        traceback.print_exc()

        return {
            "answer": "Erro ao comparar documentos.",
            "confidence": 0,
            "sources": [],
            "error": str(e)
        }