# -*- coding: utf-8 -*-

import subprocess
import sys

def executar_comando_git(comando, diretorio):
    """
    Executa um comando Git no diretório especificado.
    """
    try:
        resultado = subprocess.run(
            comando, cwd=diretorio, text=True, capture_output=True
        )
        if resultado.returncode == 0:
            print(f"Comando executado com sucesso: {' '.join(comando)}")
            print(resultado.stdout)
        else:
            print(f"Erro ao executar o comando: {' '.join(comando)}")
            print(resultado.stderr)
            sys.exit(1)  # Encerra o script em caso de erro
    except Exception as e:
        print(f"Erro inesperado: {e}")
        sys.exit(1)

def verificar_alteracoes(diretorio):
    """
    Verifica se há alterações no repositório.
    Retorna True se houver alterações, False caso contrário.
    """
    resultado = subprocess.run(
        ["git", "status", "--porcelain"], cwd=diretorio, text=True, capture_output=True
    )
    return bool(resultado.stdout.strip())

# Caminho do repositório local
repositorio_local = "D:/GitHub/ipyow"

# 1. Atualizar o repositório
print("Atualizando o repositório...")
executar_comando_git(["git", "pull"], repositorio_local)

# 2. Verificar se há alterações
if verificar_alteracoes(repositorio_local):
    print("Alterações detectadas. Preparando para commit...")

    # 3. Adicionar mudanças
    print("Adicionando mudanças...")
    executar_comando_git(["git", "add", "."], repositorio_local)

    # 4. Fazer commit com uma mensagem padrão
    print("Fazendo commit...")
    executar_comando_git(["git", "commit", "-m", "Atualização automática"], repositorio_local)

    # 5. Enviar mudanças para o repositório remoto
    print("Enviando mudanças para o repositório remoto...")
    executar_comando_git(["git", "push"], repositorio_local)
else:
    print("Nenhuma alteração detectada. Nada para commit.")

print("Processo concluído com sucesso!")