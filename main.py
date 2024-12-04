import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.logger import LoggingMiddleware, get_logger
from app.routers import auth, contest, problem, submission, user, general

app = FastAPI(title="ByteBlitz", description="API for ByteBlitz", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

app.add_middleware(LoggingMiddleware)


app.include_router(auth.router)
app.include_router(problem.router)
app.include_router(problem.judge_router)
app.include_router(contest.router)
app.include_router(submission.router)
app.include_router(user.router)
app.include_router(general.router)

@app.get("/")
async def root(logger = Depends(get_logger)):
    return {"message": "Hello ByteBlitz users!"}

if __name__ == '__main__':
    uvicorn.run("main:app", host="localhost", port=9000, reload=True)
