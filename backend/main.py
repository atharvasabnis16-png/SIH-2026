from fastapi import FastAPI

from routes import core, consent, audit

app = FastAPI()

app.include_router(core.router)
app.include_router(consent.router)
app.include_router(audit.router)

