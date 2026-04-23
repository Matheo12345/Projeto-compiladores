# =============================================================================
# gerar_pdf.py -- Gera o documento PDF da Entrega da Gramatica
# CC6252 | Prof. Diogo F. S. Ramos | FEI
# =============================================================================

import sys
sys.stdout.reconfigure(encoding='utf-8')

from fpdf import FPDF, XPos, YPos

# Caminhos das fontes com suporte a caracteres portugueses (Windows)
FONTE_REGULAR      = r'C:\Windows\Fonts\arial.ttf'
FONTE_BOLD         = r'C:\Windows\Fonts\arialbd.ttf'
FONTE_ITALIC       = r'C:\Windows\Fonts\ariali.ttf'
FONTE_COURIER      = r'C:\Windows\Fonts\cour.ttf'
FONTE_COURIER_BOLD = r'C:\Windows\Fonts\courbd.ttf'

# Cores (RGB)
AZUL_FEI    = (0,   51,  102)
AZUL_CLARO  = (232, 239, 247)
CINZA       = (85,  85,  85)
CINZA_CLARO = (245, 245, 245)
BORDA       = (204, 204, 204)
BRANCO      = (255, 255, 255)
PRETO       = (0,   0,   0)

ALTURA_LINHA_BLOCO = 5.5   # altura de cada linha dentro dos blocos de codigo
MARGEM_V_BLOCO     = 5     # margem vertical interna dos blocos


# =============================================================================
# Classe base do documento
# =============================================================================

class PDF(FPDF):
    def header(self):
        # Sem cabecalho na capa
        if self.page_no() == 1:
            return
        self.set_font('Arial', 'B', 9)
        self.set_text_color(*CINZA)
        self.cell(0, 8, 'CC6252 — Compiladores | Entrega da Gramática | FEI', align='L',
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*PRETO)
        self.set_draw_color(*BORDA)
        self.set_line_width(0.3)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', '', 9)
        self.set_text_color(*CINZA)
        self.cell(0, 10, f'Página {self.page_no()}', align='C')
        self.set_text_color(*PRETO)


def registrar_fontes(pdf: PDF):
    pdf.add_font('Arial',      '',  FONTE_REGULAR)
    pdf.add_font('Arial',      'B', FONTE_BOLD)
    pdf.add_font('Arial',      'I', FONTE_ITALIC)
    pdf.add_font('CourierNew', '',  FONTE_COURIER)
    pdf.add_font('CourierNew', 'B', FONTE_COURIER_BOLD)


# =============================================================================
# Utilitario: garante espaco antes de desenhar um elemento
# =============================================================================

def garantir_espaco(pdf: PDF, altura_necessaria: float):
    """
    Se a altura necessaria nao couber na pagina atual,
    insere uma quebra de pagina antes de continuar.
    Isso evita que retangulos e textos fiquem em paginas diferentes.
    """
    espaco_livre = pdf.h - pdf.b_margin - pdf.get_y()
    if altura_necessaria > espaco_livre:
        pdf.add_page()


# =============================================================================
# Helpers de layout
# =============================================================================

def titulo_secao(pdf: PDF, texto: str):
    """Titulo de secao em azul com linha separadora abaixo."""
    garantir_espaco(pdf, 18)
    pdf.set_font('Arial', 'B', 13)
    pdf.set_text_color(*AZUL_FEI)
    pdf.ln(4)
    pdf.cell(0, 8, texto, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_draw_color(*AZUL_FEI)
    pdf.set_line_width(0.5)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(4)
    pdf.set_text_color(*PRETO)


def titulo_subsecao(pdf: PDF, texto: str):
    """Titulo de subsecao em azul, menor."""
    garantir_espaco(pdf, 14)
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(*AZUL_FEI)
    pdf.ln(3)
    pdf.cell(0, 7, texto, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)
    pdf.set_text_color(*PRETO)


def paragrafo(pdf: PDF, texto: str, tamanho: int = 10):
    """Paragrafo de texto corrido com quebra automatica de linha."""
    garantir_espaco(pdf, 12)
    pdf.set_font('Arial', '', tamanho)
    pdf.set_text_color(*PRETO)
    pdf.multi_cell(0, 6, texto)
    pdf.ln(2)


def nota(pdf: PDF, texto: str):
    """Texto de nota em italico cinza."""
    garantir_espaco(pdf, 10)
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(*CINZA)
    pdf.multi_cell(0, 5, texto)
    pdf.ln(2)
    pdf.set_text_color(*PRETO)


# =============================================================================
# Blocos de conteudo com fundo colorido
#
# ESTRATEGIA: calcular a altura total do bloco ANTES de desenhar qualquer coisa.
# Se nao couber na pagina atual, chamar add_page() primeiro.
# Somente depois disso desenhar o retangulo e escrever o texto —
# garantindo que tudo fique na mesma pagina.
# =============================================================================

def _altura_bloco(linhas: list) -> float:
    """Calcula a altura total de um bloco dada sua lista de linhas."""
    return len(linhas) * ALTURA_LINHA_BLOCO + MARGEM_V_BLOCO * 2


def bloco_gramatica(pdf: PDF, linhas: list):
    """
    Bloco com fundo azul claro para exibir producoes da gramatica.
    Garante que o bloco inteiro fique na mesma pagina.
    """
    altura = _altura_bloco(linhas)
    garantir_espaco(pdf, altura + 4)   # +4 de margem de seguranca

    largura = pdf.w - pdf.l_margin - pdf.r_margin
    x0, y0  = pdf.get_x(), pdf.get_y()

    # Desenha o retangulo de fundo
    pdf.set_fill_color(*AZUL_CLARO)
    pdf.set_draw_color(*AZUL_FEI)
    pdf.set_line_width(0.4)
    pdf.rect(x0, y0, largura, altura, style='FD')

    # Escreve o texto dentro do retangulo
    pdf.set_font('CourierNew', '', 9)
    pdf.set_text_color(*PRETO)
    pdf.set_xy(x0 + 5, y0 + MARGEM_V_BLOCO)

    for linha in linhas:
        pdf.cell(largura - 10, ALTURA_LINHA_BLOCO, linha,
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_x(x0 + 5)

    # Posiciona o cursor abaixo do bloco
    pdf.set_y(y0 + altura + 3)


def bloco_codigo(pdf: PDF, linhas: list):
    """
    Bloco com fundo cinza claro para exibir exemplos de codigo.
    Garante que o bloco inteiro fique na mesma pagina.
    """
    altura = _altura_bloco(linhas)
    garantir_espaco(pdf, altura + 4)

    largura = pdf.w - pdf.l_margin - pdf.r_margin
    x0, y0  = pdf.get_x(), pdf.get_y()

    pdf.set_fill_color(*CINZA_CLARO)
    pdf.set_draw_color(*BORDA)
    pdf.set_line_width(0.4)
    pdf.rect(x0, y0, largura, altura, style='FD')

    pdf.set_font('CourierNew', '', 9)
    pdf.set_text_color(*PRETO)
    pdf.set_xy(x0 + 5, y0 + MARGEM_V_BLOCO)

    for linha in linhas:
        pdf.cell(largura - 10, ALTURA_LINHA_BLOCO, linha,
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_x(x0 + 5)

    pdf.set_y(y0 + altura + 3)


# =============================================================================
# Tabela de tokens
# =============================================================================

def tabela_tokens(pdf: PDF, cabecalho: list, dados: list, larguras: list):
    """
    Tabela com cabecalho azul e linhas alternadas.
    Verifica espaco disponivel antes de comecar a tabela.
    """
    h_cab = 8
    h_lin = 6.5
    altura_estimada = h_cab + len(dados) * h_lin + 4
    garantir_espaco(pdf, altura_estimada)

    x0 = pdf.l_margin

    # --- Cabecalho ---
    pdf.set_fill_color(*AZUL_FEI)
    pdf.set_text_color(*BRANCO)
    pdf.set_font('Arial', 'B', 10)
    pdf.set_draw_color(*BORDA)
    pdf.set_line_width(0.3)
    pdf.set_x(x0)
    for i, col in enumerate(cabecalho):
        pdf.cell(larguras[i], h_cab, col, border=1, fill=True)
    pdf.ln()

    # --- Linhas de dados ---
    pdf.set_text_color(*PRETO)
    pdf.set_font('Arial', '', 9)
    for idx, linha in enumerate(dados):
        # Verifica se esta linha ainda cabe na pagina atual
        garantir_espaco(pdf, h_lin + 2)
        fill = (idx % 2 == 0)
        pdf.set_fill_color(*(CINZA_CLARO if fill else BRANCO))
        pdf.set_x(x0)
        for i, cel in enumerate(linha):
            pdf.cell(larguras[i], h_lin, cel, border=1, fill=True)
        pdf.ln()

    pdf.ln(3)


# =============================================================================
# Construcao do documento
# =============================================================================

def gerar(caminho_saida: str):
    pdf = PDF(orientation='P', unit='mm', format='A4')
    pdf.set_margins(left=20, top=20, right=20)
    pdf.set_auto_page_break(auto=True, margin=20)
    registrar_fontes(pdf)

    # =========================================================================
    # CAPA
    # =========================================================================
    pdf.add_page()

    pdf.ln(18)
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(*CINZA)
    pdf.cell(0, 8, 'Centro Universitário FEI', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 8, 'CC6252 — Compiladores', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(6)

    pdf.set_draw_color(*AZUL_FEI)
    pdf.set_line_width(1.5)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(8)

    pdf.set_font('Arial', 'B', 24)
    pdf.set_text_color(*AZUL_FEI)
    pdf.cell(0, 12, 'Entrega da Gramática', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

    pdf.set_font('Arial', '', 13)
    pdf.set_text_color(*CINZA)
    pdf.cell(0, 8, 'Definição da Linguagem: Gramática GLC e Exemplos',
             align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(6)

    pdf.set_line_width(1.5)
    pdf.set_draw_color(*AZUL_FEI)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(16)

    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(*PRETO)
    pdf.cell(0, 8, 'Aluno: Matheo Campanelli de Aquino Esteves',
             align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 8, 'RA: 22.123.045-1',
             align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)
    pdf.cell(0, 8, 'Professor: Diogo F. S. Ramos',
             align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)
    pdf.cell(0, 8, 'São Bernardo do Campo, 2026',
             align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # =========================================================================
    # SECAO 1 — INTRODUCAO
    # =========================================================================
    pdf.add_page()

    titulo_secao(pdf, '1. Introdução')
    paragrafo(pdf,
        'Este documento apresenta a definição formal da linguagem criada para o projeto '
        'da disciplina CC6252 — Compiladores. A linguagem é imperativa, escrita em português, '
        'e suporta declaração de variáveis, estruturas de controle de fluxo, laços e '
        'operações de entrada e saída. Os programas escritos nessa linguagem utilizam a '
        'extensão .prog.'
    )
    paragrafo(pdf,
        'O compilador traduz programas escritos nessa linguagem para código na linguagem '
        'destino definida pelo professor após a entrega desta gramática.'
    )

    # =========================================================================
    # SECAO 2 — TOKENS
    # =========================================================================
    titulo_secao(pdf, '2. Tokens da Linguagem')
    paragrafo(pdf,
        'A tabela abaixo lista todos os tokens reconhecidos pelo analisador léxico. '
        'O reconhecimento é feito caractere a caractere, sem uso de bibliotecas de '
        'expressões regulares.'
    )

    titulo_subsecao(pdf, '2.1 Palavras Reservadas')
    tabela_tokens(pdf,
        cabecalho=['Token', 'Lexema', 'Descrição'],
        dados=[
            ['PROGRAMA',    'programa',    'Início do programa'],
            ['FIMPROG',     'fimprog',     'Fim do programa'],
            ['INTEIRO',     'inteiro',     'Declaração de variável inteira'],
            ['DECIMAL',     'decimal',     'Declaração de variável decimal (ponto flutuante)'],
            ['TEXTO_TIPO',  'texto',       'Declaração de variável texto (string)'],
            ['SE',          'se',          'Estrutura condicional (if)'],
            ['SENAO',       'senao',       'Alternativa da condicional (else)'],
            ['ENQUANTO',    'enquanto',    'Laço com pré-condição (while)'],
            ['FACA',        'faca',        'Início do laço com pós-condição (do-while)'],
            ['PARA',        'para',        'Laço com contador (for)'],
            ['LEIA',        'leia',        'Comando de entrada de dados'],
            ['ESCREVA',     'escreva',     'Comando de saída de dados'],
            ['VERDADEIRO',  'verdadeiro',  'Literal booleano verdadeiro'],
            ['FALSO',       'falso',       'Literal booleano falso'],
        ],
        larguras=[32, 32, 106]
    )

    titulo_subsecao(pdf, '2.2 Literais e Identificadores')
    tabela_tokens(pdf,
        cabecalho=['Token', 'Expressão Regular', 'Exemplo'],
        dados=[
            ['ID',          '[a-zA-Z_][a-zA-Z0-9_]*',         'contador, x1, nome_var'],
            ['NUM_INT',     '[0-9]+',                           '42, 100, 0'],
            ['NUM_DEC',     '[0-9]+ . [0-9]+',                 '3.14, 0.5, 2.0'],
            ['TEXTO_LIT',   '"" [qualquer char exceto \\n] ""', '"ola mundo", "FEI"'],
        ],
        larguras=[32, 60, 78]
    )

    titulo_subsecao(pdf, '2.3 Operadores e Delimitadores')
    tabela_tokens(pdf,
        cabecalho=['Token', 'Lexema', 'Descrição'],
        dados=[
            ['ATRIB',       ':=',   'Atribuição'],
            ['MAIS',        '+',    'Adição'],
            ['MENOS',       '-',    'Subtração'],
            ['MULT',        '*',    'Multiplicação'],
            ['DIV',         '/',    'Divisão'],
            ['MENOR',       '<',    'Menor que'],
            ['MAIOR',       '>',    'Maior que'],
            ['MENOR_IG',    '<=',   'Menor ou igual a'],
            ['MAIOR_IG',    '>=',   'Maior ou igual a'],
            ['IGUAL',       '==',   'Igual a'],
            ['DIF',         '!=',   'Diferente de'],
            ['ABRE_PAR',    '(',    'Abre parêntese'],
            ['FECHA_PAR',   ')',    'Fecha parêntese'],
            ['ABRE_CHAVE',  '{',    'Abre bloco'],
            ['FECHA_CHAVE', '}',    'Fecha bloco'],
            ['PONTO',       '.',    'Fim de comando ou declaração'],
            ['PONTO_VIRG',  ';',    'Separador interno do comando para'],
        ],
        larguras=[32, 32, 106]
    )
    nota(pdf, 'Observação: comentários de linha iniciam com // e são ignorados pelo léxico.')

    # =========================================================================
    # SECAO 3 — GRAMATICA GLC
    # =========================================================================
    pdf.add_page()

    titulo_secao(pdf, '3. Gramática Livre de Contexto (GLC)')
    paragrafo(pdf,
        'A gramática foi projetada para análise descendente recursiva. '
        'Não possui recursividade à esquerda — a precedência de operadores aritméticos '
        'é garantida pela hierarquia expr -> termo -> fator, resultado da eliminação '
        'de recursividade à esquerda da regra expr -> expr + termo.'
    )

    titulo_subsecao(pdf, '3.1 Regra Inicial e Bloco')
    bloco_gramatica(pdf, [
        'prog        ->  "programa" bloco "fimprog" "."',
        '',
        'bloco       ->  cmd bloco',
        '            |   <vazio>',
    ])

    titulo_subsecao(pdf, '3.2 Comandos')
    bloco_gramatica(pdf, [
        'cmd         ->  declara  |  cmdAtrib  |  cmdSe  |  cmdEnquanto',
        '            |   cmdFaca  |  cmdPara  |  cmdLeia  |  cmdEscreva',
        '',
        'declara     ->  tipo ID "."',
        'tipo        ->  "inteiro"  |  "decimal"  |  "texto"',
        '',
        'cmdAtrib    ->  ID ":=" expr "."',
    ])

    titulo_subsecao(pdf, '3.3 Estruturas de Controle')
    bloco_gramatica(pdf, [
        'cmdSe       ->  "se" "(" exprRel ")" "{" bloco "}" senaoOpt',
        'senaoOpt    ->  "senao" "{" bloco "}"  |  <vazio>',
        '',
        'cmdEnquanto ->  "enquanto" "(" exprRel ")" "{" bloco "}"',
        '',
        'cmdFaca     ->  "faca" "{" bloco "}" "enquanto" "(" exprRel ")" "."',
        '',
        'cmdPara     ->  "para" "(" ID ":=" expr ";" exprRel ";" ID ":=" expr ")" "{" bloco "}"',
    ])

    titulo_subsecao(pdf, '3.4 Entrada e Saída')
    bloco_gramatica(pdf, [
        'cmdLeia     ->  "leia" "(" ID ")" "."',
        '',
        'cmdEscreva  ->  "escreva" "(" conteudo ")" "."',
        'conteudo    ->  TEXTO_LIT  |  expr',
    ])

    titulo_subsecao(pdf, '3.5 Expressões Aritméticas (sem recursividade à esquerda)')
    paragrafo(pdf, 'As regras abaixo garantem que * e / tenham precedência sobre + e -:')
    bloco_gramatica(pdf, [
        'exprRel     ->  expr opRel expr',
        'opRel       ->  "<"  |  ">"  |  "<="  |  ">="  |  "=="  |  "!="',
        '',
        'expr        ->  termo exprLinha',
        'exprLinha   ->  "+" termo exprLinha  |  "-" termo exprLinha  |  <vazio>',
        '',
        'termo       ->  fator termoLinha',
        'termoLinha  ->  "*" fator termoLinha  |  "/" fator termoLinha  |  <vazio>',
        '',
        'fator       ->  NUM_INT  |  NUM_DEC  |  "verdadeiro"  |  "falso"  |  ID  |  "(" expr ")"',
    ])
    nota(pdf,
        'Observação: palavras reservadas são case-insensitive — "PROGRAMA", "Programa" '
        'e "programa" são equivalentes. Isso é uma decisão de design da linguagem.'
    )

    # =========================================================================
    # SECAO 4 — EXEMPLOS
    # =========================================================================
    pdf.add_page()

    titulo_secao(pdf, '4. Exemplos de Código')

    titulo_subsecao(pdf, '4.1 Declaração de variáveis e atribuição')
    bloco_codigo(pdf, [
        'programa',
        '',
        'inteiro a.',
        'inteiro b.',
        'decimal media.',
        '',
        'a := 10.',
        'b := 20.',
        'media := (a + b) / 2.',
        'escreva(media).',
        '',
        'fimprog.',
    ])

    titulo_subsecao(pdf, '4.2 Estrutura condicional (se/senao)')
    bloco_codigo(pdf, [
        'programa',
        '',
        'inteiro x.',
        'inteiro y.',
        '',
        'leia(x).',
        'leia(y).',
        '',
        'se (x > y) {',
        '    escreva("X e maior").',
        '} senao {',
        '    escreva("Y e maior ou igual").',
        '}',
        '',
        'fimprog.',
    ])

    titulo_subsecao(pdf, '4.3 Laço enquanto (while)')
    bloco_codigo(pdf, [
        'programa',
        '',
        'inteiro i.',
        'inteiro soma.',
        '',
        'i    := 1.',
        'soma := 0.',
        '',
        'enquanto (i <= 10) {',
        '    soma := soma + i.',
        '    i    := i + 1.',
        '}',
        '',
        'escreva("Soma de 1 a 10:").',
        'escreva(soma).',
        '',
        'fimprog.',
    ])

    titulo_subsecao(pdf, '4.4 Laço faca/enquanto (do-while)')
    bloco_codigo(pdf, [
        'programa',
        '',
        'inteiro n.',
        '',
        'faca {',
        '    escreva("Digite um numero positivo:").',
        '    leia(n).',
        '} enquanto (n <= 0).',
        '',
        'escreva("Voce digitou:").',
        'escreva(n).',
        '',
        'fimprog.',
    ])

    titulo_subsecao(pdf, '4.5 Laço para (for)')
    bloco_codigo(pdf, [
        'programa',
        '',
        'inteiro i.',
        '',
        'para (i := 1 ; i <= 5 ; i := i + 1) {',
        '    escreva(i).',
        '}',
        '',
        'fimprog.',
    ])

    pdf.add_page()
    titulo_subsecao(pdf, '4.6 Programa completo')
    paragrafo(pdf, 'Exemplo combinando declarações, entrada/saída, condicional e laço:')
    bloco_codigo(pdf, [
        'programa',
        '',
        '// Declaracoes',
        'inteiro a.',
        'inteiro b.',
        'inteiro resultado.',
        'decimal media.',
        '',
        '// Entrada',
        'escreva("Digite o primeiro numero:").',
        'leia(a).',
        'escreva("Digite o segundo numero:").',
        'leia(b).',
        '',
        '// Operacoes',
        'resultado := a + b * 2.',
        'media     := (a + b) / 2.',
        '',
        '// Condicional',
        'se (a > b) {',
        '    escreva("A e maior").',
        '    resultado := a - b.',
        '} senao {',
        '    escreva("B e maior ou igual").',
        '    resultado := b - a.',
        '}',
        '',
        '// Laco',
        'inteiro i.',
        'i := 0.',
        'enquanto (i < resultado) {',
        '    escreva(i).',
        '    i := i + 1.',
        '}',
        '',
        'fimprog.',
    ])

    # =========================================================================
    # SALVA O PDF
    # =========================================================================
    pdf.output(caminho_saida)
    print(f'PDF gerado com sucesso: {caminho_saida}')


if __name__ == '__main__':
    saida = r'C:\Users\Matheo Campanelli\Documents\FEI\Compiladores\Projeto\Projeto-compiladores\entrega_gramatica.pdf'
    gerar(saida)
