# =============================================================================
# tokens.py — Definição dos tipos de tokens e classe Token
# Compilador — CC6252 | Prof. Diogo F. S. Ramos | FEI
# =============================================================================

# ---------------------------------------------------------------------------
# Tipos de tokens (constantes string para facilitar debug e leitura)
# ---------------------------------------------------------------------------

# --- Palavras reservadas ---
PROGRAMA    = 'PROGRAMA'
FIMPROG     = 'FIMPROG'
INTEIRO     = 'INTEIRO'
DECIMAL     = 'DECIMAL'
TEXTO_TIPO  = 'TEXTO_TIPO'
SE          = 'SE'
SENAO       = 'SENAO'
ENQUANTO    = 'ENQUANTO'
FACA        = 'FACA'
PARA        = 'PARA'
LEIA        = 'LEIA'
ESCREVA     = 'ESCREVA'
VERDADEIRO  = 'VERDADEIRO'
FALSO       = 'FALSO'

# --- Literais ---
NUM_INT     = 'NUM_INT'     # ex: 42
NUM_DEC     = 'NUM_DEC'     # ex: 3.14
TEXTO_LIT   = 'TEXTO_LIT'  # ex: "olá mundo"

# --- Identificador ---
ID          = 'ID'          # ex: contador, x, nome

# --- Operadores matemáticos ---
MAIS        = 'MAIS'        # +
MENOS       = 'MENOS'       # -
MULT        = 'MULT'        # *
DIV         = 'DIV'         # /

# --- Operadores relacionais ---
MENOR       = 'MENOR'       # <
MAIOR       = 'MAIOR'       # >
MENOR_IG    = 'MENOR_IG'    # <=
MAIOR_IG    = 'MAIOR_IG'    # >=
IGUAL       = 'IGUAL'       # ==
DIF         = 'DIF'         # !=

# --- Operador de atribuição ---
ATRIB       = 'ATRIB'       # :=

# --- Delimitadores ---
ABRE_PAR    = 'ABRE_PAR'    # (
FECHA_PAR   = 'FECHA_PAR'   # )
ABRE_CHAVE  = 'ABRE_CHAVE'  # {
FECHA_CHAVE = 'FECHA_CHAVE' # }
PONTO       = 'PONTO'       # .  (fim de declaração/comando)
PONTO_VIRG  = 'PONTO_VIRG'  # ;  (usado no 'para')

# --- Especial ---
EOF         = 'EOF'         # fim do arquivo

# ---------------------------------------------------------------------------
# Mapeamento: texto literal → tipo de token (para palavras reservadas)
# A ORDEM IMPORTA: palavras reservadas devem ser verificadas antes de ID
# ---------------------------------------------------------------------------
PALAVRAS_RESERVADAS = {
    'programa'   : PROGRAMA,
    'fimprog'    : FIMPROG,
    'inteiro'    : INTEIRO,
    'decimal'    : DECIMAL,
    'texto'      : TEXTO_TIPO,
    'se'         : SE,
    'senao'      : SENAO,
    'enquanto'   : ENQUANTO,
    'faca'       : FACA,
    'para'       : PARA,
    'leia'       : LEIA,
    'escreva'    : ESCREVA,
    'verdadeiro' : VERDADEIRO,
    'falso'      : FALSO,
}

# ---------------------------------------------------------------------------
# Classe Token — representa um token reconhecido pelo léxico
# ---------------------------------------------------------------------------
class Token:
    def __init__(self, tipo, valor, linha):
        self.tipo  = tipo    # tipo do token (uma das constantes acima)
        self.valor = valor   # texto original lido do fonte
        self.linha = linha   # número da linha (para mensagens de erro)

    def __repr__(self):
        return f'Token({self.tipo}, {repr(self.valor)}, linha={self.linha})'

    def __str__(self):
        return f'Linha {self.linha:>3} | {self.tipo:<15} | {repr(self.valor)}'
