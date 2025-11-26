import json
import unicodedata
import re
import os

# ======================================================
# 1. RUTAS CORRECTAS
# ======================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))                  # .../.assets
VOCAB_PATH = os.path.join(BASE_DIR, "vocab.json")                      # vocab.json
VOCAB_HTML_PATH = os.path.join(os.path.dirname(BASE_DIR), "vocabulario.html")  # ../vocabulario.html


# ======================================================
# 2. ORDENACIÓN ALFABÉTICA GREGA
# ======================================================

GREEK_ORDER = [
    "Α","Β","Γ","Δ","Ε","Ζ","Η","Θ",
    "Ι","Κ","Λ","Μ","Ν","Ξ","Ο","Π",
    "Ρ","Σ","Τ","Υ","Φ","Χ","Ψ","Ω"
]

# ids en latín (para href e id da sección)
LATIN_IDS = {
    "Α":"alpha","Β":"beta","Γ":"gamma","Δ":"delta",
    "Ε":"epsilon","Ζ":"zeta","Η":"eta","Θ":"theta",
    "Ι":"iota","Κ":"kappa","Λ":"lambda","Μ":"mu",
    "Ν":"nu","Ξ":"xi","Ο":"omicron","Π":"pi",
    "Ρ":"rho","Σ":"sigma","Τ":"tau","Υ":"upsilon",
    "Φ":"phi","Χ":"chi","Ψ":"psi","Ω":"omega"
}


# ======================================================
# 3. Detectar primeira letra (sen acentos)
# ======================================================

def first_letter(word):
    norm = unicodedata.normalize("NFD", word)
    for ch in norm:
        # letra grega?
        if "\u0370" <= ch <= "\u03FF":   
            return unicodedata.normalize("NFC", ch.upper())
    return None


# ======================================================
# 4. Cargar vocab
# ======================================================

def load_vocab(path=VOCAB_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ======================================================
# 5. Agrupar por letra inicial
# ======================================================

def group_by_letter(entries):
    grouped = {ltr: [] for ltr in GREEK_ORDER}
    for e in entries:
        ltr = first_letter(e["greek"])
        if ltr in grouped:
            grouped[ltr].append(e)

    for ltr in grouped:
        grouped[ltr] = sorted(grouped[ltr], key=lambda x: x["greek"])
    return grouped


# ======================================================
# 6. Nomes das letras
# ======================================================

NAMES = {
    "Α": "ἄλφα",  "Β": "βῆτα",  "Γ": "γάμμα",     "Δ": "δέλτα",
    "Ε": "ἒ ψιλόν","Ζ": "ζῆτα", "Η": "ἦτα",       "Θ": "θῆτα",
    "Ι": "ἰῶτα",  "Κ": "κάππα","Λ": "λάμβδα",    "Μ": "μῦ",
    "Ν": "νῦ",    "Ξ": "ξῖ",   "Ο": "ὂ μικρόν",  "Π": "πῖ",
    "Ρ": "ῥῶ",    "Σ": "σῖγμα","Τ": "ταῦ",       "Υ": "ὖ ψιλόν",
    "Φ": "φῖ",    "Χ": "χῖ",   "Ψ": "ψῖ",        "Ω": "ὦ μέγα"
}


# ======================================================
# 7. Construír HTML dunha letra
# ======================================================

def build_section(letter, items):
    latin_id = LATIN_IDS[letter]
    html = [f'<section id="{latin_id}" class="letter-block">']
    html.append(f'<h2>{letter} — {NAMES[letter]}</h2>')
    html.append('<ul class="vocab">')

    for e in items:
        html.append(
            f'<li><span class="gr">{e["greek"]}</span> — '
            f'<span class="gl">{e["gl"]}</span></li>'
        )

    html.append('</ul></section>')
    return "\n".join(html)


# ======================================================
# 8. Construír TODAS as seccións
# ======================================================

def build_all_sections(grouped):
    return "\n\n".join(build_section(ltr, grouped[ltr]) for ltr in GREEK_ORDER)


# ======================================================
# 9. Inserir no HTML
# ======================================================

def insert_into_page(sections_html, page_path=VOCAB_HTML_PATH):
    with open(page_path, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = re.sub(
        r"<!-- VOCABULARIO AUTOGENERADO INICIO -->(.*?)<!-- VOCABULARIO AUTOGENERADO FIN -->",
        f"<!-- VOCABULARIO AUTOGENERADO INICIO -->\n{sections_html}\n<!-- VOCABULARIO AUTOGENERADO FIN -->",
        content,
        flags=re.DOTALL
    )

    with open(page_path, "w", encoding="utf-8") as f:
        f.write(new_content)


# ======================================================
# MAIN
# ======================================================

def main():
    entries = load_vocab()
    grouped = group_by_letter(entries)
    sections_html = build_all_sections(grouped)
    insert_into_page(sections_html)
    print("✔ Vocabulario actualizado en vocabulario.html")

if __name__ == "__main__":
    main()
