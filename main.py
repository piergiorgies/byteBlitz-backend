import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, contest, problem, submission, user

app = FastAPI(title="ByteBlitz", description="API for ByteBlitz", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

app.include_router(auth.router)
app.include_router(problem.router)
app.include_router(problem.judge_router)
app.include_router(contest.router)
app.include_router(submission.router)
app.include_router(user.router)

@app.get("/")
async def root():
    return {"message": "Hello ByteBlitz users!"}

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)