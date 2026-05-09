# =============================================================================
# lexico.py — Analisador Léxico
# Compilador — CC6252 | Prof. Charles Ferreira | FEI
#
# IMPORTANTE: Este léxico NÃO utiliza nenhuma biblioteca de expressões
# regulares (como 're'). Todo o reconhecimento é feito caractere a caractere.
# =============================================================================

from tokens import (
    Token, PALAVRAS_RESERVADAS,
    ID, NUM_INT, NUM_DEC, TEXTO_LIT,
    MAIS, MENOS, MULT, DIV,
    MENOR, MAIOR, MENOR_IG, MAIOR_IG, IGUAL, DIF,
    ATRIB, ABRE_PAR, FECHA_PAR, ABRE_CHAVE, FECHA_CHAVE,
    PONTO, PONTO_VIRG, EOF
)


class ErroLexico(Exception):
    """Exceção lançada quando o léxico encontra um erro."""
    pass


class Lexico:
    """
    Analisador Léxico — lê o código-fonte caractere por caractere
    e produz uma sequência de tokens.

    Uso:
        lexico = Lexico(codigo_fonte)
        tokens = lexico.tokenizar()
        lexico.imprimir_tokens(tokens)
    """

    def __init__(self, fonte: str):
        self.fonte  = fonte        # código-fonte completo como string
        self.pos    = 0            # posição atual no texto
        self.linha  = 1            # linha atual (começa em 1)
        self.erros  = []           # lista de erros encontrados

    # -----------------------------------------------------------------------
    # Métodos auxiliares de leitura de caracteres
    # -----------------------------------------------------------------------

    def _atual(self) -> str:
        """Retorna o caractere na posição atual sem avançar."""
        if self.pos < len(self.fonte):
            return self.fonte[self.pos]
        return ''  # fim do arquivo

    def _proximo(self) -> str:
        """Retorna o próximo caractere (look-ahead de 1) sem avançar."""
        if self.pos + 1 < len(self.fonte):
            return self.fonte[self.pos + 1]
        return ''

    def _avanca(self) -> str:
        """Lê e retorna o caractere atual, avançando a posição."""
        c = self._atual()
        if c == '\n':
            self.linha += 1
        self.pos += 1
        return c

    def _fim_arquivo(self) -> bool:
        """Retorna True se chegou ao fim do código-fonte."""
        return self.pos >= len(self.fonte)

    # -----------------------------------------------------------------------
    # Pular espaços e comentários
    # -----------------------------------------------------------------------

    def _pula_espacos(self):
        """
        Avança enquanto o caractere atual for espaço, tab ou quebra de linha.
        Também ignora comentários de linha que começam com '//'
        """
        while not self._fim_arquivo():
            c = self._atual()

            # Espaços, tabs, retorno de carro, nova linha
            if c in (' ', '\t', '\r', '\n'):
                self._avanca()

            # Comentário de linha: // até o final da linha
            elif c == '/' and self._proximo() == '/':
                while not self._fim_arquivo() and self._atual() != '\n':
                    self._avanca()

            else:
                break  # encontrou um caractere significativo

    # -----------------------------------------------------------------------
    # Reconhecimento de cada categoria de token
    # -----------------------------------------------------------------------

    def _le_palavra(self) -> Token:
        """
        Lê uma sequência de letras e dígitos.
        Verifica se é palavra reservada; se não, é um ID.
        Regra: começa com letra, seguido de letras, dígitos ou '_'
        """
        inicio = self.linha
        palavra = ''

        while not self._fim_arquivo() and (self._atual().isalpha() or
                                            self._atual().isdigit() or
                                            self._atual() == '_'):
            palavra += self._avanca()

        # Verifica se é palavra reservada (comparação case-insensitive)
        tipo = PALAVRAS_RESERVADAS.get(palavra.lower(), ID)
        return Token(tipo, palavra, inicio)

    def _le_numero(self) -> Token:
        """
        Lê um número inteiro ou decimal.
        Inteiro:  [0-9]+
        Decimal:  [0-9]+ '.' [0-9]+
        """
        inicio = self.linha
        numero = ''

        # Parte inteira
        while not self._fim_arquivo() and self._atual().isdigit():
            numero += self._avanca()

        # Verifica se tem parte decimal (ponto seguido de dígito)
        if self._atual() == '.' and self._proximo().isdigit():
            numero += self._avanca()  # consome o '.'
            while not self._fim_arquivo() and self._atual().isdigit():
                numero += self._avanca()
            return Token(NUM_DEC, numero, inicio)

        return Token(NUM_INT, numero, inicio)

    def _le_string(self) -> Token:
        """
        Lê um literal de texto entre aspas duplas.
        Regra: '"' [qualquer caractere exceto nova linha]* '"'
        """
        inicio = self.linha
        self._avanca()  # consome a aspas de abertura '"'
        conteudo = ''

        while not self._fim_arquivo() and self._atual() != '"':
            if self._atual() == '\n':
                self._registra_erro(f'String não fechada — nova linha inesperada')
                break
            conteudo += self._avanca()

        if self._fim_arquivo():
            self._registra_erro(f'String não fechada — fim do arquivo inesperado')
        else:
            self._avanca()  # consome a aspas de fechamento '"'

        return Token(TEXTO_LIT, conteudo, inicio)

    def _le_operador(self) -> Token:
        """
        Lê operadores de um ou dois caracteres:
          :=  <=  >=  ==  !=  <  >  +  -  *  /  (  )  {  }  .  ;
        """
        inicio = self.linha
        c = self._avanca()  # consome o primeiro caractere

        # Operador de atribuição: :=
        if c == ':':
            if self._atual() == '=':
                self._avanca()
                return Token(ATRIB, ':=', inicio)
            else:
                self._registra_erro(f"Caractere ':' inválido — esperava ':='")
                return self._proximo_token()  # tenta recuperar

        # Operadores relacionais de dois caracteres
        if c == '<':
            if self._atual() == '=':
                self._avanca()
                return Token(MENOR_IG, '<=', inicio)
            return Token(MENOR, '<', inicio)

        if c == '>':
            if self._atual() == '=':
                self._avanca()
                return Token(MAIOR_IG, '>=', inicio)
            return Token(MAIOR, '>', inicio)

        if c == '=':
            if self._atual() == '=':
                self._avanca()
                return Token(IGUAL, '==', inicio)
            else:
                self._registra_erro(f"Caractere '=' inválido — use ':=' para atribuição ou '==' para comparação")
                return self._proximo_token()

        if c == '!':
            if self._atual() == '=':
                self._avanca()
                return Token(DIF, '!=', inicio)
            else:
                self._registra_erro(f"Caractere '!' inválido — esperava '!='")
                return self._proximo_token()

        # Operadores de um caractere
        tabela = {
            '+': MAIS,
            '-': MENOS,
            '*': MULT,
            '/': DIV,
            '(': ABRE_PAR,
            ')': FECHA_PAR,
            '{': ABRE_CHAVE,
            '}': FECHA_CHAVE,
            '.': PONTO,
            ';': PONTO_VIRG,
        }
        if c in tabela:
            return Token(tabela[c], c, inicio)

        # Caractere não reconhecido
        self._registra_erro(f"Caractere '{c}' não reconhecido")
        return self._proximo_token()  # tenta continuar após o erro

    # -----------------------------------------------------------------------
    # Motor principal: lê o próximo token
    # -----------------------------------------------------------------------

    def _proximo_token(self) -> Token:
        """
        Função principal do léxico.
        Pula espaços, identifica o tipo do próximo token e o retorna.
        """
        self._pula_espacos()

        if self._fim_arquivo():
            return Token(EOF, 'EOF', self.linha)

        c = self._atual()

        # Palavra (palavra reservada ou identificador)
        if c.isalpha() or c == '_':
            return self._le_palavra()

        # Número
        if c.isdigit():
            return self._le_numero()

        # Literal de texto
        if c == '"':
            return self._le_string()

        # Operadores e delimitadores
        return self._le_operador()

    # -----------------------------------------------------------------------
    # Tokenização completa e utilitários
    # -----------------------------------------------------------------------

    def tokenizar(self) -> list:
        """
        Percorre todo o código-fonte e retorna a lista completa de tokens.
        O último token da lista é sempre EOF.
        """
        tokens = []
        while True:
            tok = self._proximo_token()
            tokens.append(tok)
            if tok.tipo == EOF:
                break
        return tokens

    def imprimir_tokens(self, tokens: list):
        """
        Imprime a lista de tokens no formato:
            Linha  X | TIPO            | 'valor'
        """
        print('=' * 50)
        print(f'{"LISTA DE TOKENS":^50}')
        print('=' * 50)
        print(f'  {"Linha":<8} {"Tipo":<16} Valor')
        print('-' * 50)
        for tok in tokens:
            print(f'  {str(tok.linha):<8} {tok.tipo:<16} {repr(tok.valor)}')
        print('=' * 50)
        print(f'  Total: {len(tokens)} tokens ({len(tokens)-1} + EOF)')
        if self.erros:
            print(f'\n  ⚠ {len(self.erros)} erro(s) léxico(s) encontrado(s).')
        print('=' * 50)

    def _registra_erro(self, mensagem: str):
        """Registra e imprime um erro léxico."""
        erro = f'ERRO LÉXICO na linha {self.linha}: {mensagem}'
        self.erros.append(erro)
        print(erro)
