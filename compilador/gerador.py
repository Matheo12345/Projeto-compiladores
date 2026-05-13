# =============================================================================
# gerador.py — Gerador de Código C
# Compilador — CC6252 | Prof. Diogo F. S. Ramos | FEI
#
# Percorre a árvore de derivação produzida pelo Parser e gera código C válido.
# =============================================================================


# Mapeamento de tipos da linguagem fonte para C
_TIPO_C = {
    'inteiro': 'int',
    'decimal': 'double',
    'texto':   'char*',
}

# Formato de printf/scanf por tipo
_FMT_PRINTF = {
    'inteiro': '%d',
    'decimal': '%lf',
    'texto':   '%s',
}
_FMT_SCANF = {
    'inteiro': '%d',
    'decimal': '%lf',
    'texto':   '%s',
}


class Gerador:
    """
    Gerador de Código C.

    Uso:
        gerador = Gerador(arvore)
        codigo_c = gerador.gerar()
        gerador.escrever_arquivo('saida.c')
    """

    def __init__(self, arvore):
        self.arvore   = arvore
        self._linhas  = []       # linhas do código C gerado
        self._indent  = 0        # nível de indentação atual
        self._tabela  = {}       # tabela de símbolos: nome → tipo ('inteiro'|'decimal'|'texto')
        self._erros   = []

    # -----------------------------------------------------------------------
    # Ponto de entrada público
    # -----------------------------------------------------------------------

    def gerar(self) -> str:
        """Gera o código C e retorna como string."""
        self._coletar_tipos(self.arvore)   # 1ª passagem: monta tabela de símbolos
        self._gerar_prog(self.arvore)      # 2ª passagem: gera o código
        return '\n'.join(self._linhas)

    def escrever_arquivo(self, caminho: str):
        """Grava o código C gerado em um arquivo."""
        codigo = self.gerar() if not self._linhas else '\n'.join(self._linhas)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(codigo)
        print(f'Código C gerado em: {caminho}')

    # -----------------------------------------------------------------------
    # 1ª passagem — coleta declarações para montar a tabela de símbolos
    # Necessário para saber o tipo de cada variável ao gerar printf/scanf
    # -----------------------------------------------------------------------

    def _coletar_tipos(self, no):
        if no is None:
            return
        if no.tipo == 'declara':
            tipo_fonte = no.filhos[0].valor   # 'inteiro', 'decimal' ou 'texto'
            nome       = no.filhos[1].valor   # nome do ID
            self._tabela[nome] = tipo_fonte
        for filho in no.filhos:
            self._coletar_tipos(filho)

    # -----------------------------------------------------------------------
    # Helpers de escrita
    # -----------------------------------------------------------------------

    def _escreve(self, linha: str):
        self._linhas.append('    ' * self._indent + linha)

    def _abre_bloco(self):
        self._escreve('{')
        self._indent += 1

    def _fecha_bloco(self):
        self._indent -= 1
        self._escreve('}')

    # -----------------------------------------------------------------------
    # Geração por tipo de nó
    # -----------------------------------------------------------------------

    def _gerar_prog(self, no):
        """prog → cabeçalho C + bloco + rodapé"""
        self._escreve('#include <stdio.h>')
        self._escreve('#include <stdlib.h>')
        self._escreve('')
        self._escreve('int main(void)')
        self._abre_bloco()
        self._gerar_bloco(no.filhos[0])
        self._escreve('')
        self._escreve('return 0;')
        self._fecha_bloco()

    def _gerar_bloco(self, no):
        for filho in no.filhos:
            self._gerar_cmd(filho)

    def _gerar_cmd(self, no):
        despacho = {
            'declara':    self._gerar_declara,
            'cmdAtrib':   self._gerar_atrib,
            'cmdSe':      self._gerar_se,
            'cmdEnquanto':self._gerar_enquanto,
            'cmdFaca':    self._gerar_faca,
            'cmdPara':    self._gerar_para,
            'cmdLeia':    self._gerar_leia,
            'cmdEscreva': self._gerar_escreva,
        }
        fn = despacho.get(no.tipo)
        if fn:
            fn(no)
        else:
            self._erro(f"Nó desconhecido: '{no.tipo}'", no)

    # declara → tipo ID  →  int x;
    def _gerar_declara(self, no):
        tipo_fonte = no.filhos[0].valor
        nome       = no.filhos[1].valor
        tipo_c     = _TIPO_C.get(tipo_fonte, 'int')
        self._escreve(f'{tipo_c} {nome};')

    # cmdAtrib → ID := expr  →  ID = expr;
    def _gerar_atrib(self, no):
        nome = no.filhos[0].valor
        expr = self._gerar_expr(no.filhos[1])
        self._escreve(f'{nome} = {expr};')

    # Versão inline usada dentro do for — retorna string sem ponto-e-vírgula
    def _gerar_atrib_inline(self, no) -> str:
        nome = no.filhos[0].valor
        expr = self._gerar_expr(no.filhos[1])
        return f'{nome} = {expr}'

    # cmdSe → se (cond) { bloco } [senao { bloco }]
    def _gerar_se(self, no):
        cond       = self._gerar_expr_rel(no.filhos[0])
        bloco_se   = no.filhos[1]
        bloco_senao = no.filhos[2] if len(no.filhos) > 2 else None

        self._escreve(f'if ({cond})')
        self._abre_bloco()
        self._gerar_bloco(bloco_se)
        self._fecha_bloco()

        if bloco_senao is not None:
            self._escreve('else')
            self._abre_bloco()
            self._gerar_bloco(bloco_senao)
            self._fecha_bloco()

    # cmdEnquanto → enquanto (cond) { bloco }
    def _gerar_enquanto(self, no):
        cond = self._gerar_expr_rel(no.filhos[0])
        self._escreve(f'while ({cond})')
        self._abre_bloco()
        self._gerar_bloco(no.filhos[1])
        self._fecha_bloco()

    # cmdFaca → faca { bloco } enquanto (cond)
    def _gerar_faca(self, no):
        self._escreve('do')
        self._abre_bloco()
        self._gerar_bloco(no.filhos[0])
        self._fecha_bloco()
        cond = self._gerar_expr_rel(no.filhos[1])
        self._escreve(f'while ({cond});')

    # cmdPara → para (init; cond; passo) { bloco }
    def _gerar_para(self, no):
        init  = self._gerar_atrib_inline(no.filhos[0])
        cond  = self._gerar_expr_rel(no.filhos[1])
        passo = self._gerar_atrib_inline(no.filhos[2])
        self._escreve(f'for ({init}; {cond}; {passo})')
        self._abre_bloco()
        self._gerar_bloco(no.filhos[3])
        self._fecha_bloco()

    # cmdLeia → leia(ID)  →  scanf("%d", &x);
    def _gerar_leia(self, no):
        nome = no.filhos[0].valor
        tipo = self._tabela.get(nome, 'inteiro')
        fmt  = _FMT_SCANF[tipo]
        # char* não precisa de & no scanf
        ref  = nome if tipo == 'texto' else f'&{nome}'
        self._escreve(f'scanf("{fmt}", {ref});')

    # cmdEscreva → escreva(conteudo)
    # conteudo pode ser: TEXTO_LIT, ID, NUM_INT, NUM_DEC ou expr composta
    def _gerar_escreva(self, no):
        conteudo = no.filhos[0]

        if conteudo.tipo == 'TEXTO_LIT':
            texto = conteudo.valor.replace('"', '\\"')
            self._escreve(f'printf("{texto}\\n");')

        elif conteudo.tipo == 'ID':
            nome = conteudo.valor
            tipo = self._tabela.get(nome, 'inteiro')
            fmt  = _FMT_PRINTF[tipo]
            self._escreve(f'printf("{fmt}\\n", {nome});')

        elif conteudo.tipo == 'NUM_INT':
            self._escreve(f'printf("%d\\n", {conteudo.valor});')

        elif conteudo.tipo == 'NUM_DEC':
            self._escreve(f'printf("%lf\\n", {conteudo.valor});')

        else:
            # Expressão composta: infere tipo pelo resultado (usa %lf se houver decimal)
            expr_str = self._gerar_expr(conteudo)
            fmt = '%lf' if self._expr_e_decimal(conteudo) else '%d'
            self._escreve(f'printf("{fmt}\\n", {expr_str});')

    # -----------------------------------------------------------------------
    # Geração de expressões — retornam string C
    # -----------------------------------------------------------------------

    def _gerar_expr_rel(self, no) -> str:
        """exprRel → expr op_rel expr"""
        esq = self._gerar_expr(no.filhos[0])
        op  = no.filhos[1].valor
        dir_ = self._gerar_expr(no.filhos[2])
        return f'{esq} {op} {dir_}'

    def _gerar_expr(self, no) -> str:
        """Gera qualquer nó de expressão como string C."""
        if no.tipo in ('expr', 'termo'):
            # nó binário: [esq, OP, dir]
            esq  = self._gerar_expr(no.filhos[0])
            op   = no.filhos[1].valor
            dir_ = self._gerar_expr(no.filhos[2])
            return f'({esq} {op} {dir_})'

        elif no.tipo == 'ID':
            return no.valor

        elif no.tipo in ('NUM_INT', 'NUM_DEC'):
            return no.valor

        elif no.tipo == 'VERDADEIRO':
            return '1'

        elif no.tipo == 'FALSO':
            return '0'

        elif no.tipo == 'TEXTO_LIT':
            return f'"{no.valor}"'

        else:
            self._erro(f"Expressão desconhecida: '{no.tipo}'", no)
            return '0'

    def _expr_e_decimal(self, no) -> bool:
        """Retorna True se a expressão contém algum decimal."""
        if no is None:
            return False
        if no.tipo == 'NUM_DEC':
            return True
        if no.tipo == 'ID':
            return self._tabela.get(no.valor) == 'decimal'
        return any(self._expr_e_decimal(f) for f in no.filhos)

    # -----------------------------------------------------------------------
    # Erros do gerador
    # -----------------------------------------------------------------------

    def _erro(self, mensagem: str, no=None):
        linha = getattr(no, 'linha', '?') if no else '?'
        msg   = f'ERRO GERADOR na linha {linha}: {mensagem}'
        self._erros.append(msg)
        print(msg)
