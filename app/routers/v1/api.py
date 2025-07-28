from fastapi import APIRouter

router = APIRouter()

API_VERSION = "/api/v1"

@router.get("/health")
def health_check():
    return {"status": "ok"}

