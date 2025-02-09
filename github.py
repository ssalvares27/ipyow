# -*- coding: utf-8 -*-

import subprocess

def executar_comando_git(comando, diretorio):
    """
    Executa um comando Git no diretório especificado.
    """
    try:
        resultado = subprocess.run(
            comando, cwd=diretorio, text=True, capture_output=True, shell=True
        )
        if resultado.returncode == 0:
            print(f"Comando executado com sucesso: {' '.join(comando)}")
            print(resultado.stdout)
        else:
            print(f"Erro ao executar o comando: {' '.join(comando)}")
            print(resultado.stderr)
    except Exception as e:
        print(f"Erro inesperado: {e}")

# Caminho do repositório local
repositorio_local = "D:/GitHub"

# Atualizar o repositório
executar_comando_git(["git", "pull"], repositorio_local)

# Adicionar mudanças
executar_comando_git(["git", "add", "."], repositorio_local)

# Fazer commit com uma mensagem padrão
executar_comando_git(["git", "commit", "-m", "Atualização automática"], repositorio_local)

# Enviar mudanças para o repositório remoto
executar_comando_git(["git", "push"], repositorio_local)


