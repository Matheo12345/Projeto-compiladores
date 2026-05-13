# =============================================================================
# sintatico.py — Analisador Sintático (Parser Descendente Recursivo)
# Compilador — CC6252 | Prof. Diogo F. S. Ramos | FEI
#
# Abordagem: uma função por regra gramatical.
# A gramática não possui recursividade à esquerda (já eliminada em expr/expr').
# =============================================================================

from tokens import (
    Token,
    PROGRAMA, FIMPROG,
    INTEIRO, DECIMAL, TEXTO_TIPO,
    SE, SENAO, ENQUANTO, FACA, PARA, LEIA, ESCREVA,
    ID, NUM_INT, NUM_DEC, TEXTO_LIT, VERDADEIRO, FALSO,
    MAIS, MENOS, MULT, DIV,
    MENOR, MAIOR, MENOR_IG, MAIOR_IG, IGUAL, DIF,
    ATRIB,
    ABRE_PAR, FECHA_PAR, ABRE_CHAVE, FECHA_CHAVE,
    PONTO, PONTO_VIRG,
    EOF,
)


# =============================================================================
# Nó da Árvore de Derivação
# =============================================================================

class No:
    """
    Nó genérico da árvore de derivação (AST).
      tipo   — nome da regra gramatical ou do token (ex: 'prog', 'cmdSe', 'ID')
      filhos — lista de Nos filhos
      valor  — texto do token (só nas folhas: ID, NUM_INT, NUM_DEC, TEXTO_LIT)
      linha  — linha no fonte (para mensagens de erro do gerador)
    """

    def __init__(self, tipo: str, filhos=None, valor=None, linha=None):
        self.tipo   = tipo
        self.filhos = filhos or []
        self.valor  = valor
        self.linha  = linha

    def imprimir(self, nivel: int = 0):
        """Imprime a árvore com indentação visual."""
        prefixo = '  ' * nivel
        detalhe = f' "{self.valor}"' if self.valor is not None else ''
        print(f'{prefixo}[{self.tipo}]{detalhe}')
        for filho in self.filhos:
            if filho is not None:
                filho.imprimir(nivel + 1)


# =============================================================================
# Exceção de erro sintático
# =============================================================================

class ErroSintatico(Exception):
    pass


# =============================================================================
# Parser
# =============================================================================

class Parser:
    """
    Parser Descendente Recursivo.

    Uso:
        parser = Parser(tokens)
        arvore = parser.analisar()   # retorna No raiz ou None se erro
        arvore.imprimir()
    """

    def __init__(self, tokens: list):
        self.tokens       = tokens
        self.pos          = 0
        self.token_atual  = tokens[0]
        self.erros        = []

    # -----------------------------------------------------------------------
    # Controle de tokens
    # -----------------------------------------------------------------------

    def _consome(self, tipo_esperado: str) -> Token:
        """Verifica o token atual, avança e o retorna. Lança erro se divergir."""
        tok = self.token_atual
        if tok.tipo == tipo_esperado:
            self.pos += 1
            self.token_atual = self.tokens[self.pos] if self.pos < len(self.tokens) else self.tokens[-1]
            return tok
        else:
            self._erro(
                f"Esperado '{tipo_esperado}', "
                f"encontrado '{tok.valor}' ({tok.tipo})"
            )

    def _tipo_atual(self) -> str:
        return self.token_atual.tipo

    def _erro(self, mensagem: str):
        linha = self.token_atual.linha
        msg   = f'ERRO SINTÁTICO na linha {linha}: {mensagem}'
        self.erros.append(msg)
        print(msg)
        raise ErroSintatico(msg)

    # -----------------------------------------------------------------------
    # Ponto de entrada público
    # -----------------------------------------------------------------------

    def analisar(self):
        """Analisa o programa completo. Retorna a árvore ou None se erro."""
        try:
            arvore = self._prog()
            return arvore
        except ErroSintatico:
            return None

    # -----------------------------------------------------------------------
    # Regras gramaticais — uma função por regra
    # -----------------------------------------------------------------------

    # prog → 'programa' bloco 'fimprog' '.'
    def _prog(self) -> No:
        linha = self.token_atual.linha
        self._consome(PROGRAMA)
        bloco = self._bloco()
        self._consome(FIMPROG)
        self._consome(PONTO)
        return No('prog', [bloco], linha=linha)

    # bloco → cmd bloco | ε
    # Para 'fimprog' ou '}' → ε
    def _bloco(self) -> No:
        linha  = self.token_atual.linha
        filhos = []
        _INICIO_CMD = {INTEIRO, DECIMAL, TEXTO_TIPO, ID, SE, ENQUANTO, FACA, PARA, LEIA, ESCREVA}
        while self._tipo_atual() in _INICIO_CMD:
            filhos.append(self._cmd())
        return No('bloco', filhos, linha=linha)

    # cmd → declara | cmdAtrib | cmdSe | cmdEnquanto | cmdFaca | cmdPara | cmdLeia | cmdEscreva
    def _cmd(self) -> No:
        t = self._tipo_atual()
        if t in (INTEIRO, DECIMAL, TEXTO_TIPO):
            return self._declara()
        elif t == ID:
            return self._cmd_atrib()
        elif t == SE:
            return self._cmd_se()
        elif t == ENQUANTO:
            return self._cmd_enquanto()
        elif t == FACA:
            return self._cmd_faca()
        elif t == PARA:
            return self._cmd_para()
        elif t == LEIA:
            return self._cmd_leia()
        elif t == ESCREVA:
            return self._cmd_escreva()
        else:
            self._erro(f"Comando inválido: '{self.token_atual.valor}'")

    # declara → tipo ID '.'
    def _declara(self) -> No:
        linha = self.token_atual.linha
        no_tipo = self._tipo()
        tok_id  = self._consome(ID)
        self._consome(PONTO)
        no_id = No('ID', valor=tok_id.valor, linha=tok_id.linha)
        return No('declara', [no_tipo, no_id], linha=linha)

    # tipo → 'inteiro' | 'decimal' | 'texto'
    def _tipo(self) -> No:
        t   = self._tipo_atual()
        tok = self.token_atual
        if t == INTEIRO:
            self._consome(INTEIRO)
            return No('tipo', valor='inteiro', linha=tok.linha)
        elif t == DECIMAL:
            self._consome(DECIMAL)
            return No('tipo', valor='decimal', linha=tok.linha)
        elif t == TEXTO_TIPO:
            self._consome(TEXTO_TIPO)
            return No('tipo', valor='texto', linha=tok.linha)
        else:
            self._erro(f"Tipo inválido: '{tok.valor}'")

    # cmdAtrib → ID ':=' expr '.'
    def _cmd_atrib(self) -> No:
        tok_id = self._consome(ID)
        self._consome(ATRIB)
        no_expr = self._expr()
        self._consome(PONTO)
        no_id = No('ID', valor=tok_id.valor, linha=tok_id.linha)
        return No('cmdAtrib', [no_id, no_expr], linha=tok_id.linha)

    # Versão sem ponto final — usada internamente no 'para'
    def _cmd_atrib_sem_ponto(self) -> No:
        tok_id = self._consome(ID)
        self._consome(ATRIB)
        no_expr = self._expr()
        no_id = No('ID', valor=tok_id.valor, linha=tok_id.linha)
        return No('cmdAtrib', [no_id, no_expr], linha=tok_id.linha)

    # cmdSe → 'se' '(' exprRel ')' '{' bloco '}' senao_opt
    def _cmd_se(self) -> No:
        linha = self.token_atual.linha
        self._consome(SE)
        self._consome(ABRE_PAR)
        cond = self._expr_rel()
        self._consome(FECHA_PAR)
        self._consome(ABRE_CHAVE)
        bloco_se = self._bloco()
        self._consome(FECHA_CHAVE)
        bloco_senao = self._senao_opt()
        return No('cmdSe', [cond, bloco_se, bloco_senao], linha=linha)

    # senao_opt → 'senao' '{' bloco '}' | ε
    def _senao_opt(self):
        if self._tipo_atual() == SENAO:
            self._consome(SENAO)
            self._consome(ABRE_CHAVE)
            bloco = self._bloco()
            self._consome(FECHA_CHAVE)
            return bloco
        return None  # ε

    # cmdEnquanto → 'enquanto' '(' exprRel ')' '{' bloco '}'
    def _cmd_enquanto(self) -> No:
        linha = self.token_atual.linha
        self._consome(ENQUANTO)
        self._consome(ABRE_PAR)
        cond = self._expr_rel()
        self._consome(FECHA_PAR)
        self._consome(ABRE_CHAVE)
        bloco = self._bloco()
        self._consome(FECHA_CHAVE)
        return No('cmdEnquanto', [cond, bloco], linha=linha)

    # cmdFaca → 'faca' '{' bloco '}' 'enquanto' '(' exprRel ')' '.'
    def _cmd_faca(self) -> No:
        linha = self.token_atual.linha
        self._consome(FACA)
        self._consome(ABRE_CHAVE)
        bloco = self._bloco()
        self._consome(FECHA_CHAVE)
        self._consome(ENQUANTO)
        self._consome(ABRE_PAR)
        cond = self._expr_rel()
        self._consome(FECHA_PAR)
        self._consome(PONTO)
        return No('cmdFaca', [bloco, cond], linha=linha)

    # cmdPara → 'para' '(' cmdAtrib_sem_ponto ';' exprRel ';' cmdAtrib_sem_ponto ')' '{' bloco '}'
    def _cmd_para(self) -> No:
        linha = self.token_atual.linha
        self._consome(PARA)
        self._consome(ABRE_PAR)
        init = self._cmd_atrib_sem_ponto()
        self._consome(PONTO_VIRG)
        cond = self._expr_rel()
        self._consome(PONTO_VIRG)
        passo = self._cmd_atrib_sem_ponto()
        self._consome(FECHA_PAR)
        self._consome(ABRE_CHAVE)
        bloco = self._bloco()
        self._consome(FECHA_CHAVE)
        return No('cmdPara', [init, cond, passo, bloco], linha=linha)

    # cmdLeia → 'leia' '(' ID ')' '.'
    def _cmd_leia(self) -> No:
        linha = self.token_atual.linha
        self._consome(LEIA)
        self._consome(ABRE_PAR)
        tok_id = self._consome(ID)
        self._consome(FECHA_PAR)
        self._consome(PONTO)
        no_id = No('ID', valor=tok_id.valor, linha=tok_id.linha)
        return No('cmdLeia', [no_id], linha=linha)

    # cmdEscreva → 'escreva' '(' conteudo ')' '.'
    # conteudo → TEXTO_LIT | expr
    def _cmd_escreva(self) -> No:
        linha = self.token_atual.linha
        self._consome(ESCREVA)
        self._consome(ABRE_PAR)
        if self._tipo_atual() == TEXTO_LIT:
            tok = self._consome(TEXTO_LIT)
            conteudo = No('TEXTO_LIT', valor=tok.valor, linha=tok.linha)
        else:
            conteudo = self._expr()
        self._consome(FECHA_PAR)
        self._consome(PONTO)
        return No('cmdEscreva', [conteudo], linha=linha)

    # -----------------------------------------------------------------------
    # Expressões relacionais
    # exprRel → expr op_rel expr
    # -----------------------------------------------------------------------

    _OP_REL = {MENOR, MAIOR, MENOR_IG, MAIOR_IG, IGUAL, DIF}

    def _expr_rel(self) -> No:
        linha   = self.token_atual.linha
        esq     = self._expr()
        tok_op  = self.token_atual
        if tok_op.tipo not in self._OP_REL:
            self._erro(
                f"Operador relacional esperado, encontrado '{tok_op.valor}'"
            )
        self._consome(tok_op.tipo)
        dir_ = self._expr()
        no_op = No('OP_REL', valor=tok_op.valor, linha=tok_op.linha)
        return No('exprRel', [esq, no_op, dir_], linha=linha)

    # -----------------------------------------------------------------------
    # Expressões aritméticas (sem recursividade à esquerda)
    #
    # expr  → termo expr'
    # expr' → '+' termo expr' | '-' termo expr' | ε
    # -----------------------------------------------------------------------

    def _expr(self) -> No:
        linha = self.token_atual.linha
        no    = self._termo()
        return self._expr_linha(no, linha)

    def _expr_linha(self, esq: No, linha: int) -> No:
        t = self._tipo_atual()
        if t == MAIS:
            tok = self._consome(MAIS)
            dir_ = self._termo()
            no   = No('expr', [esq, No('OP', valor='+', linha=tok.linha), dir_], linha=linha)
            return self._expr_linha(no, linha)
        elif t == MENOS:
            tok = self._consome(MENOS)
            dir_ = self._termo()
            no   = No('expr', [esq, No('OP', valor='-', linha=tok.linha), dir_], linha=linha)
            return self._expr_linha(no, linha)
        return esq  # ε

    # termo  → fator termo'
    # termo' → '*' fator termo' | '/' fator termo' | ε
    def _termo(self) -> No:
        linha = self.token_atual.linha
        no    = self._fator()
        return self._termo_linha(no, linha)

    def _termo_linha(self, esq: No, linha: int) -> No:
        t = self._tipo_atual()
        if t == MULT:
            tok  = self._consome(MULT)
            dir_ = self._fator()
            no   = No('termo', [esq, No('OP', valor='*', linha=tok.linha), dir_], linha=linha)
            return self._termo_linha(no, linha)
        elif t == DIV:
            tok  = self._consome(DIV)
            dir_ = self._fator()
            no   = No('termo', [esq, No('OP', valor='/', linha=tok.linha), dir_], linha=linha)
            return self._termo_linha(no, linha)
        return esq  # ε

    # fator → NUM_INT | NUM_DEC | VERDADEIRO | FALSO | ID | '(' expr ')'
    def _fator(self) -> No:
        tok = self.token_atual
        t   = tok.tipo

        if t == NUM_INT:
            self._consome(NUM_INT)
            return No('NUM_INT', valor=tok.valor, linha=tok.linha)

        elif t == NUM_DEC:
            self._consome(NUM_DEC)
            return No('NUM_DEC', valor=tok.valor, linha=tok.linha)

        elif t == VERDADEIRO:
            self._consome(VERDADEIRO)
            return No('VERDADEIRO', valor='verdadeiro', linha=tok.linha)

        elif t == FALSO:
            self._consome(FALSO)
            return No('FALSO', valor='falso', linha=tok.linha)

        elif t == ID:
            self._consome(ID)
            return No('ID', valor=tok.valor, linha=tok.linha)

        elif t == ABRE_PAR:
            self._consome(ABRE_PAR)
            no = self._expr()
            self._consome(FECHA_PAR)
            return no

        else:
            self._erro(
                f"Fator inválido: '{tok.valor}' — esperado número, identificador ou '('"
            )
