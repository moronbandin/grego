import json
import unicodedata
import os
import re
from weasyprint import HTML, CSS

BASE = os.path.dirname(os.path.abspath(__file__))

VOCAB_JSON = os.path.join(BASE, "vocab.json")
PRINT_HTML = os.path.join(BASE, "vocabulario_print.html")
PRINT_OUT = os.path.join(os.path.dirname(BASE), "vocabulario.pdf")
PRINT_CSS = os.path.join(BASE, "print.css")


# Orde alfabética grega
GREEK_ORDER = [
    "Α","Β","Γ","Δ","Ε","Ζ","Η","Θ",
    "Ι","Κ","Λ","Μ","Ν","Ξ","Ο","Π",
    "Ρ","Σ","Τ","Υ","Φ","Χ","Ψ","Ω"
]


def first_letter(word):
    norm = unicodedata.normalize("NFD", word)
    for ch in norm:
        if "\u0370" <= ch <= "\u03FF":
            return unicodedata.normalize("NFC", ch.upper())
    return None


def load_vocab():
    with open(VOCAB_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def group_by_letter(entries):
    grouped = {ltr: [] for ltr in GREEK_ORDER}
    for e in entries:
        ltr = first_letter(e["greek"])
        if ltr in grouped:
            grouped[ltr].append(e)

    for ltr in grouped:
        grouped[ltr] = sorted(grouped[ltr], key=lambda x: x["greek"])
    return grouped


def build_pdf_block(grouped):
    html = ['<div class="columns">']

    for letter in GREEK_ORDER:
        items = grouped[letter]
        if not items:
            continue

        html.append(f"<h2>{letter}</h2>")

        for e in items:
            html.append(
                f'<div class="entry"><span class="gr">{e["greek"]}</span>'
                f'<span class="gl">— {e["gl"]}</span></div>'
            )

        html.append("<br>")  # pequeno espazo entre bloques

    html.append('</div>')
    return "\n".join(html)


def insert_in_html(block):
    with open(PRINT_HTML, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = re.sub(
        r"<!-- VOCABULARIO_PDF_INICIO -->(.*?)<!-- VOCABULARIO_PDF_FIN -->",
        f"<!-- VOCABULARIO_PDF_INICIO -->\n{block}\n<!-- VOCABULARIO_PDF_FIN -->",
        content,
        flags=re.DOTALL
    )

    tmp_html = PRINT_HTML.replace(".html", "_tmp.html")
    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write(new_content)

    return tmp_html


def export_pdf(html_path):
    HTML(html_path).write_pdf(PRINT_OUT, stylesheets=[CSS(PRINT_CSS)])
    print(f"✔ PDF xerado: {PRINT_OUT}")


def main():
    entries = load_vocab()
    grouped = group_by_letter(entries)
    block = build_pdf_block(grouped)
    tmp = insert_in_html(block)
    export_pdf(tmp)
    os.remove(tmp)


if __name__ == "__main__":
    main()
