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
from lexico import Lexico
from sintatico import Parser
from gerador import Gerador


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

    if lexico.erros:
        print(f'\nCompilação interrompida: {len(lexico.erros)} erro(s) léxico(s).')
        sys.exit(1)

    print('\nAnálise léxica concluída com sucesso.')

    # --- Fase 2: Análise Sintática ---
    print('\n' + '=' * 50)
    print(f'{"ÁRVORE DE DERIVAÇÃO":^50}')
    print('=' * 50)

    parser = Parser(tokens)
    arvore = parser.analisar()

    if parser.erros:
        print(f'\nCompilação interrompida: {len(parser.erros)} erro(s) sintático(s).')
        sys.exit(1)

    arvore.imprimir()
    print('\nAnálise sintática concluída com sucesso.')

    # --- Fase 3: Geração de Código C ---
    caminho_saida = os.path.splitext(caminho)[0] + '.c'
    gerador = Gerador(arvore)
    gerador.gerar()

    if gerador._erros:
        print(f'\nCompilação interrompida: {len(gerador._erros)} erro(s) no gerador.')
        sys.exit(1)

    print('\n' + '=' * 50)
    print(f'{"CÓDIGO C GERADO":^50}')
    print('=' * 50)
    print('\n'.join(gerador._linhas))
    print('=' * 50)

    gerador.escrever_arquivo(caminho_saida)


if __name__ == '__main__':
    main()
