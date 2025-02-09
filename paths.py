# -*- coding: utf-8 -*-

""" paths.py"""

import os

# Caminho raiz do projeto
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Caminho da pasta `static`
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Caminho para a pasta de códigos de barras
BARCODES_DIR = os.path.join(STATIC_DIR, "img", "barcodes")
PRODUTOS_DIR = os.path.join(STATIC_DIR, "img", "produtos")

# Outros caminhos relevantes
IMAGES_DIR = os.path.join(STATIC_DIR, "img")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Função para garantir que as pastas existam


def ensure_directories():
    for directory in [BARCODES_DIR, IMAGES_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)


# Certifique-se de que as pastas estão criadas ao importar este arquivo
ensure_directories()
