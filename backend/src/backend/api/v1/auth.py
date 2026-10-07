from fastapi import APIRouter

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/register")
async def register_user():
    pass


@router.post("/login")
async def login_user():
    pass


@router.post("/refresh")
async def refresh_token():
    pass


@router.get("/me")
async def me():
    pass


@router.patch("/me")
async def get_me():
    pass
