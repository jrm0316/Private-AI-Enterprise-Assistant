from fastapi import APIRouter, Depends, Request
from auth.auth_bearer import JWTBearer, get_current_user
from services.ai_service import rebuild_vectorstore

import os
import json
import traceback

router = APIRouter()

# =========================
# LIST DOCUMENTS
# =========================
@router.get(
    "/documents",
    dependencies=[Depends(JWTBearer())]
)
def list_documents(request: Request):

    try:

        user_id = get_current_user(request)

        metadata_path = os.path.join(
            "vectorstores",
            str(user_id),
            "metadata.json"
        )

        if not os.path.exists(metadata_path):

            return {
                "success": True,
                "data": []
            }

        with open(metadata_path, "r", encoding="utf-8") as f:

            metadata = json.load(f)

        return {
            "success": True,
            "data": metadata
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }

@router.delete("/documents/{filename}")
def delete_document(
    filename: str,
    request: Request
):

    try:

        user_id = get_current_user(request)

        user_path = os.path.join(
            "vectorstores",
            str(user_id)
        )

        # =========================
        # METADATA PATH
        # =========================

        metadata_path = os.path.join(
            user_path,
            "metadata.json"
        )

        # =========================
        # DOCUMENTS PATH
        # =========================

        documents_path = os.path.join(
            user_path,
            "documents.json"
        )

        # =========================
        # REMOVE METADATA
        # =========================

        metadata = []

        if os.path.exists(metadata_path):

            with open(
                metadata_path,
                "r",
                encoding="utf-8"
            ) as f:

                metadata = json.load(f)

        metadata = [
            item for item in metadata
            if item["filename"] != filename
        ]

        with open(
            metadata_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                metadata,
                f,
                ensure_ascii=False,
                indent=2
            )

        # =========================
        # REMOVE DOCUMENT CHUNKS
        # =========================

        saved_documents = []

        if os.path.exists(documents_path):

            with open(
                documents_path,
                "r",
                encoding="utf-8"
            ) as f:

                saved_documents = json.load(f)

        saved_documents = [
            doc for doc in saved_documents
            if doc["metadata"]["source"] != filename
        ]

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
        # REBUILD VECTORSTORE
        # =========================

        rebuild_vectorstore(user_id)

        return {
            "success": True,
            "message": f"{filename} removido"
        }

    except Exception as e:

        traceback.print_exc()

        return {
            "success": False,
            "error": str(e)
        }