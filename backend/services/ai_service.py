import os
import json
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from services.vector_store import search

load_dotenv()

# LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# CONFIG RAG
TOP_K_CONTEXT = 1  # usa só o melhor chunk


# =========================================================
# 🔵 FUNÇÃO AUXILIAR - LIMPAR JSON DO LLM
# =========================================================
def extract_json(text: str):
    try:
        # remove ```json ... ```
        text = re.sub(r"```json|```", "", text).strip()

        # pega só o JSON
        start = text.find("{")
        end = text.rfind("}") + 1
        json_str = text[start:end]

        return json.loads(json_str)

    except Exception:
        return {
            "erro": "Falha ao gerar JSON",
            "raw": text
        }

# =========================================================
# 🔵 RAG CHAT
# =========================================================
def chat_with_resume(question: str):
    results = search(question, k=5)

    # 🔴 nenhum resultado
    if not results:
        return {
            "answer": "Não encontrei informação relevante no documento.",
            "sources": []
        }

    # BLOQUEIO INTELIGENTE (ESSENCIAL)
    best_score = float(results[0][1])

    if best_score > 0.8:
        return {
            "answer": "Não encontrei informação relevante no documento.",
            "sources": []
        }

    # 🟢 pega só os melhores
    TOP_K_CONTEXT = 3
    top_results = results[:TOP_K_CONTEXT]

    # 🟢 monta contexto
    context_parts = []
    for doc, _ in top_results:
        if hasattr(doc, "page_content"):
            context_parts.append(doc.page_content)
        else:
            context_parts.append(str(doc))

    context = "\n\n".join(context_parts)

    # 🟢 monta fontes
    sources = []
    for doc, score in top_results:
        content = doc.page_content if hasattr(doc, "page_content") else str(doc)

        sources.append({
            "content": content,
            "score": float(score)
        })

    # prompt melhorado
    prompt = f"""
Responda SOMENTE com base no contexto abaixo.
Cite apenas informações presentes no contexto.
Se não encontrar resposta, diga exatamente:
"Não encontrei informação relevante no documento."

Contexto:
{context}

Pergunta:
{question}
"""

    response = llm.invoke(prompt)

    return {
        "answer": response.content,
        "sources": sources
    }


# =========================================================
# 🔵 ANALISADOR DE CURRÍCULO
# =========================================================
def analyze_resume(text: str):
    prompt = f"""
Você é um analisador de currículos.

RESPONDA APENAS EM JSON VÁLIDO.
NÃO escreva explicações.
NÃO use markdown.
NÃO escreva nada antes ou depois do JSON.

Formato obrigatório:
{{
  "nivel": "Júnior | Pleno | Senior",
  "pontos_fortes": ["..."],
  "pontos_fracos": ["..."],
  "sugestoes": ["..."]
}}

Se o texto for inválido, ainda assim retorne JSON.

CURRÍCULO:
{text}
"""

    response = llm.invoke(prompt)

    return extract_json(response.content)

# =========================================================
# 🔵 COMPARAR CURRÍCULO COM VAGA
# =========================================================
def compare_with_job(resume: str, job: str):
    # 🔥 pesos (pode evoluir depois)
    weights = {
        "python": 30,
        "fastapi": 25,
        "docker": 20,
        "testes": 15,
        "aws": 10
    }

    resume_lower = resume.lower()
    job_lower = job.lower()

    match_score = 0

    pontos_fortes = []
    faltando_obrigatorio = []
    faltando_desejavel = []

    explicacao = []

    for skill, weight in weights.items():
        if skill in job_lower:
            if skill in resume_lower:
                match_score += weight
                pontos_fortes.append(skill)
                explicacao.append(f"{skill} (+{weight}%)")
            else:
                # 🔥 regra simples: obrigatório vs desejável
                if skill in ["python", "fastapi", "docker"]:
                    faltando_obrigatorio.append(skill)
                else:
                    faltando_desejavel.append(skill)

    # 🔥 limitar em 100
    match_score = min(match_score, 100)

    resumo = (
        f"Match baseado em pesos. Pontos fortes: {', '.join(pontos_fortes)}. "
        f"Faltando: {', '.join(faltando_obrigatorio + faltando_desejavel)}."
    )

    return {
        "match": match_score,
        "faltando_obrigatorio": faltando_obrigatorio,
        "faltando_desejavel": faltando_desejavel,
        "pontos_fortes": pontos_fortes,
        "explicacao": explicacao,
        "resumo": resumo
    }