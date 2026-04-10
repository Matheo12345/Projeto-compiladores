# =============================================================================
# main.py -- Ponto de entrada do compilador
# Compilador -- CC6252 | Prof. Charles Ferreira | FEI
#
# Uso:
#   python main.py <arquivo.prog>
#   python main.py teste.prog
# =============================================================================

import sys
import os

# Garante que o terminal exiba acentos corretamente no Windows
sys.stdout.reconfigure(encoding='utf-8')

from lexico    import Lexico
from sintatico import Parser, ErroSintatico


def main():
    # --- Verifica argumento de entrada ---
    if len(sys.argv) < 2:
        print('Uso: python main.py <arquivo.prog>')
        print('Exemplo: python main.py teste.prog')
        sys.exit(1)

    caminho = sys.argv[1]

    if not os.path.exists(caminho):
        print(f'Erro: arquivo "{caminho}" nao encontrado.')
        sys.exit(1)

    # --- Leitura do arquivo fonte ---
    with open(caminho, 'r', encoding='utf-8') as f:
        codigo = f.read()

    print(f'\nCompilando: {caminho}')
    print(f'Tamanho: {len(codigo)} caracteres\n')

    # -------------------------------------------------------------------------
    # Fase 1: Analise Lexica
    # Transforma o codigo-fonte em uma lista de tokens.
    # -------------------------------------------------------------------------
    lexico = Lexico(codigo)
    tokens = lexico.tokenizar()
    lexico.imprimir_tokens(tokens)

    # Se houve erros lexicos, nao faz sentido continuar para o parser
    if lexico.erros:
        print(f'\nCompilacao interrompida: {len(lexico.erros)} erro(s) lexico(s).')
        sys.exit(1)

    print('\nAnalise lexica concluida com sucesso.')

    # -------------------------------------------------------------------------
    # Fase 2: Analise Sintatica
    # Consome a lista de tokens e constroi a arvore de derivacao.
    # -------------------------------------------------------------------------
    print('\n' + '=' * 50)
    print(f'{"ARVORE DE DERIVACAO":^50}')
    print('=' * 50)

    try:
        parser = Parser(tokens)
        arvore = parser.analisar()
        arvore.imprimir()               # imprime a arvore identada
        print('=' * 50)
        print('\nAnalise sintatica concluida com sucesso.')
        print('(Proxima etapa: Geracao de Codigo)')
    except ErroSintatico:
        print('\nCompilacao interrompida por erro sintatico.')
        sys.exit(1)


if __name__ == '__main__':
    main()
