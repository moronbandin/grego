import os
import shutil
import re

SRC = "src"
BUILD = "build"
TEMPLATE = "templates/base.html"

# ========================================================
# 1. Cargar template base
# ========================================================
with open(TEMPLATE, "r", encoding="utf-8") as f:
    BASE = f.read()


# ========================================================
# 2. Ler meta-title dun ficheiro HTML
# ========================================================
def extract_title(filepath):
    """
    Busca no ficheiro HTML unha liña como:
       <meta name="title" content="Algo bonito">
    Se existe, devolve "Algo bonito".
    Senón, devolve o nome do ficheiro sen .html.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        m = re.search(r'<meta\s+name="title"\s+content="([^"]+)"', content)
        if m:
            return m.group(1)

    except:
        pass

    return os.path.basename(filepath).replace(".html", "")


# ========================================================
# 3. Construír sidebar automática
# ========================================================
def build_sidebar():
    html = "<div class='sidebar-title'>Suplemento</div>\n<nav class='sidebar-nav'>\n"

    for root, dirs, files in sorted(os.walk(SRC)):

        # ---- EXCLUSIÓNS ----
        # 1) Ignorar carpeta CSS
        if "css" in root:
            continue

        # 2) Ignorar calquera carpeta que comece con punto
        parts = root.split(os.sep)
        if any(p.startswith(".") for p in parts):
            continue

        # ---- NOME DA SECCIÓN ----
        level = root.replace(SRC, "").strip("/")
        if level:
            section = os.path.basename(root)
            html += f"<div class='sidebar-section'>{section.capitalize()}</div>\n"

        # ---- ENGADIR PÁXINAS ----
        for file in sorted(files):
            if file.endswith(".html"):

                # Construír ruta relativa visible na web
                filepath = os.path.join(root, file)
                rel = filepath.replace(SRC + "/", "")

                # Ler título HUMANO dende meta
                title = extract_title(filepath)

                html += f"<a href='/{rel}'>{title}</a>\n"

    html += "</nav>"
    return html


SIDEBAR = build_sidebar()


# ========================================================
# 4. Preparar carpeta build desde cero
# ========================================================
if os.path.exists(BUILD):
    shutil.rmtree(BUILD)
os.makedirs(BUILD)


# ========================================================
# 5. Copiar arquivos NON-HTML (PDF, imaxes, etc.)
# ========================================================
for root, dirs, files in os.walk(SRC):

    # Excluir carpetas ocultas
    parts = root.split(os.sep)
    if any(p.startswith(".") for p in parts):
        continue

    for file in files:
        if not file.endswith(".html"):
            src = os.path.join(root, file)
            dst = os.path.join(BUILD, src.replace(SRC + "/", ""))

            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)


# ========================================================
# 6. Compilar HTML usando o template
# ========================================================
for root, dirs, files in os.walk(SRC):
    for file in files:

        if not file.endswith(".html"):
            continue

        # Excluir carpetas ocultas
        parts = root.split(os.sep)
        if any(p.startswith(".") for p in parts):
            continue

        src_path = os.path.join(root, file)
        rel_path = src_path.replace(SRC + "/", "")
        dst_path = os.path.join(BUILD, rel_path)

        with open(src_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Nivel de profundidade
        depth = rel_path.count("/")
        root_prefix = "../" * depth

        # Título da páxina (non sidebar)
        page_title = extract_title(src_path)

        # Inxectar template
        page = BASE.replace("{{ content }}", content)
        page = page.replace("{{ title }}", page_title)
        page = page.replace("{{ sidebar }}", SIDEBAR)
        page = page.replace("{{ root }}", root_prefix)

        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        with open(dst_path, "w", encoding="utf-8") as f:
            f.write(page)

print("✔️ Web construída correctamente en /build")
