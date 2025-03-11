import asyncio

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.router import auth, category, tag, note
from app.settings.settings import settings
from app.service import middleware as middleware_service

app = FastAPI(title="Public notes", redoc_url=None, docs_url=settings.notes_swagger)
app.include_router(auth.router)
app.include_router(category.router)
app.include_router(tag.router)
app.include_router(note.router)



@app.middleware("http")
async def login_fails_management(request: Request, call_next):
    # Before processing the request.
    if middleware_service.is_ip_locked(ip=request.client.host):
        return JSONResponse(status_code=429, content="Too many invalid requests.",
                            headers={"Retry-After": settings.middleware_settings.ip_blocked_expires_minutes})

    response = await call_next(request)

    # After processing
    if response.status_code in {401, 403}:
        middleware_service.add_login_fail(ip=request.client.host)
        await asyncio.sleep(2)

    return response


if __name__ == "__main__":
    uvicorn.run(app)
