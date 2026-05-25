from fastapi import FastAPI
from routes.chat import router as chat_router
from routes.upload import router as upload_router
from routes.analyze import router as analyze_router
from routes.match import router as match_router
from routes.compare import router as compare_router
from routes import interview
from routes.compare_docs import router as compare_docs_router
from routes.match_score import router as match_score_router
from routes.auth import router as auth_router
from routes.history import router as history_router
from routes.documents import router as documents_router
from routes.delete_document import router as delete_document_router

app = FastAPI()

app.include_router(chat_router)
app.include_router(upload_router)
app.include_router(analyze_router)
app.include_router(match_router)
app.include_router(compare_router)
app.include_router(interview.router)
app.include_router(compare_docs_router)
app.include_router(match_score_router)
app.include_router(auth_router)
app.include_router(history_router)
app.include_router(documents_router)
app.include_router(delete_document_router)