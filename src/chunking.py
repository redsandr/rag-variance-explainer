"""
Structure-aware document chunking.

Uses recursive splitting by natural boundaries (paragraph → line → token)
to avoid cutting through tables, sentences, or paragraphs. Fixes the
table-splitting issue where fixed-size token slicing created chunks
starting with orphaned data (e.g. ") 0.3% 6.0%").

Strategy:
  1. Split by double newline (paragraph boundary)
  2. If a paragraph exceeds chunk_size, split by single newline
  3. If a line still exceeds chunk_size, token-split it (rare)
  4. Merge small segments up to chunk_size
  5. Add overlap by prepending tail of previous chunk
"""


import tiktoken

_ENCODING = tiktoken.get_encoding("cl100k_base")


def _token_len(text: str) -> int:
    return len(_ENCODING.encode(text))


def _recursive_split(text: str, chunk_size: int) -> list[str]:
    """
    Split text hierarchically: paragraphs → lines → tokens.
    Returns atomic segments each <= chunk_size.
    """
    segments = []
    for paragraph in text.split("\n\n"):
        if _token_len(paragraph) <= chunk_size:
            segments.append(paragraph)
            continue

        for line in paragraph.split("\n"):
            if _token_len(line) <= chunk_size:
                segments.append(line)
                continue

            tokens = _ENCODING.encode(line)
            for i in range(0, len(tokens), chunk_size):
                segments.append(_ENCODING.decode(tokens[i:i + chunk_size]))

    return segments


def _merge_segments(segments: list[str], chunk_size: int) -> list[str]:
    """Merge atomic segments into chunks respecting the token budget."""
    if not segments:
        return []

    chunks = []
    current = [segments[0]]

    for seg in segments[1:]:
        candidate = "\n\n".join(current + [seg])
        if _token_len(candidate) <= chunk_size:
            current.append(seg)
        else:
            chunks.append("\n\n".join(current))
            current = [seg]

    if current:
        chunks.append("\n\n".join(current))

    return chunks


def chunk_document(
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
) -> list[str]:
    """Structure-aware recursive text chunking.

    Splits by paragraph → line → token boundaries to avoid cutting
    through tables, sentences, or financial figures. Adds overlap by
    prepending the tail of the previous chunk so downstream retrieval
    doesn't lose context at boundaries.
    """
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    if not text or not text.strip():
        return []

    segments = _recursive_split(text, chunk_size)
    chunks = _merge_segments(segments, chunk_size)

    if chunk_overlap > 0 and len(chunks) > 1:
        for i in range(1, len(chunks)):
            prev_tokens = _ENCODING.encode(chunks[i - 1])
            if len(prev_tokens) > chunk_overlap:
                overlap = _ENCODING.decode(prev_tokens[-chunk_overlap:])
                chunks[i] = overlap + "\n\n" + chunks[i]

    return chunks


def count_tokens(text: str) -> int:
    return _token_len(text)
