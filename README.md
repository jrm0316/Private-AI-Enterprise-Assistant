# Private-AI-Enterprise-Assistant
Assistente corporativo de documentos com IA, equipado com busca semântica, memória persistente e arquitetura multiusuário.

2.) Visão geral
  Private AI Enterprise Assistant é um assistente corporativo de documentos com IA, desenvolvido com FastAPI, Streamlit, LangChain e FAISS. O sistema permite que múltiplos usuários façam upload de arquivos PDF e TXT, realizem busca semântica e interajam com os documentos através de um chat contextual com IA. Ele utiliza embeddings e busca vetorial para fornecer respostas precisas baseadas apenas no conteúdo enviado pelo usuário. O projeto inclui autenticação JWT, memória persistente de conversas, armazenamento vetorial multiusuário e arquitetura REST API. Também foi adicionado suporte a Docker para simplificar o deploy e a portabilidade do ambiente.

3.) Features          
• Login JWT            
• Multiusuário            
• Upload de PDFs/TXT                
• RAG com FAISS                  
• Busca semântica                
• Chat contextual             
• Memória persistente                       
• Histórico de conversa                     
• API REST FastAPI                   
• Frontend Streamlit             
• Docker support              
• IA local opcional           

4.) Arquitetura         
Frontend:                 
• Streamlit               
  
Backend:               
• FastAPI                    
  
IA:                  
  •	LangChain                   
  •	Groq                   
  •	Sentence Transformers                 
  
Banco vetorial:                   
  •	FAISS                     


5.) Fluxo do sistema               
Upload PDF                       
↓                                 
Chunking                       
↓                               
Embeddings                         
↓                                
FAISS                             
↓                          
Busca semântica                       
↓                               
LLM                           
↓                                    
Resposta contextual                           


6.) Tecnologias usadas                   
•	Python                           
•	FastAPI                              
•	Streamlit                             
•	LangChain                               
•	FAISS                                    
•	Docker                                           
•	JWT                                      
•	Sentence Transformers                             
•	Groq API                                     

7.) Estrutura do projeto                    
backend/                           
frontend/                              
routes/                              
services/                              
vectorstores/                            
chat_history/
