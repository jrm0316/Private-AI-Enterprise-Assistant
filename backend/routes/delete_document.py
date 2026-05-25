from fastapi import APIRouter, Depends, Request
from auth.auth_bearer import JWTBearer, get_current_user

from services.ai_service import rebuild_vectorstore

import os
import json

router = APIRouter()

# =========================
# DELETE DOCUMENT
# =========================
@router.delete(
    "/documents/{filename}",
    dependencies=[Depends(JWTBearer())]
)
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

        metadata_path = os.path.join(
            user_path,
            "metadata.json"
        )

        documents_path = os.path.join(
            user_path,
            "documents.json"
        )

        # =========================
        # REMOVE METADATA
        # =========================

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

        if os.path.exists(documents_path):

            with open(
                documents_path,
                "r",
                encoding="utf-8"
            ) as f:

                docs = json.load(f)

            docs = [
                doc for doc in docs
                if doc["metadata"]["source"] != filename
            ]

            with open(
                documents_path,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    docs,
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

        return {
            "success": False,
            "error": str(e)
        }