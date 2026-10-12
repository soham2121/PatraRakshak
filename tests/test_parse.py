import io
import zipfile
from pathlib import Path

import pytest
from pypdf import PdfWriter

from patrarakshak.parse import ParseError, parse

FIX = Path(__file__).parent / "fixtures"
NS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'


def para(text: str, hidden: bool = False) -> str:
    rpr = "<w:rPr><w:vanish/></w:rPr>" if hidden else ""
    return f"<w:p><w:r>{rpr}<w:t>{text}</w:t></w:r></w:p>"


def make_docx(body: str, extra: dict[str, str] | None = None) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("word/document.xml", f"<w:document {NS}><w:body>{body}</w:body></w:document>")
        for name, xml in (extra or {}).items():
            z.writestr(name, xml)
    return buf.getvalue()


def test_txt_utf8():
    assert parse("a.txt", "héllo".encode()) == "héllo"


def test_txt_not_utf8():
    with pytest.raises(ParseError, match="UTF-8"):
        parse("a.txt", b"\xff\xfe\x00bad")


def test_docx_reads_headers_and_hidden_runs():
    data = make_docx(para("Visible body.") + para("Secret instruction.", hidden=True),
                     {"word/header1.xml": f"<w:hdr {NS}>{para('Header text.')}</w:hdr>"})
    text = parse("a.docx", data)
    assert "Visible body." in text and "Secret instruction." in text and "Header text." in text


def test_docx_zip_bomb_rejected():
    data = make_docx(" " * 60_000_000)
    assert len(data) < 5 * 1024 * 1024
    with pytest.raises(ParseError, match="too large"):
        parse("a.docx", data)


def test_extension_content_mismatch():
    with pytest.raises(ParseError, match="not a valid .pdf"):
        parse("a.pdf", make_docx(para("x")))


def test_unsupported_type():
    with pytest.raises(ParseError, match="Upload a .txt"):
        parse("a.exe", b"MZ")


def test_oversized():
    with pytest.raises(ParseError, match="5 MB"):
        parse("a.txt", b"a" * (5 * 1024 * 1024 + 1))


def test_pdf_pages_separated_by_form_feed():
    text = parse("sample.pdf", (FIX / "sample.pdf").read_bytes())
    page2 = text.split("\f")[1]
    assert "Ignore previous instructions" in page2


def test_scanned_pdf_explains_ocr():
    with pytest.raises(ParseError, match="OCR"):
        parse("scanned.pdf", (FIX / "scanned.pdf").read_bytes())


def test_encrypted_pdf_rejected():
    w = PdfWriter()
    w.add_blank_page(100, 100)
    w.encrypt("pw")
    buf = io.BytesIO()
    w.write(buf)
    with pytest.raises(ParseError, match="Password"):
        parse("a.pdf", buf.getvalue())
