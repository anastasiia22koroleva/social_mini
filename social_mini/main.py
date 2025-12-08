from fastapi import FastAPI
from social_mini.api import auth, posts

app = FastAPI(title="Social Mini API", version="1.0.0")

app.include_router(auth.router)
app.include_router(posts.router)

@app.get("/")
def root():
    return {"message": "Social Mini API is running!"}