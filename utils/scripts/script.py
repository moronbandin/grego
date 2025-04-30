import os
import re

# Ruta base das unidades
base_dir = "UNIDADES"
output_file = "contidos_actividades_unidades.md"
unidades_filtradas = []

# Só imos coller as carpetas 1 a 15
numeros_validos = [str(i) for i in range(1, 16)]

# Percorrer os subdirectorios
for raiz, dirs, files in os.walk(base_dir):
    for nome_dir in dirs:
        if nome_dir in numeros_validos:
            index_path = os.path.join(raiz, nome_dir, "index.md")
            if os.path.isfile(index_path):
                with open(index_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Título da unidade
                match_título = re.search(r"## Unidade [0-9]+\. .*", content)
                título = match_título.group(0).strip() if match_título else f"Unidade {nome_dir}"

                # Extraer seccións de contidos e actividades
                contidos = re.search(r"### Contidos\n.*?(?=\n### |\Z)", content, flags=re.DOTALL)
                actividades = re.search(r"### Actividades de ensino-aprendizaxe\n.*?(?=\n### |\Z)", content, flags=re.DOTALL)

                # Compoñer bloque se existen
                bloque = [título]
                if contidos:
                    bloque.append(contidos.group(0).strip())
                if actividades:
                    bloque.append(actividades.group(0).strip())

                # Engadir ao resultado se hai algo
                if len(bloque) > 1:
                    unidades_filtradas.append("\n\n".join(bloque))

# Escribir o ficheiro final
with open(output_file, "w", encoding="utf-8") as out:
    out.write("# 📘 Contidos e actividades das unidades 1 a 15\n\n")
    out.write("\n\n---\n\n".join(unidades_filtradas))

print(f"Arquivo xerado: {output_file}")
