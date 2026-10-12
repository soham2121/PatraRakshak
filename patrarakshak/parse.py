import io
import re
import zipfile

from defusedxml.ElementTree import fromstring
from pypdf import PdfReader

MAX_BYTES = 5 * 1024 * 1024
MAX_UNZIPPED = 50 * 1024 * 1024
MAX_PAGES = 300
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
# Body plus everything a human might not look at; hidden/white runs are included on purpose.
DOCX_PARTS = re.compile(r"word/(document|header\d*|footer\d*|footnotes|endnotes|comments)\.xml")


class ParseError(ValueError):
    """Message is safe to show to the user."""


def parse(filename: str, data: bytes) -> str:
    if len(data) > MAX_BYTES:
        raise ParseError("File is larger than 5 MB.")
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext == "txt":
        try:
            return data.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise ParseError("TXT files must be UTF-8 encoded.")
    if ext not in ("docx", "pdf"):
        raise ParseError("Upload a .txt, .pdf or .docx file.")
    if not data.startswith(b"PK" if ext == "docx" else b"%PDF-"):
        raise ParseError(f"This file is not a valid .{ext} file.")
    return _docx(data) if ext == "docx" else _pdf(data)


def _docx(data: bytes) -> str:
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        infos = z.infolist()
    except zipfile.BadZipFile:
        raise ParseError("This file is not a valid .docx file.")
    if sum(i.file_size for i in infos) > MAX_UNZIPPED:
        raise ParseError("DOCX content is too large once decompressed.")
    names = sorted((i.filename for i in infos if DOCX_PARTS.fullmatch(i.filename)),
                   key=lambda n: n != "word/document.xml")
    if "word/document.xml" not in names:
        raise ParseError("This file is not a valid .docx file.")
    paras = []
    try:
        for name in names:
            for p in fromstring(z.read(name)).iter(W + "p"):
                text = "".join(t.text or "" for t in p.iter(W + "t"))
                if text.strip():
                    paras.append(text)
    except Exception:
        raise ParseError("Could not read the .docx file.")
    return "\n\n".join(paras)


def _pdf(data: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(data))
        encrypted = reader.is_encrypted
        n = 0 if encrypted else len(reader.pages)
        pages = [] if encrypted or n > MAX_PAGES else [p.extract_text() or "" for p in reader.pages]
    except Exception:
        raise ParseError("Could not read the .pdf file.")
    if encrypted:
        raise ParseError("Password-protected PDFs are not supported.")
    if n > MAX_PAGES:
        raise ParseError(f"PDFs over {MAX_PAGES} pages are not supported.")
    if not any(p.strip() for p in pages):
        raise ParseError("No text found. Scanned PDFs need OCR, which PatraRakshak does not support.")
    return "\f".join(pages)
