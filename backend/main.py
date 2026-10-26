from fastapi import FastAPI

app = FastAPI(title="Pinch")


# quick check that the server is up
@app.get("/health")
def health():
    return {"status": "ok"}
