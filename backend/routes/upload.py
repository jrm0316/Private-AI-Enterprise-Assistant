from fastapi import APIRouter, UploadFile, File, Depends
from pypdf import PdfReader
import json
import os
from datetime import datetime

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from fastapi import Request

from auth.auth_bearer import (
    JWTBearer,
    get_current_user
)

from services.ai_service import update_vectorstore

import traceback

print("UPLOAD.PY CARREGADO")

router = APIRouter()


@router.post("/upload", dependencies=[Depends(JWTBearer())])
async def upload_files(
    request: Request,
    files: list[UploadFile] = File(...)
):

    try:

        user_id = get_current_user(request)
        print("USER ID:", user_id)

        print("UPLOAD INICIOU")

        all_documents = []

        # =========================
        # PROCESS FILES
        # =========================

        for file in files:

            if file.filename.endswith(".pdf"):

                reader = PdfReader(file.file)

                for page_number, page in enumerate(reader.pages):

                    text = page.extract_text()

                    if text:

                        all_documents.append(
                            Document(
                                page_content=text,
                                metadata={
                                    "source": file.filename,
                                    "page": page_number + 1
                                }
                            )
                        )

            elif file.filename.endswith(".txt"):

                text = (await file.read()).decode("utf-8")

                all_documents.append(
                    Document(
                        page_content=text,
                        metadata={
                            "source": file.filename,
                            "page": 1
                        }
                    )
                )

            else:

                return {
                    "success": False,
                    "error": f"Formato não suportado: {file.filename}"
                }

        # =========================
        # SPLIT
        # =========================

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150
        )

        final_chunks = splitter.split_documents(all_documents)

        # =========================
        # COUNT CHUNKS
        # =========================

        chunk_count_by_file = {}

        for chunk in final_chunks:

            filename = chunk.metadata.get("source")

            if filename not in chunk_count_by_file:
                chunk_count_by_file[filename] = 0

            chunk_count_by_file[filename] += 1

        # =========================
        # UPDATE VECTORSTORE
        # =========================

        update_vectorstore(
            user_id,
            final_chunks
        )

        user_path = os.path.join(
        "vectorstores",
        str(user_id)
        )

        # =========================
        # SAVE DOCUMENTS
        # =========================

        documents_path = os.path.join(
            user_path,
            "documents.json"
        )

        saved_documents = []

        # LOAD OLD
        if os.path.exists(documents_path):

            with open(
                documents_path,
                "r",
                encoding="utf-8"
            ) as f:

                saved_documents = json.load(f)

        # ADD NEW
        for chunk in final_chunks:

            saved_documents.append({
                "content": chunk.page_content,
                "metadata": chunk.metadata
            })

        # SAVE
        with open(
            documents_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                saved_documents,
                f,
                ensure_ascii=False,
                indent=2
            )

        # =========================
        # SAVE METADATA
        # =========================

        user_path = os.path.join(
            "vectorstores",
            str(user_id)
        )

        os.makedirs(user_path, exist_ok=True)

        metadata_path = os.path.join(
            user_path,
            "metadata.json"
        )

        metadata = []

        # LOAD OLD METADATA
        if os.path.exists(metadata_path):

            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

        # ADD OR UPDATE FILES
        for file in files:

            # REMOVE DUPLICADOS
            metadata = [
                item for item in metadata
                if item["filename"] != file.filename
            ]

            metadata.append({
                "filename": file.filename,
                "uploaded_at": str(datetime.now()),
                "chunks": chunk_count_by_file.get(
                    file.filename,
                    0
                ),
                "pages": 1
            })

        # SAVE FILE
        with open(metadata_path, "w", encoding="utf-8") as f:

            json.dump(
                metadata,
                f,
                ensure_ascii=False,
                indent=2
            )

        print("METADATA SALVA")
        print("UPLOAD OK")

        return {
            "success": True,
            "message": f"{len(files)} arquivos processados com sucesso",
            "chunks": len(final_chunks)
        }       
    except Exception as e:

        traceback.print_exc()

        return {
            "success": False,
            "error": str(e)
        }