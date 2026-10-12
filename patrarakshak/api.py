from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles

from . import detector
from .parse import MAX_BYTES, ParseError, parse

app = FastAPI(title="PatraRakshak")
score_batch, meta = detector.load()


@app.post("/api/v1/scan")
def scan(text: str | None = Form(None), file: UploadFile | None = File(None)):
    # Plain def: FastAPI runs it in a worker thread, so CPU-bound scoring doesn't block the event loop.
    # Nothing here logs or stores the submitted text.
    if (text is None) == (file is None):
        raise HTTPException(422, "Send exactly one of 'text' or 'file'.")
    name, kind = None, "text"
    if file is not None:
        name = file.filename or ""
        kind = name.rsplit(".", 1)[-1].lower()
        try:
            text = parse(name, file.file.read(MAX_BYTES + 1))
        except ParseError as e:
            raise HTTPException(422, str(e))
    if not text.strip():
        raise HTTPException(422, "No text to scan.")
    result = detector.scan(text, score_batch, meta)
    for seg in result["segments"]:
        seg["page"] = text.count("\f", 0, seg["start"]) + 1 if kind == "pdf" else None
    result["source"] = {"kind": kind, "name": name, "chars": len(text)}
    return result


if Path("web/dist").is_dir():
    app.mount("/", StaticFiles(directory="web/dist", html=True), name="web")
