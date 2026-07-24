from fastapi import APIRouter, Request, Depends
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.user import User

config = Config(".env")
oauth = OAuth(config)

oauth.register(
    name="google",
    client_id=config("GOOGLE_CLIENT_ID"),
    client_secret=config("GOOGLE_CLIENT_SECRET"),
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    client_kwargs={"scope": "openid email profile"},
)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/login")
async def login(request: Request):
    redirect_uri = config("REDIRECT_URI")
    # redirect_uri = request.url_for("auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    # Get token from Google
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.parse_id_token(request, token)

    google_sub = user_info["sub"]   # matches your column
    email = user_info["email"]
    name = user_info.get("name")

    # 🔎 Check if user already exists by google_sub
    db_user = db.query(User).filter(User.google_sub == google_sub).first()
    print(db_user)
    if not db_user:
        db_user = User(
            email=email,
            full_name=name,
            google_sub=google_sub,
            is_active=True,
            is_admin=False
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        print("New user created:", db_user.id, db_user.email, db_user.google_sub)
    return {
        "message": "Login successful",
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "is_active": db_user.is_active,
            "is_admin": db_user.is_admin,
        },
    }
