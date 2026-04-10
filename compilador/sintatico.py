# =============================================================================
# sintatico.py -- Analisador Sintatico (Parser)
# Compilador -- CC6252 | Prof. Charles Ferreira | FEI
#
# Abordagem: Descendente Recursivo -- uma funcao por regra da gramatica.
# Recebe a lista de tokens gerada pelo lexico e constroi a arvore de derivacao.
# =============================================================================

import sys
sys.stdout.reconfigure(encoding='utf-8')

from tokens import (
    PROGRAMA, FIMPROG,
    INTEIRO, DECIMAL, TEXTO_TIPO,
    SE, SENAO, ENQUANTO, FACA, PARA, LEIA, ESCREVA,
    ID, NUM_INT, NUM_DEC, TEXTO_LIT,
    ATRIB,
    MAIS, MENOS, MULT, DIV,
    MENOR, MAIOR, MENOR_IG, MAIOR_IG, IGUAL, DIF,
    ABRE_PAR, FECHA_PAR, ABRE_CHAVE, FECHA_CHAVE,
    PONTO, PONTO_VIRG,
    EOF
)


# =============================================================================
# Classe No -- representa um no da arvore de derivacao
# =============================================================================

class No:
    """
    Cada no da arvore guarda:
      - tipo  : nome da regra gramatical (ex: 'prog', 'cmdSe', 'expr')
      - filhos: lista de nos filhos (sub-arvores)
      - valor : valor literal do token, usado apenas nas folhas
                (ex: o nome de um ID, o valor de um NUM_INT)
    """

    def __init__(self, tipo, filhos=None, valor=None):
        self.tipo   = tipo
        self.filhos = filhos or []  # nos filhos (lista de No)
        self.valor  = valor         # valor textual (so para folhas)

    def imprimir(self, nivel=0):
        """
        Imprime a arvore de forma identada para facilitar a visualizacao.
        Cada nivel de profundidade recebe 2 espacos extras.

        Exemplo de saida:
          [prog]
            [bloco]
              [declara]
                [tipo] 'inteiro'
                [id] 'a'
        """
        prefixo = '  ' * nivel
        # Se o no e uma folha (tem valor), exibe o valor ao lado do tipo
        info_valor = f" '{self.valor}'" if self.valor is not None else ''
        print(f'{prefixo}[{self.tipo}]{info_valor}')
        # Imprime recursivamente cada filho
        for filho in self.filhos:
            if filho is not None:
                filho.imprimir(nivel + 1)


# =============================================================================
# Classe ErroSintatico -- excecao lancada pelo parser
# =============================================================================

class ErroSintatico(Exception):
    """Excecao lancada quando o parser encontra um erro na estrutura do programa."""
    pass


# =============================================================================
# Classe Parser -- analisador sintatico descendente recursivo
# =============================================================================

class Parser:
    """
    Recebe a lista de tokens do lexico e verifica se o programa
    esta sintaticamente correto, construindo a arvore de derivacao.

    Uso:
        parser = Parser(tokens)
        arvore = parser.analisar()
        arvore.imprimir()
    """

    def __init__(self, tokens: list):
        self.tokens = tokens    # lista completa de tokens
        self.pos    = 0         # indice do token atual
        self.atual  = tokens[0] # token que esta sendo analisado agora

    # -----------------------------------------------------------------------
    # Metodos auxiliares de consumo de tokens
    # -----------------------------------------------------------------------

    def _consome(self, tipo_esperado: str):
        """
        Verifica se o token atual e do tipo esperado.
        Se sim, avanca para o proximo token e retorna o token consumido.
        Se nao, lanca um erro sintatico com a linha e o que era esperado.
        """
        if self.atual.tipo == tipo_esperado:
            token = self.atual
            self.pos += 1
            # Garante que nunca ultrapassamos o fim da lista
            if self.pos < len(self.tokens):
                self.atual = self.tokens[self.pos]
            return token
        else:
            self._erro(f"esperado '{tipo_esperado}', encontrado '{self.atual.valor}'")

    def _erro(self, mensagem: str):
        """Imprime a mensagem de erro sintatico e encerra o programa."""
        linha = self.atual.linha
        print(f'ERRO SINTATICO na linha {linha}: {mensagem}')
        raise ErroSintatico(mensagem)

    def _tipo_atual(self) -> str:
        """Retorna o tipo do token atual (atalho para legibilidade)."""
        return self.atual.tipo

    # -----------------------------------------------------------------------
    # Ponto de entrada publico
    # -----------------------------------------------------------------------

    def analisar(self) -> No:
        """
        Inicia a analise sintatica a partir da regra inicial 'prog'.
        Retorna o no raiz da arvore de derivacao.
        """
        arvore = self._prog()
        return arvore

    # -----------------------------------------------------------------------
    # Regras da gramatica -- uma funcao por regra
    # -----------------------------------------------------------------------

    # --- prog -> 'programa' bloco 'fimprog' '.' ---
    def _prog(self) -> No:
        """
        Regra raiz do programa.
        Todo programa comeca com 'programa' e termina com 'fimprog' '.'
        """
        self._consome(PROGRAMA)
        no_bloco = self._bloco()        # corpo do programa
        self._consome(FIMPROG)
        self._consome(PONTO)
        return No('prog', [no_bloco])

    # --- bloco -> cmd bloco | <vazio> ---
    def _bloco(self) -> No:
        """
        Um bloco e uma sequencia de zero ou mais comandos.
        Termina quando encontra 'fimprog' ou '}' (fim de bloco aninhado).
        """
        filhos = []
        # Continua lendo comandos enquanto nao chegar ao fim do bloco
        while self._tipo_atual() not in (FIMPROG, FECHA_CHAVE, EOF):
            filhos.append(self._cmd())
        return No('bloco', filhos)

    # --- cmd -> declara | cmdAtrib | cmdSe | cmdEnquanto | cmdFaca |
    #            cmdPara | cmdLeia | cmdEscreva ---
    def _cmd(self) -> No:
        """
        Decide qual tipo de comando esta sendo lido com base no token atual
        e chama a funcao correspondente.
        """
        tipo = self._tipo_atual()

        if tipo in (INTEIRO, DECIMAL, TEXTO_TIPO):
            return self._declara()

        elif tipo == ID:
            return self._cmd_atrib()

        elif tipo == SE:
            return self._cmd_se()

        elif tipo == ENQUANTO:
            return self._cmd_enquanto()

        elif tipo == FACA:
            return self._cmd_faca()

        elif tipo == PARA:
            return self._cmd_para()

        elif tipo == LEIA:
            return self._cmd_leia()

        elif tipo == ESCREVA:
            return self._cmd_escreva()

        else:
            self._erro(f"comando invalido: '{self.atual.valor}'")

    # -----------------------------------------------------------------------
    # Declaracao de variavel
    # -----------------------------------------------------------------------

    # --- declara -> tipo ID '.' ---
    def _declara(self) -> No:
        """
        Declaracao de variavel: inteiro x.
        Retorna um no com o tipo e o identificador como filhos.
        """
        no_tipo = self._tipo()                          # 'inteiro', 'decimal' ou 'texto'
        tok_id  = self._consome(ID)                     # nome da variavel
        self._consome(PONTO)                            # '.' obrigatorio no fim
        return No('declara', [no_tipo, No('id', valor=tok_id.valor)])

    # --- tipo -> 'inteiro' | 'decimal' | 'texto' ---
    def _tipo(self) -> No:
        """Le o tipo da variavel e retorna um no folha com o lexema."""
        tipo = self._tipo_atual()
        if tipo == INTEIRO:
            tok = self._consome(INTEIRO)
        elif tipo == DECIMAL:
            tok = self._consome(DECIMAL)
        elif tipo == TEXTO_TIPO:
            tok = self._consome(TEXTO_TIPO)
        else:
            self._erro(f"tipo invalido: '{self.atual.valor}'")
        return No('tipo', valor=tok.valor)

    # -----------------------------------------------------------------------
    # Atribuicao
    # -----------------------------------------------------------------------

    # --- cmdAtrib -> ID ':=' expr '.' ---
    def _cmd_atrib(self) -> No:
        """
        Comando de atribuicao: x := expr.
        O lado esquerdo e sempre um ID, o lado direito e uma expressao.
        """
        tok_id = self._consome(ID)
        self._consome(ATRIB)            # ':='
        no_expr = self._expr()          # lado direito da atribuicao
        self._consome(PONTO)
        return No('cmdAtrib', [No('id', valor=tok_id.valor), no_expr])

    # -----------------------------------------------------------------------
    # Estruturas de controle
    # -----------------------------------------------------------------------

    # --- cmdSe -> 'se' '(' exprRel ')' '{' bloco '}' senaoOpt ---
    def _cmd_se(self) -> No:
        """
        Estrutura condicional: se (cond) { bloco } senao { bloco }
        O bloco senao e opcional.
        """
        self._consome(SE)
        self._consome(ABRE_PAR)
        no_cond = self._expr_rel()      # condicao entre parenteses
        self._consome(FECHA_PAR)
        self._consome(ABRE_CHAVE)
        no_bloco_se = self._bloco()     # bloco executado se verdadeiro
        self._consome(FECHA_CHAVE)
        no_bloco_senao = self._senao_opt()  # bloco senao (pode ser None)
        return No('cmdSe', [no_cond, no_bloco_se, no_bloco_senao])

    # --- senaoOpt -> 'senao' '{' bloco '}' | <vazio> ---
    def _senao_opt(self):
        """
        Parte opcional do 'se'. Retorna o no do bloco senao,
        ou None se nao houver 'senao'.
        """
        if self._tipo_atual() == SENAO:
            self._consome(SENAO)
            self._consome(ABRE_CHAVE)
            no_bloco = self._bloco()
            self._consome(FECHA_CHAVE)
            return no_bloco
        return None     # producao vazia: senaoOpt -> <vazio>

    # --- cmdEnquanto -> 'enquanto' '(' exprRel ')' '{' bloco '}' ---
    def _cmd_enquanto(self) -> No:
        """
        Laco while: enquanto (cond) { bloco }
        Executa o bloco enquanto a condicao for verdadeira.
        """
        self._consome(ENQUANTO)
        self._consome(ABRE_PAR)
        no_cond = self._expr_rel()
        self._consome(FECHA_PAR)
        self._consome(ABRE_CHAVE)
        no_bloco = self._bloco()
        self._consome(FECHA_CHAVE)
        return No('cmdEnquanto', [no_cond, no_bloco])

    # --- cmdFaca -> 'faca' '{' bloco '}' 'enquanto' '(' exprRel ')' '.' ---
    def _cmd_faca(self) -> No:
        """
        Laco do-while: faca { bloco } enquanto (cond).
        Executa o bloco pelo menos uma vez antes de checar a condicao.
        """
        self._consome(FACA)
        self._consome(ABRE_CHAVE)
        no_bloco = self._bloco()
        self._consome(FECHA_CHAVE)
        self._consome(ENQUANTO)
        self._consome(ABRE_PAR)
        no_cond = self._expr_rel()
        self._consome(FECHA_PAR)
        self._consome(PONTO)
        return No('cmdFaca', [no_bloco, no_cond])

    # --- cmdPara -> 'para' '(' ID ':=' expr ';' exprRel ';' ID ':=' expr ')' '{' bloco '}' ---
    def _cmd_para(self) -> No:
        """
        Laco for: para (i := 0 ; i < 10 ; i := i + 1) { bloco }
        Composto por: inicializacao ; condicao ; incremento
        """
        self._consome(PARA)
        self._consome(ABRE_PAR)

        # Inicializacao: ID ':=' expr
        tok_id_ini = self._consome(ID)
        self._consome(ATRIB)
        no_ini = self._expr()
        no_atrib_ini = No('cmdAtrib', [No('id', valor=tok_id_ini.valor), no_ini])

        self._consome(PONTO_VIRG)       # ';' separador

        # Condicao: exprRel
        no_cond = self._expr_rel()

        self._consome(PONTO_VIRG)       # ';' separador

        # Incremento: ID ':=' expr
        tok_id_inc = self._consome(ID)
        self._consome(ATRIB)
        no_inc = self._expr()
        no_atrib_inc = No('cmdAtrib', [No('id', valor=tok_id_inc.valor), no_inc])

        self._consome(FECHA_PAR)
        self._consome(ABRE_CHAVE)
        no_bloco = self._bloco()
        self._consome(FECHA_CHAVE)

        return No('cmdPara', [no_atrib_ini, no_cond, no_atrib_inc, no_bloco])

    # -----------------------------------------------------------------------
    # Entrada e saida
    # -----------------------------------------------------------------------

    # --- cmdLeia -> 'leia' '(' ID ')' '.' ---
    def _cmd_leia(self) -> No:
        """
        Comando de entrada: leia(x).
        Le um valor do teclado e armazena na variavel ID.
        """
        self._consome(LEIA)
        self._consome(ABRE_PAR)
        tok_id = self._consome(ID)
        self._consome(FECHA_PAR)
        self._consome(PONTO)
        return No('cmdLeia', [No('id', valor=tok_id.valor)])

    # --- cmdEscreva -> 'escreva' '(' conteudo ')' '.' ---
    def _cmd_escreva(self) -> No:
        """
        Comando de saida: escreva("msg") ou escreva(x) ou escreva(expr).
        Imprime um texto literal, uma variavel ou o resultado de uma expressao.
        """
        self._consome(ESCREVA)
        self._consome(ABRE_PAR)
        no_conteudo = self._conteudo()
        self._consome(FECHA_PAR)
        self._consome(PONTO)
        return No('cmdEscreva', [no_conteudo])

    # --- conteudo -> TEXTO_LIT | ID | expr ---
    def _conteudo(self) -> No:
        """
        O que pode ser passado para escreva():
          - Um literal de texto: "mensagem"
          - Um identificador: x
          - Uma expressao: a + b
        Para diferenciar ID de expr, usamos o lookahead (token seguinte).
        Se apos o ID vier ')' e fim de conteudo, e so um ID. Caso contrario, e expr.
        """
        if self._tipo_atual() == TEXTO_LIT:
            tok = self._consome(TEXTO_LIT)
            return No('textoLit', valor=tok.valor)
        else:
            # Tanto ID isolado quanto expressoes passam por _expr()
            # O parser de expr trata os dois casos corretamente
            return self._expr()

    # -----------------------------------------------------------------------
    # Expressao relacional
    # -----------------------------------------------------------------------

    # --- exprRel -> expr opRel expr ---
    def _expr_rel(self) -> No:
        """
        Expressao relacional usada nas condicoes de if, while e for.
        Formato: expr opRel expr  (ex: a > b, i < 10, x == y)
        """
        no_esq = self._expr()           # lado esquerdo
        no_op  = self._op_rel()         # operador relacional
        no_dir = self._expr()           # lado direito
        return No('exprRel', [no_esq, no_op, no_dir])

    # --- opRel -> '<' | '>' | '<=' | '>=' | '==' | '!=' ---
    def _op_rel(self) -> No:
        """Le o operador relacional e retorna um no folha com o simbolo."""
        tipo = self._tipo_atual()
        operadores = (MENOR, MAIOR, MENOR_IG, MAIOR_IG, IGUAL, DIF)
        if tipo in operadores:
            tok = self._consome(tipo)
            return No('opRel', valor=tok.valor)
        else:
            self._erro(f"operador relacional esperado, encontrado '{self.atual.valor}'")

    # -----------------------------------------------------------------------
    # Expressoes aritmeticas (com precedencia correta, sem recursividade a esquerda)
    # -----------------------------------------------------------------------

    # --- expr -> termo exprLinha ---
    def _expr(self) -> No:
        """
        Ponto de entrada para expressoes aritmeticas.
        Delega para termo() e depois verifica se ha '+' ou '-'.
        """
        no_esq = self._termo()
        return self._expr_linha(no_esq)

    # --- exprLinha -> '+' termo exprLinha | '-' termo exprLinha | <vazio> ---
    def _expr_linha(self, no_esq: No) -> No:
        """
        Continuacao de uma expressao: trata '+' e '-'.
        A recursao a direita garante associatividade a esquerda
        e elimina a recursividade a esquerda da gramatica original.

        Exemplo: a + b - c
          _expr_linha(a) le '+', chama _termo() -> b
          _expr_linha(a+b) le '-', chama _termo() -> c
          _expr_linha((a+b)-c) nao ha mais op -> retorna
        """
        tipo = self._tipo_atual()
        if tipo == MAIS:
            tok = self._consome(MAIS)
            no_dir = self._termo()
            no_op  = No('op', valor=tok.valor)
            no_atual = No('expr', [no_esq, no_op, no_dir])
            return self._expr_linha(no_atual)   # continua verificando
        elif tipo == MENOS:
            tok = self._consome(MENOS)
            no_dir = self._termo()
            no_op  = No('op', valor=tok.valor)
            no_atual = No('expr', [no_esq, no_op, no_dir])
            return self._expr_linha(no_atual)
        else:
            return no_esq   # producao vazia: nao ha mais operadores

    # --- termo -> fator termoLinha ---
    def _termo(self) -> No:
        """
        Trata multiplicacao e divisao (maior precedencia que + e -).
        Chama fator() e depois verifica se ha '*' ou '/'.
        """
        no_esq = self._fator()
        return self._termo_linha(no_esq)

    # --- termoLinha -> '*' fator termoLinha | '/' fator termoLinha | <vazio> ---
    def _termo_linha(self, no_esq: No) -> No:
        """
        Continuacao de um termo: trata '*' e '/'.
        Mesma logica de _expr_linha mas para operadores de maior precedencia.
        """
        tipo = self._tipo_atual()
        if tipo == MULT:
            tok = self._consome(MULT)
            no_dir = self._fator()
            no_op  = No('op', valor=tok.valor)
            no_atual = No('termo', [no_esq, no_op, no_dir])
            return self._termo_linha(no_atual)
        elif tipo == DIV:
            tok = self._consome(DIV)
            no_dir = self._fator()
            no_op  = No('op', valor=tok.valor)
            no_atual = No('termo', [no_esq, no_op, no_dir])
            return self._termo_linha(no_atual)
        else:
            return no_esq   # producao vazia

    # --- fator -> NUM_INT | NUM_DEC | ID | '(' expr ')' ---
    def _fator(self) -> No:
        """
        Unidade basica de uma expressao (maior precedencia de todos).
        Pode ser:
          - Um numero inteiro: 42
          - Um numero decimal: 3.14
          - Um identificador: x
          - Uma sub-expressao entre parenteses: (a + b)
        """
        tipo = self._tipo_atual()

        if tipo == NUM_INT:
            tok = self._consome(NUM_INT)
            return No('numInt', valor=tok.valor)

        elif tipo == NUM_DEC:
            tok = self._consome(NUM_DEC)
            return No('numDec', valor=tok.valor)

        elif tipo == ID:
            tok = self._consome(ID)
            return No('id', valor=tok.valor)

        elif tipo == ABRE_PAR:
            # Sub-expressao entre parenteses: ( expr )
            self._consome(ABRE_PAR)
            no_expr = self._expr()
            self._consome(FECHA_PAR)
            return no_expr  # retorna a sub-arvore diretamente (sem no extra)

        else:
            self._erro(f"fator invalido: '{self.atual.valor}'")
