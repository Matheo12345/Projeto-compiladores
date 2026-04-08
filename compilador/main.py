# =============================================================================
# main.py — Ponto de entrada do compilador
# Compilador — CC6252 | Prof. Charles Ferreira | FEI
#
# Uso:
#   python main.py <arquivo.prog>
#   python main.py teste.prog
# =============================================================================

import sys
import os

# Garante que o terminal exiba acentos corretamente no Windows
sys.stdout.reconfigure(encoding='utf-8')

from lexico import Lexico


def main():
    # --- Verifica argumento de entrada ---
    if len(sys.argv) < 2:
        print('Uso: python main.py <arquivo.prog>')
        print('Exemplo: python main.py teste.prog')
        sys.exit(1)

    caminho = sys.argv[1]

    if not os.path.exists(caminho):
        print(f'Erro: arquivo "{caminho}" não encontrado.')
        sys.exit(1)

    # --- Leitura do arquivo fonte ---
    with open(caminho, 'r', encoding='utf-8') as f:
        codigo = f.read()

    print(f'\nCompilando: {caminho}')
    print(f'Tamanho: {len(codigo)} caracteres\n')

    # --- Fase 1: Análise Léxica ---
    lexico = Lexico(codigo)
    tokens = lexico.tokenizar()
    lexico.imprimir_tokens(tokens)

    # Verifica se houve erros léxicos
    if lexico.erros:
        print(f'\nCompilação interrompida: {len(lexico.erros)} erro(s) léxico(s).')
        sys.exit(1)

    print('\nAnálise léxica concluída com sucesso.')
    print('(Próxima etapa: Análise Sintática)')


if __name__ == '__main__':
    main()
