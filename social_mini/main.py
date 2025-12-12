from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from social_mini.api import auth, posts
from social_mini.api import social_extra

app = FastAPI(
    title="Social Mini",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(social_extra.router)

app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")


@app.get("/")
async def root():
    return {"message": "Social Mini API", "docs": "/docs", "frontend": "/frontend"}