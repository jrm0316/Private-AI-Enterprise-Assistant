
# Private AI Enterprise Assistant

### Assistente corporativo de documentos com Inteligência Artificial

Sistema de consulta e análise de documentos desenvolvido em Python, utilizando **FastAPI, Streamlit, LangChain, FAISS e Groq**.

O projeto aplica a arquitetura **RAG (Retrieval-Augmented Generation)** para recuperar informações de documentos e gerar respostas contextualizadas por meio de modelos de linguagem (LLMs).

A aplicação possui autenticação JWT, processamento de arquivos PDF e TXT, armazenamento vetorial organizado por usuário e interface web para interação com documentos.

## 1. Visão geral

O Private AI Enterprise Assistant foi desenvolvido para explorar a aplicação de Inteligência Artificial em sistemas corporativos de gerenciamento e consulta de documentos.

A solução combina uma API REST construída com FastAPI e uma interface desenvolvida em Streamlit.

Os documentos enviados são processados, divididos em fragmentos de texto (chunks), convertidos em embeddings e armazenados em índices vetoriais FAISS.

Durante uma consulta, o sistema realiza uma busca semântica para recuperar os trechos mais relevantes e os utiliza como contexto para gerar uma resposta com auxílio de um LLM.

O projeto também implementa uma estrutura de armazenamento separada por usuário, utilizando autenticação JWT para proteger as principais operações.

## 2. Funcionalidades

### Autenticação e usuários

- Autenticação baseada em JWT.
- Proteção de endpoints com token.
- Identificação do usuário autenticado.
- Organização dos índices vetoriais por usuário.

### Gerenciamento de documentos

- Upload de arquivos PDF e TXT.
- Processamento de múltiplos arquivos.
- Extração de texto de documentos.
- Divisão automática do conteúdo em chunks.
- Geração de embeddings.
- Indexação vetorial com FAISS.
- Persistência local dos índices e dos documentos processados.
- Armazenamento de metadados dos arquivos.

### Inteligência Artificial

- Arquitetura RAG.
- Busca semântica em documentos.
- Integração com modelos de linguagem via Groq.
- Geração de respostas contextualizadas.
- Consulta a um documento selecionado ou ao conjunto de documentos.
- Retorno de referências, trechos e páginas dos documentos recuperados.
- Indicadores calculados de relevância e confiança.

### Histórico de conversas

- Estrutura de armazenamento do histórico em arquivos JSON por usuário.
- Consulta ao histórico por meio da API.
- Endpoint para limpar o histórico.
- Carregamento do histórico existente para contextualização das respostas.

**Limitação atual:** embora existam funções para salvar e carregar o histórico, a gravação automática das novas mensagens ainda não está integrada ao fluxo principal de chat.

## 3. Arquitetura

A aplicação é organizada em camadas:

**Frontend — Streamlit**

Interface web utilizada para interação com o sistema.

**Backend — FastAPI**

API REST responsável por autenticação, upload, consultas e gerenciamento dos documentos.

**Processamento de documentos**

Extração de texto e fragmentação do conteúdo utilizando bibliotecas Python e LangChain.

**Embeddings — Sentence Transformers**

Modelo utilizado:

`sentence-transformers/all-MiniLM-L6-v2`

**Banco vetorial — FAISS**

Armazenamento e recuperação semântica dos documentos.

**LLM — Groq**

Integração com o modelo:

`llama-3.1-8b-instant`

**Persistência**

Armazenamento local de índices vetoriais, documentos processados, metadados e arquivos de histórico.

## 4. Fluxo de funcionamento

### Processamento dos documentos

1. O usuário realiza a autenticação.
2. Envia um ou mais arquivos PDF ou TXT.
3. O backend extrai o conteúdo textual.
4. O texto é dividido em chunks.
5. Os chunks são convertidos em embeddings.
6. Os embeddings são armazenados no FAISS.
7. Os documentos e metadados são persistidos no diretório associado ao usuário.

### Consulta com RAG

1. O usuário envia uma pergunta.
2. O sistema identifica o usuário autenticado.
3. O índice vetorial correspondente é carregado.
4. Uma busca semântica recupera trechos relevantes.
5. Os resultados são organizados e utilizados como contexto.
6. O contexto e a pergunta são enviados ao LLM.
7. O sistema retorna a resposta, as fontes e um indicador calculado de confiança.

O prompt orienta o modelo a utilizar somente o contexto fornecido. Entretanto, essa instrução não constitui uma garantia absoluta contra respostas incorretas ou informações não fundamentadas.

## 5. Tecnologias utilizadas

| Tecnologia | Finalidade |
|---|---|
| Python | Linguagem principal |
| FastAPI | Desenvolvimento da API REST |
| Streamlit | Interface web |
| LangChain | Integração e processamento de componentes de IA |
| FAISS | Armazenamento e busca vetorial |
| Sentence Transformers | Geração de embeddings |
| Groq API | Inferência com modelos de linguagem |
| PyPDF | Extração de texto de PDFs |
| JWT | Autenticação baseada em tokens |
| JSON | Persistência de documentos, metadados e histórico |
| Docker | Arquivos de configuração para execução em contêineres |

## 6. Estrutura do projeto

```text
Private-AI-Enterprise-Assistant/
|
|-- backend/
|   |-- auth/
|   |-- routes/
|   |-- services/
|   |-- main.py
|   |-- requirements.txt
|
|-- frontend/
|   |-- streamlit_app.py
|   |-- requirements.txt
|
|-- docker-compose.yml
|-- .dockerignore
|-- .gitignore
|-- README.md
```

Durante a execução, a aplicação também utiliza diretórios locais para os índices vetoriais e o histórico de conversas.

## 7. Requisitos

Para executar o projeto localmente:

- Python 3.12 (versão utilizada nos testes locais).
- pip.
- Conexão com a internet para acessar a Groq API.
- Chave de API da Groq.
- Terminal PowerShell ou equivalente.

O download inicial do modelo de embeddings também pode exigir conexão com a internet.

## 8. Instalação

Os comandos abaixo consideram o Windows com PowerShell.

### 8.1. Obter o projeto

Faça o download do repositório pelo GitHub ou clone utilizando Git:

```bash
git clone https://github.com/jrm0316/Private-AI-Enterprise-Assistant.git
```

Entre na pasta do projeto.

### 8.2. Criar o ambiente virtual

```powershell
py -3.12 -m venv .venv
```

### 8.3. Ativar o ambiente virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

### 8.4. Instalar as dependências

```powershell
pip install -r backend\requirements.txt
pip install -r frontend\requirements.txt
```

**Observação:** nos testes locais, foi necessário utilizar `bcrypt==4.0.1` para resolver uma incompatibilidade com a biblioteca de autenticação.

Caso ocorra o mesmo problema:

```powershell
pip install bcrypt==4.0.1
```

A instalação reproduzível em um ambiente limpo ainda precisa ser validada.

## 9. Variáveis de ambiente

Na pasta principal do projeto, crie um arquivo chamado `.env`.

Configure as seguintes variáveis:

```env
GROQ_API_KEY=sua_chave_da_groq
SECRET_KEY=sua_chave_secreta_jwt
```

A variável `GROQ_API_KEY` permite acessar o modelo de linguagem.

A variável `SECRET_KEY` é utilizada para assinar os tokens JWT.

Utilize uma chave secreta forte e exclusiva para cada ambiente.

**Importante:** nunca publique o arquivo `.env` nem suas credenciais no GitHub.

## 10. Executando a aplicação

### 10.1. Iniciar o backend

Na pasta principal do projeto, com o ambiente virtual ativado:

```powershell
python -m uvicorn main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

A documentação interativa da API estará disponível em:

http://127.0.0.1:8000/docs

### 10.2. Iniciar o frontend

Abra um segundo terminal, ative o mesmo ambiente virtual e execute:

```powershell
python -m streamlit run frontend\streamlit_app.py --server.port 8501
```

A interface estará disponível em:

http://localhost:8501

Mantenha o backend em execução enquanto utiliza o frontend.

## 11. Endpoints principais

Os seguintes endpoints foram identificados no backend:

| Método | Endpoint | Finalidade |
|---|---|---|
| POST | `/upload` | Processar e indexar documentos |
| POST | `/chat` | Consultar documentos com IA |
| GET | `/history` | Consultar o histórico |
| DELETE | `/clear-history` | Limpar o histórico |

Essas rotas utilizam autenticação JWT.

Outros endpoints podem ser consultados na documentação automática do FastAPI, disponível em `/docs`.

## 12. Persistência e organização por usuário

O serviço principal de IA organiza os índices FAISS no diretório:

```text
vectorstores/
    usuario_1/
        index.faiss
        index.pkl
        documents.json
        metadata.json

    usuario_2/
        index.faiss
        index.pkl
        documents.json
        metadata.json
```

Essa organização representa a estrutura utilizada pelo código, não uma listagem de usuários reais.

O histórico é organizado separadamente:

```text
chat_history/
    usuario_1.json
    usuario_2.json
```

A separação de diretórios por usuário está implementada. Uma auditoria completa de isolamento de dados, permissões e segurança ainda não foi realizada.

## 13. Limitações conhecidas

O projeto encontra-se em desenvolvimento e possui pontos de melhoria identificados durante a revisão do código:

- Integrar a gravação automática de novas mensagens ao histórico do chat.
- Validar o resultado da indexação antes de confirmar o sucesso do upload.
- Corrigir a quantidade de páginas registrada nos metadados.
- Tratar o reenvio de documentos com nomes repetidos para evitar duplicações.
- Revisar o carregamento de índices FAISS e os riscos de desserialização.
- Revisar o gerenciamento de credenciais e remover a exposição de segredos nos logs.
- Substituir credenciais demonstrativas antes de qualquer implantação real.
- Validar a instalação das dependências e a execução com Docker em ambiente limpo.
- Ampliar os testes automatizados e as verificações de segurança.

## 14. Objetivo do projeto

O Private AI Enterprise Assistant é um projeto de portfólio voltado ao desenvolvimento Backend Python e à aplicação prática de Inteligência Artificial.

O projeto demonstra conceitos e implementações relacionados a:

- Desenvolvimento de APIs REST com FastAPI.
- Autenticação JWT.
- Processamento e persistência de documentos.
- Busca semântica e bancos vetoriais.
- Arquitetura RAG.
- Integração com LLMs.
- Organização de serviços e componentes de backend.
- Construção de interfaces com Streamlit.

O sistema é uma implementação de estudo e portfólio, não uma solução corporativa auditada ou pronta para produção.

## 15. Autor

Desenvolvido por **Juliano Madeira**.

GitHub: https://github.com/jrm0316
