import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI

from src.config import settings



sys.path.append(str(Path(__file__).parent.parent))

from src.api.auth import router as router_auth

print(f"{settings.DB_URL=}")

app = FastAPI()

app.include_router(router_auth)



if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)