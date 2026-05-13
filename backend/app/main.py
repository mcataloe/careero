from fastapi import FastAPI

app = FastAPI(
    title="Careero API",
    description="Local-first API foundation for Careero.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
