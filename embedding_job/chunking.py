"""Markdown-aware chunking: split along section headers first (each section
is usually a coherent topic - one formation option, one player note, etc.),
then fall back to paragraph-splitting only if a section is too long for a
single embedding to represent well.
"""
import re

MAX_CHARS = 1200


def chunk_markdown(text: str, max_chars: int = MAX_CHARS) -> list:
    sections = re.split(r"\n(?=#{1,3} )", text.strip())
    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        if len(section) <= max_chars:
            chunks.append(section)
            continue

        paragraphs = [p.strip() for p in section.split("\n\n") if p.strip()]
        buf = ""
        for para in paragraphs:
            if buf and len(buf) + len(para) + 2 > max_chars:
                chunks.append(buf)
                buf = para
            else:
                buf = f"{buf}\n\n{para}" if buf else para
        if buf:
            chunks.append(buf)
    return chunks
