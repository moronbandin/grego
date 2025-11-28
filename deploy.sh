#!/bin/bash

set -e  # parar se hai erros

# 1. Construír a web
python3 build.py

# 2. Entrar na carpeta build (a que queremos publicar)
cd build

# 3. Inicializar repo temporal
git init
git checkout -b gh-pages

# 4. Engadir todo o HTML/CSS/recursos
git add .

git commit -m "Deploy automatico"

# 5. Publicar na rama gh-pages DO TEU REPO
git push -f https://github.com/moronbandin/grego.git gh-pages

# 6. Volver atrás por seguridade
cd ..
