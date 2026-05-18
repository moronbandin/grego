#!/usr/bin/env python3
"""Generate the MkDocs supplement from the source Markdown and TSV files."""

from __future__ import annotations

import csv
import re
import shutil
import unicodedata
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SOURCE_MD = ROOT / "suplemento-grego.md"
LESSONS_TSV = ROOT / "lectiones-fixed.tsv"


@dataclass(frozen=True)
class Heading:
    line: int
    level: int
    title: str


def read_source() -> list[str]:
    return SOURCE_MD.read_text(encoding="utf-8").splitlines()


def headings(lines: list[str]) -> list[Heading]:
    found: list[Heading] = []
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            found.append(Heading(index, len(match.group(1)), match.group(2)))
    return found


def section(lines: list[str], found: list[Heading], title: str) -> list[str]:
    start_heading = next(h for h in found if h.title == title)
    end = len(lines)
    for h in found:
        if h.line > start_heading.line and h.level <= start_heading.level:
            end = h.line
            break
    content = lines[start_heading.line:end]
    if content and content[0].startswith("#"):
        content[0] = re.sub(r"^#+\s+", "# ", content[0])
    return content


def combine(lines: list[str], found: list[Heading], title: str, sections: list[str]) -> str:
    body = [f"# {title}", ""]
    for name in sections:
        chunk = section(lines, found, name)
        if not chunk:
            continue
        chunk[0] = re.sub(r"^#\s+", "## ", chunk[0])
        body.extend(chunk)
        body.append("")
    return "\n".join(body).rstrip() + "\n"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def slug(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(c for c in normalized if not unicodedata.combining(c))
    ascii_text = ascii_text.lower()
    ascii_text = re.sub(r"`([^`]+)`", r"\1", ascii_text)
    ascii_text = re.sub(r"[^a-z0-9]+", "_", ascii_text)
    return ascii_text.strip("_") or "entrada"


def split_items(text: str) -> list[str]:
    text = text.replace("\u2028", " ")
    parts = re.split(r",\s+|;\s+", text)
    return [part.strip().rstrip(".") for part in parts if part.strip()]


def lesson_link(number: str, title: str) -> str:
    return f"[Lección {int(number)} — {title}](../leccions/{int(number):02d}.md)"


def make_index(title: str, intro: str, links: list[tuple[str, str]]) -> str:
    lines = [f"# {title}", "", intro, ""]
    for label, href in links:
        lines.append(f"- [{label}]({href})")
    return "\n".join(lines).rstrip() + "\n"


def build_concept_pages() -> None:
    lines = read_source()
    found = headings(lines)

    old_docs_sources = DOCS / "_fontes"
    if old_docs_sources.exists():
        shutil.rmtree(old_docs_sources)

    originals = ROOT / "_fontes"
    originals.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE_MD, originals / "suplemento-grego.md")
    shutil.copy2(LESSONS_TSV, originals / "lectiones-fixed.tsv")

    pages: dict[Path, str] = {
        DOCS / "fonetica" / "alfabeto.md": section(lines, found, "A) O alfabeto"),
        DOCS / "fonetica" / "diptongos.md": section(lines, found, "B) Os diptongos"),
        DOCS / "fonetica" / "espiritos_acentos.md": section(lines, found, "C) O espírito e os acentos"),
        DOCS / "fonetica" / "puntuacion.md": section(lines, found, "D) Signos de puntuación"),
        DOCS / "fonetica" / "acentuacion.md": section(lines, found, "II. A acentuación grega"),
        DOCS / "fonetica" / "fonetica_sintactica.md": section(lines, found, "III. Fonética sintáctica"),
        DOCS / "fonetica" / "fonetica_evolutiva.md": section(lines, found, "IV. Fonética evolutiva"),
        DOCS / "morfoloxia_nominal" / "substantivos.md": section(lines, found, "1. Declinación dos substantivos"),
        DOCS / "morfoloxia_nominal" / "adxectivos.md": section(lines, found, "2. Declinación dos adxectivos"),
        DOCS / "morfoloxia_nominal" / "participios.md": section(lines, found, "2.5. Declinación dos participios"),
        DOCS / "morfoloxia_nominal" / "pronomes_numerais.md": section(lines, found, "3. Declinación dos pronomes e dos numerais"),
        DOCS / "morfoloxia_nominal" / "adverbios.md": section(lines, found, "4. A formación de adverbios (de modo-cantidade)"),
        DOCS / "morfoloxia_verbal" / "estrutura_verbo.md": section(lines, found, "5.1. A estrutura morfolóxica do verbo regular"),
        DOCS / "morfoloxia_verbal" / "paradigmas.md": section(lines, found, "5.2. Paradigmas básicos de conxugación"),
        DOCS / "sintaxe" / "substantivo.md": section(lines, found, "1. Sintaxe do substantivo"),
        DOCS / "sintaxe" / "adxectivo.md": section(lines, found, "2. Sintaxe do adxectivo"),
        DOCS / "sintaxe" / "infinitivo.md": section(lines, found, "3.1. Sintaxe do infinitivo"),
        DOCS / "sintaxe" / "participio.md": section(lines, found, "3.2. Sintaxe do participio"),
        DOCS / "sintaxe" / "completivas.md": section(lines, found, "1. Oracións subordinadas substantivas, ou completivas"),
        DOCS / "sintaxe" / "relativas.md": section(lines, found, "2. Oracións de relativo"),
        DOCS / "sintaxe" / "adverbiais.md": section(lines, found, "3. Oracións subordinadas adverbiais"),
        DOCS / "lexico" / "semantica_gramatical.md": section(lines, found, "1. Semántica dalgunhas palabras con significado gramatical"),
        DOCS / "lexico" / "categorias_verbais.md": section(lines, found, "2. Semántica das categorías verbais inherentes"),
        DOCS / "lexico" / "etimoloxia.md": section(lines, found, "V. Etimoloxía"),
    }

    for path, content in pages.items():
        write(path, "\n".join(content).rstrip() + "\n")

    write(
        DOCS / "fonetica" / "index.md",
        make_index(
            "Fonética",
            "Sistema gráfico e fonético do grego antigo, organizado para consulta rápida.",
            [
                ("Alfabeto", "alfabeto.md"),
                ("Diptongos", "diptongos.md"),
                ("Espíritos e acentos", "espiritos_acentos.md"),
                ("Signos de puntuación", "puntuacion.md"),
                ("Acentuación", "acentuacion.md"),
                ("Fonética sintáctica", "fonetica_sintactica.md"),
                ("Fonética evolutiva", "fonetica_evolutiva.md"),
            ],
        ),
    )
    write(
        DOCS / "morfoloxia_nominal" / "index.md",
        make_index(
            "Morfoloxía nominal",
            "Declinación, adxectivos, pronomes, numerais, participios e adverbios.",
            [
                ("Substantivos", "substantivos.md"),
                ("Adxectivos", "adxectivos.md"),
                ("Participios", "participios.md"),
                ("Pronomes e numerais", "pronomes_numerais.md"),
                ("Adverbios", "adverbios.md"),
            ],
        ),
    )
    write(
        DOCS / "morfoloxia_verbal" / "index.md",
        make_index(
            "Morfoloxía verbal",
            "Estrutura do verbo grego e paradigmas básicos de conxugación.",
            [
                ("Estrutura morfolóxica do verbo regular", "estrutura_verbo.md"),
                ("Paradigmas básicos de conxugación", "paradigmas.md"),
            ],
        ),
    )
    write(
        DOCS / "sintaxe" / "index.md",
        make_index(
            "Sintaxe",
            "Funcións, concordancia e oración complexa como sistema de referencia.",
            [
                ("Sintaxe do substantivo", "substantivo.md"),
                ("Sintaxe do adxectivo", "adxectivo.md"),
                ("Sintaxe do infinitivo", "infinitivo.md"),
                ("Sintaxe do participio", "participio.md"),
                ("Completivas", "completivas.md"),
                ("Relativas", "relativas.md"),
                ("Adverbiais", "adverbiais.md"),
            ],
        ),
    )
    write(
        DOCS / "lexico" / "index.md",
        make_index(
            "Léxico e semántica",
            "Semántica gramatical, categorías verbais e repertorio etimolóxico.",
            [
                ("Semántica gramatical", "semantica_gramatical.md"),
                ("Categorías verbais", "categorias_verbais.md"),
                ("Etimoloxía", "etimoloxia.md"),
            ],
        ),
    )

    for stale in [DOCS / "fonetica" / "fenomenos_foneticos.md", DOCS / "morfoloxia" / "index.md"]:
        if stale.exists():
            stale.unlink()


def build_lessons() -> None:
    with LESSONS_TSV.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))

    lesson_links: list[tuple[str, str]] = []
    topic_lessons: dict[str, list[tuple[str, str]]] = {}
    cultural_topics: dict[str, list[tuple[str, str]]] = {}

    concept_targets = [
        ("participio", "../sintaxe/participio.md"),
        ("infinitivo", "../sintaxe/infinitivo.md"),
        ("relativ", "../sintaxe/relativas.md"),
        ("completiv", "../sintaxe/completivas.md"),
        ("adverbial", "../sintaxe/adverbiais.md"),
        ("comparativ", "../morfoloxia_nominal/adxectivos.md"),
        ("superlativ", "../morfoloxia_nominal/adxectivos.md"),
        ("adxectiv", "../morfoloxia_nominal/adxectivos.md"),
        ("pronome", "../morfoloxia_nominal/pronomes_numerais.md"),
        ("numeral", "../morfoloxia_nominal/pronomes_numerais.md"),
        ("artigo", "../morfoloxia_nominal/pronomes_numerais.md"),
        ("declinaci", "../morfoloxia_nominal/substantivos.md"),
        ("xenitivo", "../sintaxe/substantivo.md"),
        ("dativo", "../sintaxe/substantivo.md"),
        ("acusativo", "../sintaxe/substantivo.md"),
        ("nominativo", "../sintaxe/substantivo.md"),
        ("vocativo", "../sintaxe/substantivo.md"),
        ("preposici", "../lexico/semantica_gramatical.md"),
        ("conxunci", "../lexico/semantica_gramatical.md"),
        ("particula", "../lexico/semantica_gramatical.md"),
        ("aoristo", "../morfoloxia_verbal/paradigmas.md"),
        ("perfecto", "../morfoloxia_verbal/paradigmas.md"),
        ("futuro", "../morfoloxia_verbal/paradigmas.md"),
        ("imperfecto", "../morfoloxia_verbal/paradigmas.md"),
        ("presente", "../morfoloxia_verbal/paradigmas.md"),
        ("verbo", "../morfoloxia_verbal/estrutura_verbo.md"),
        ("voz", "../lexico/categorias_verbais.md"),
        ("modo", "../lexico/categorias_verbais.md"),
        ("aspecto", "../lexico/categorias_verbais.md"),
        ("tempo", "../lexico/categorias_verbais.md"),
    ]

    for row in rows:
        number = int(row["number"])
        title = row["title"].strip()
        path = DOCS / "leccions" / f"{number:02d}.md"
        lesson_links.append((f"Lección {number} — {title}", f"{number:02d}.md"))

        language_items = split_items(row["language"])
        culture_items = split_items(row["greek_world"])
        for item in language_items:
            topic_lessons.setdefault(slug(item), []).append((row["number"], title))
        for item in culture_items:
            cultural_topics.setdefault(slug(item), []).append((row["number"], title))

        supplement_lines: list[str] = []
        seen_targets: set[str] = set()
        for item in language_items:
            normalized = slug(item)
            target = None
            for needle, href in concept_targets:
                if needle in normalized:
                    target = href
                    break
            if target and target not in seen_targets:
                label = target.rsplit("/", 1)[-1].replace(".md", "").replace("_", " ").capitalize()
                supplement_lines.append(f"- [{label}]({target})")
                seen_targets.add(target)

        content = [
            f"# Lección {number} — {title}",
            "",
            row["summary"].strip(),
            "",
            "## Contidos lingüísticos",
            "",
            *(f"- {item}" for item in language_items),
            "",
            "## Ir ao suplemento",
            "",
            *(supplement_lines or ["- Consulta a busca do suplemento para localizar estes fenómenos."]),
            "",
            "## Contidos culturais",
            "",
            *(f"- {item}" for item in culture_items),
            "",
            "## Lectura",
            "",
            row["reading"].strip(),
        ]
        write(path, "\n".join(content).rstrip() + "\n")

    write(
        DOCS / "leccions" / "index.md",
        make_index(
            "Leccións",
            "Mapa docente das leccións: cada páxina resume os fenómenos lingüísticos e remite ao suplemento.",
            lesson_links,
        ),
    )

    textos_dir = DOCS / "textos"
    textos_dir.mkdir(parents=True, exist_ok=True)
    for old_page in textos_dir.glob("*.md"):
        if old_page.name != "index.md":
            old_page.unlink()

    context_lines = [
        "# Textos e contextos",
        "",
        "Índice breve de referencias culturais conectadas coas leccións. "
        "Esta sección funciona como orientación, non como corpus paralelo ao manual.",
        "",
    ]
    for row in rows:
        greek_world = row["greek_world"].strip() or "_Pendente de completar no TSV._"
        context_lines.extend(
            [
                f"## Lección {int(row['number'])} — {row['title'].strip()}",
                "",
                greek_world,
                "",
                f"[Ver mapa da lección](../leccions/{int(row['number']):02d}.md)",
                "",
            ]
        )
    write(DOCS / "textos" / "index.md", "\n".join(context_lines).rstrip() + "\n")

    backlinks = {
        DOCS / "morfoloxia_nominal" / "substantivos.md": ["declinaci", "xenitivo", "dativo", "acusativo", "nominativo", "vocativo"],
        DOCS / "morfoloxia_nominal" / "adxectivos.md": ["adxectiv", "comparativ", "superlativ"],
        DOCS / "morfoloxia_nominal" / "pronomes_numerais.md": ["pronome", "numeral", "artigo"],
        DOCS / "morfoloxia_verbal" / "paradigmas.md": ["presente", "imperfecto", "futuro", "aoristo", "perfecto"],
        DOCS / "morfoloxia_verbal" / "estrutura_verbo.md": ["verbo", "contract"],
        DOCS / "sintaxe" / "infinitivo.md": ["infinitivo"],
        DOCS / "sintaxe" / "participio.md": ["participio"],
        DOCS / "sintaxe" / "relativas.md": ["relativ"],
        DOCS / "sintaxe" / "completivas.md": ["completiv"],
        DOCS / "sintaxe" / "adverbiais.md": ["adverbial", "condicional", "final", "temporal"],
        DOCS / "lexico" / "semantica_gramatical.md": ["preposici", "conxunci", "particula"],
        DOCS / "lexico" / "categorias_verbais.md": ["voz", "modo", "aspecto", "tempo"],
    }

    for path, needles in backlinks.items():
        lessons: list[tuple[str, str]] = []
        for row in rows:
            normalized = slug(row["language"])
            if any(needle in normalized for needle in needles):
                lessons.append((row["number"], row["title"].strip()))
        if not lessons:
            continue
        text = path.read_text(encoding="utf-8").rstrip()
        text += "\n\n## Presente en\n\n"
        for num, title in lessons:
            text += f"- {lesson_link(num, title)}\n"
        write(path, text)


def build_home_and_config() -> None:
    write(
        DOCS / "index.md",
        "# Suplemento de Grego\n\n"
        "Referencia lingüística navegable para acompañar o manual de Grego. "
        "O sitio organiza conceptos, conecta leccións e ofrece unha consulta rápida sen duplicar o libro.\n\n"
        "## Entrar pola gramática\n\n"
        "- [Fonética](fonetica/index.md)\n"
        "- [Morfoloxía nominal](morfoloxia_nominal/index.md)\n"
        "- [Morfoloxía verbal](morfoloxia_verbal/index.md)\n"
        "- [Sintaxe](sintaxe/index.md)\n"
        "- [Léxico e semántica](lexico/index.md)\n\n"
        "## Entrar polo curso\n\n"
        "- [Leccións](leccions/index.md)\n"
        "- [Textos e contextos](textos/index.md)\n"
        "- [Exames PAU](pau/index.md)\n\n"
        "## Fontes\n\n"
        "A partición das páxinas conceptuais procede de `suplemento-grego.md`; "
        "as páxinas de lección proceden de `lectiones-fixed.tsv`.\n",
    )

    mkdocs = """site_name: Suplemento de Grego
site_url: https://moronbandin.github.io/grego/

theme:
  name: material
  language: gl
  features:
    - navigation.sections
    - navigation.expand
    - navigation.indexes
    - navigation.top
    - search.highlight
    - search.share
    - content.code.copy
    - toc.follow

plugins:
  - search

markdown_extensions:
  - admonition
  - tables
  - footnotes
  - attr_list
  - md_in_html
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.highlight

nav:
  - Inicio: index.md
  - Fonética:
      - fonetica/index.md
      - Alfabeto: fonetica/alfabeto.md
      - Diptongos: fonetica/diptongos.md
      - Espíritos e acentos: fonetica/espiritos_acentos.md
      - Signos de puntuación: fonetica/puntuacion.md
      - Acentuación: fonetica/acentuacion.md
      - Fonética sintáctica: fonetica/fonetica_sintactica.md
      - Fonética evolutiva: fonetica/fonetica_evolutiva.md
  - Morfoloxía nominal:
      - morfoloxia_nominal/index.md
      - Substantivos: morfoloxia_nominal/substantivos.md
      - Adxectivos: morfoloxia_nominal/adxectivos.md
      - Participios: morfoloxia_nominal/participios.md
      - Pronomes e numerais: morfoloxia_nominal/pronomes_numerais.md
      - Adverbios: morfoloxia_nominal/adverbios.md
  - Morfoloxía verbal:
      - morfoloxia_verbal/index.md
      - Estrutura do verbo: morfoloxia_verbal/estrutura_verbo.md
      - Paradigmas: morfoloxia_verbal/paradigmas.md
  - Sintaxe:
      - sintaxe/index.md
      - Substantivo: sintaxe/substantivo.md
      - Adxectivo: sintaxe/adxectivo.md
      - Infinitivo: sintaxe/infinitivo.md
      - Participio: sintaxe/participio.md
      - Completivas: sintaxe/completivas.md
      - Relativas: sintaxe/relativas.md
      - Adverbiais: sintaxe/adverbiais.md
  - Leccións:
      - leccions/index.md
      - Lección 1: leccions/01.md
      - Lección 2: leccions/02.md
      - Lección 3: leccions/03.md
      - Lección 4: leccions/04.md
      - Lección 5: leccions/05.md
      - Lección 6: leccions/06.md
      - Lección 7: leccions/07.md
      - Lección 8: leccions/08.md
      - Lección 9: leccions/09.md
      - Lección 10: leccions/10.md
      - Lección 11: leccions/11.md
      - Lección 12: leccions/12.md
      - Lección 13: leccions/13.md
      - Lección 14: leccions/14.md
      - Lección 15: leccions/15.md
      - Lección 16: leccions/16.md
      - Lección 17: leccions/17.md
      - Lección 18: leccions/18.md
      - Lección 19: leccions/19.md
      - Lección 20: leccions/20.md
      - Lección 21: leccions/21.md
      - Lección 22: leccions/22.md
      - Lección 23: leccions/23.md
      - Lección 24: leccions/24.md
      - Lección 25: leccions/25.md
  - Léxico:
      - lexico/index.md
      - Semántica gramatical: lexico/semantica_gramatical.md
      - Categorías verbais: lexico/categorias_verbais.md
      - Etimoloxía: lexico/etimoloxia.md
  - Textos e contextos:
      - textos/index.md
  - PAU:
      - Exames PAU: pau/index.md
"""
    (ROOT / "mkdocs.yml").write_text(mkdocs, encoding="utf-8")


def main() -> None:
    build_concept_pages()
    build_lessons()
    build_home_and_config()


if __name__ == "__main__":
    main()
