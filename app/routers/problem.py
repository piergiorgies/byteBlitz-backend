from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(
    tags=["Problems"],
    prefix="/problems"
)

@router.get("/test", summary="Test", response_description="Test")
async def test():
    """
    Test

    Returns:
        JSONResponse: response
    """
    return JSONResponse(
        status_code=200,
        content={"detail": "Test successful"}
    )