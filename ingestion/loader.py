import re
from dataclasses import dataclass, field

from rag.config import RAW_DATA_DIR

SECTION_NAMES = ["Overview", "Eligibility", "Benefits", "Required Documents"]


@dataclass
class SchemeDoc:
    name: str
    source_url: str
    sections: dict = field(default_factory=dict)


def _parse_scheme_file(text: str) -> SchemeDoc:
    name_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    name = name_match.group(1).strip() if name_match else "Unknown Scheme"

    source_match = re.search(r"^Source:\s*(.+)$", text, re.MULTILINE)
    source_url = source_match.group(1).strip() if source_match else ""

    sections = {}
    for section_name in SECTION_NAMES:
        pattern = rf"^##\s+{re.escape(section_name)}\s*\n(.*?)(?=^##\s+|^Source:|\Z)"
        match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
        if match:
            sections[section_name] = match.group(1).strip()

    return SchemeDoc(name=name, source_url=source_url, sections=sections)


def load_schemes() -> list[SchemeDoc]:
    schemes = []
    for path in sorted(RAW_DATA_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        schemes.append(_parse_scheme_file(text))
    return schemes
