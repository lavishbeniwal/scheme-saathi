from dataclasses import dataclass

from ingestion.loader import SchemeDoc


@dataclass
class Chunk:
    text: str
    scheme_name: str
    section: str
    source_url: str


def chunk_scheme(scheme: SchemeDoc) -> list[Chunk]:
    chunks = []
    for section, content in scheme.sections.items():
        if not content:
            continue
        text = f"{scheme.name} — {section}: {content}"
        chunks.append(
            Chunk(
                text=text,
                scheme_name=scheme.name,
                section=section,
                source_url=scheme.source_url,
            )
        )
    return chunks


def chunk_schemes(schemes: list[SchemeDoc]) -> list[Chunk]:
    chunks = []
    for scheme in schemes:
        chunks.extend(chunk_scheme(scheme))
    return chunks
