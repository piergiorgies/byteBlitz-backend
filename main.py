import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from app.logger import LoggingMiddleware, get_logger
from app.routers import auth, contest, problem, submission, user, general, judge
from app.routers.admin import contest as contest_admin, problem as problem_admin, user as user_admin, judge as judge_admin
from app.config import settings

app = FastAPI(title="ByteBlitz", description="API for ByteBlitz", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.APP_DOMAIN],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)
app.add_middleware(ProxyHeadersMiddleware)
app.add_middleware(LoggingMiddleware)

# user routers
app.include_router(auth.router)
app.include_router(problem.router)
app.include_router(contest.router)
app.include_router(submission.router)
app.include_router(user.router)

# general routers
app.include_router(general.ws)
app.include_router(general.router)

# admin routers
app.include_router(contest_admin.router)
app.include_router(problem_admin.router)
app.include_router(user_admin.router)
app.include_router(judge_admin.router)

# judge routers
app.include_router(judge.router)


@app.get("/")
async def root(logger = Depends(get_logger)):
    return {"message": "Hello ByteBlitz users!"}


if __name__ == "__main__":

    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True
    )

