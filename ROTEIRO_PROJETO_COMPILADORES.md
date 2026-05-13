﻿# Roteiro de Desenvolvimento — Compilador (CC6252)

> **Prof. Diogo F. S. Ramos** | FEI  
> Documentação: **11/05/2026** · Projeto: **13/05/2026** · Apresentação: **13–14/05/2026**  
> Hoje: **08/04/2026** → Você tem ~5 semanas.

---

## Visão Geral do que você vai construir

Seu compilador é um programa que lê um arquivo de texto escrito na linguagem que **você inventou** e gera um arquivo de saída equivalente em outra linguagem (C, Java, Python — o professor decide após você entregar a gramática).

O fluxo interno é exatamente o que foi mostrado na Aula 01:

```
Arquivo de entrada
      ↓
[Analisador Léxico]   → lê caractere por caractere → gera lista de tokens
      ↓
[Analisador Sintático] → lê tokens → verifica estrutura → gera árvore
      ↓
[Gerador de Código]    → percorre a árvore → escreve o arquivo de saída
```

Cada bloco desse vira uma parte separada do código. São **3 módulos independentes** — e essa separação é o que faz o projeto ser gerenciável.

---

## Cronograma Sugerido (5 semanas)

| Semana | Datas | O que fazer |
|--------|-------|-------------|
| 1 | 08/04 – 14/04 | Definir a linguagem: tokens + gramática completa |
| 2 | 15/04 – 21/04 | Implementar o Analisador Léxico |
| 3 | 22/04 – 28/04 | Implementar o Analisador Sintático (parser) |
| 4 | 29/04 – 05/05 | Implementar o Gerador de Código + testes |
| 5 | 06/05 – 11/05 | Ajustes, mensagens de erro, documentação, ensaio da apresentação |

---

## ETAPA 1 — Definir a Linguagem (Semana 1)

Esta é a etapa mais importante. Se a gramática estiver errada, tudo que vier depois vai ser difícil. Faça isso com calma.

### 1.1 — Escolha os Tokens (Analisador Léxico)

Um token é a menor unidade com significado na sua linguagem. Você precisa definir uma **expressão regular** para cada um. Abaixo está um conjunto mínimo recomendado, baseado nos exercícios da Aula 04:

| Token | Expressão Regular | Exemplo |
|-------|------------------|---------|
| `ID` | `[a-zA-Z][a-zA-Z0-9_]*` | `nome`, `x1`, `contador` |
| `NUM_INT` | `[0-9]+` | `42`, `100` |
| `NUM_DEC` | `[0-9]+'.'[0-9]+` | `3.14`, `0.5` |
| `TEXTO` | `'"'[qualquer caractere]*'"'` | `"olá mundo"` |
| `BOOL` | `verdadeiro` ou `falso` | `verdadeiro` |
| `TIPO_INT` | palavra reservada `inteiro` | `inteiro` |
| `TIPO_DEC` | palavra reservada `decimal` | `decimal` |
| `TIPO_TEXTO` | palavra reservada `texto` | `texto` |
| `SE` | `se` | |
| `SENAO` | `senao` | |
| `ENQUANTO` | `enquanto` | |
| `FACA` | `faca` | |
| `PARA` | `para` | |
| `LEIA` | `leia` | |
| `ESCREVA` | `escreva` | |
| `PROGRAMA` | `programa` | |
| `FIMPROG` | `fimprog` | |
| `ATRIB` | `:=` | |
| `OP_REL` | `<`, `>`, `<=`, `>=`, `==`, `!=` | |
| `OP_MAT` | `+`, `-`, `*`, `/` | |
| `ABRE_PAR` | `(` | |
| `FECHA_PAR` | `)` | |
| `ABRE_CHAVE` | `{` | |
| `FECHA_CHAVE` | `}` | |
| `PONTO` | `.` | (fim de comando) |

> **Dica:** palavras reservadas (`se`, `enquanto`, etc.) devem ser verificadas **antes** do token `ID`, pois um ID também começaria com letra. A ordem de reconhecimento importa (conforme a Aula 04).

### 1.2 — Escreva a Gramática (Analisador Sintático)

A gramática descreve as estruturas válidas da sua linguagem. Use o modelo da Aula 08 (Descendente Recursivo): **uma regra = uma função**.

Regras críticas do professor:
- **Proibido recursividade à esquerda** (ex: `expr → expr + fator` é proibido diretamente)
- Deve haver eliminação de recursão e fatoração quando necessário

**Gramática mínima sugerida:**

```
prog       → 'programa' bloco 'fimprog' '.'

bloco      → cmd bloco | ε

cmd        → declara | cmdAtrib | cmdSe | cmdEnquanto | cmdPara |
             cmdFaca | cmdLeia | cmdEscreva

declara    → tipo ID '.'
tipo       → 'inteiro' | 'decimal' | 'texto'

cmdAtrib   → ID ':=' expr '.'

cmdSe      → 'se' '(' expr op_rel expr ')' '{' bloco '}' senao_opt
senao_opt  → 'senao' '{' bloco '}' | ε

cmdEnquanto → 'enquanto' '(' expr op_rel expr ')' '{' bloco '}'

cmdFaca    → 'faca' '{' bloco '}' 'enquanto' '(' expr op_rel expr ')' '.'

cmdPara    → 'para' '(' cmdAtrib_sem_ponto ';' expr op_rel expr ';'
              ID ':=' expr ')' '{' bloco '}'

cmdLeia    → 'leia' '(' ID ')' '.'
cmdEscreva → 'escreva' '(' conteudo ')' '.'
conteudo   → TEXTO | ID | expr

op_rel     → '<' | '>' | '<=' | '>=' | '==' | '!='

--- Expressões com precedência correta (sem recursividade à esquerda) ---

expr       → termo expr'
expr'      → '+' termo expr' | '-' termo expr' | ε

termo      → fator termo'
termo'     → '*' fator termo' | '/' fator termo' | ε

fator      → NUM_INT | NUM_DEC | ID | '(' expr ')'
```

> **Por que essa estrutura de expr/expr'?** Porque `expr → expr + termo` tem recursividade à esquerda. A versão com `expr'` é o resultado da **eliminação de recursividade à esquerda**, exatamente o que o prof. pediu. Isso também garante a precedência correta: `*` e `/` são resolvidos antes de `+` e `-`.

---

## ETAPA 2 — Analisador Léxico (Semana 2) — vale 3 pontos

O léxico lê o arquivo de entrada **caractere por caractere** e retorna tokens.

### O que implementar:

**1. Estrutura de um Token**
```python
# Exemplo em Python
class Token:
    def __init__(self, tipo, valor, linha):
        self.tipo  = tipo   # ex: "ID", "NUM_INT", "SE"
        self.valor = valor  # ex: "contador", "42", "se"
        self.linha = linha  # para mensagens de erro
```

**2. A função `proximo_token()`**

Esta função é o coração do léxico. Ela:
1. Ignora espaços, tabs e quebras de linha
2. Olha o próximo caractere
3. Decide qual token está sendo lido
4. Consome os caracteres necessários
5. Retorna o Token completo

Pseudocódigo (baseado nos exemplos da Aula 04 e 08):
```
função proximo_token():
    pula_espacos()
    
    se chegou ao fim do arquivo:
        retorna Token(EOF, "", linha_atual)
    
    c = lê próximo caractere
    
    se c é letra:
        lê enquanto for letra ou dígito → forma a palavra
        se palavra está na tabela de palavras_reservadas:
            retorna Token(palavra_reservada, palavra, linha)
        senão:
            retorna Token(ID, palavra, linha)
    
    se c é dígito:
        lê enquanto for dígito
        se próximo for '.':
            lê o ponto e os dígitos seguintes
            retorna Token(NUM_DEC, valor, linha)
        senão:
            retorna Token(NUM_INT, valor, linha)
    
    se c == '"':
        lê até encontrar o próximo '"'
        retorna Token(TEXTO, conteúdo, linha)
    
    se c == ':':
        se próximo for '=':
            retorna Token(ATRIB, ":=", linha)
        senão:
            ERRO léxico
    
    se c == '<':
        se próximo for '=': retorna Token(OP_REL, "<=", linha)
        senão: retorna Token(OP_REL, "<", linha)
    
    ... (mesmo para os outros operadores)
    
    retorna Token(DESCONHECIDO, c, linha) → gera erro
```

**3. Função para imprimir a lista de tokens** (vale 1 ponto!)
```python
def imprime_tokens(lista_tokens):
    for tok in lista_tokens:
        print(f"Linha {tok.linha}: [{tok.tipo}] '{tok.valor}'")
```

**Atenção crítica:** O professor dá 1 ponto por **não usar bibliotecas de expressões regulares** (como `re` do Python ou `Pattern` do Java). Faça tudo na mão, comparando caractere por caractere.

---

## ETAPA 3 — Analisador Sintático (Semana 3) — vale 4 pontos

O parser recebe a lista de tokens do léxico e verifica se a estrutura do programa está correta, construindo a árvore de derivação.

### Abordagem: Descendente Recursivo (Aula 08)

A regra de ouro: **uma função por regra gramatical**.

**Estrutura base do parser:**

```python
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.token_atual = tokens[0]

    def consome(self, tipo_esperado):
        """Verifica se o token atual é o esperado e avança."""
        if self.token_atual.tipo == tipo_esperado:
            token = self.token_atual
            self.pos += 1
            self.token_atual = self.tokens[self.pos]
            return token
        else:
            self.erro(f"Esperado '{tipo_esperado}', encontrado '{self.token_atual.valor}'")

    def erro(self, mensagem):
        linha = self.token_atual.linha
        print(f"ERRO SINTÁTICO na linha {linha}: {mensagem}")
        exit(1)
```

**Exemplo de funções do parser** (baseado no pseudocódigo da Aula 08):

```python
def prog(self):
    self.consome('PROGRAMA')
    no_bloco = self.bloco()
    self.consome('FIMPROG')
    self.consome('PONTO')
    return No('prog', [no_bloco])

def bloco(self):
    filhos = []
    while self.token_atual.tipo not in ['FIMPROG', 'FECHA_CHAVE']:
        filhos.append(self.cmd())
    return No('bloco', filhos)

def cmd(self):
    tok = self.token_atual.tipo
    if tok in ['INTEIRO', 'DECIMAL', 'TEXTO']:
        return self.declara()
    elif tok == 'ID':
        return self.cmdAtrib()
    elif tok == 'SE':
        return self.cmdSe()
    elif tok == 'ENQUANTO':
        return self.cmdEnquanto()
    elif tok == 'FACA':
        return self.cmdFaca()
    elif tok == 'PARA':
        return self.cmdPara()
    elif tok == 'LEIA':
        return self.cmdLeia()
    elif tok == 'ESCREVA':
        return self.cmdEscreva()
    else:
        self.erro(f"Comando inválido: '{self.token_atual.valor}'")

def cmdSe(self):
    self.consome('SE')
    self.consome('ABRE_PAR')
    cond = self.expr_relacional()
    self.consome('FECHA_PAR')
    self.consome('ABRE_CHAVE')
    bloco_se = self.bloco()
    self.consome('FECHA_CHAVE')
    bloco_senao = None
    if self.token_atual.tipo == 'SENAO':
        self.consome('SENAO')
        self.consome('ABRE_CHAVE')
        bloco_senao = self.bloco()
        self.consome('FECHA_CHAVE')
    return No('cmdSe', [cond, bloco_se, bloco_senao])
```

**A Árvore de Derivação (vale 1 ponto):**

Crie uma classe `No` simples. Basta guardar o tipo do nó e seus filhos:
```python
class No:
    def __init__(self, tipo, filhos=None, valor=None):
        self.tipo   = tipo
        self.filhos = filhos or []
        self.valor  = valor  # para folhas (ID, NUM, etc.)

    def imprimir(self, nivel=0):
        print("  " * nivel + f"[{self.tipo}]" + (f" '{self.valor}'" if self.valor else ""))
        for filho in self.filhos:
            if filho:
                filho.imprimir(nivel + 1)
```

---

## ETAPA 4 — Gerador de Código (Semana 4) — vale 2 pontos

O gerador percorre a árvore construída pelo parser e gera o texto do código na linguagem destino. É basicamente uma função recursiva que visita cada nó.

O professor vai te dizer a linguagem destino depois que você entregar a gramática. Mas já prepare a estrutura:

```python
class Gerador:
    def __init__(self, arvore):
        self.arvore = arvore
        self.saida = []
        self.indent = 0

    def gerar(self, no):
        if no.tipo == 'prog':
            # Ex: para C → "#include <stdio.h>\nint main(void) {"
            self.saida.append('#include <stdio.h>')
            self.saida.append('int main(void) {')
            self.indent += 1
            self.gerar(no.filhos[0])  # bloco
            self.indent -= 1
            self.saida.append('}')

        elif no.tipo == 'declara':
            tipo = no.filhos[0].valor   # "inteiro"
            nome = no.filhos[1].valor   # "x"
            tipo_c = {'inteiro': 'int', 'decimal': 'double', 'texto': 'char*'}[tipo]
            self.saida.append('  ' * self.indent + f'{tipo_c} {nome};')

        elif no.tipo == 'cmdAtrib':
            # ID := expr → ID = expr;
            ...

        elif no.tipo == 'cmdSe':
            # se ( cond ) { bloco } senao { bloco }
            ...

        # ... etc para cada tipo de nó

    def escrever_arquivo(self, caminho):
        with open(caminho, 'w') as f:
            f.write('\n'.join(self.saida))
```

**Dica de mapeamento** (caso a linguagem destino seja C, que é o exemplo do prof.):

| Sua linguagem | C |
|--------------|---|
| `inteiro x.` | `int x;` |
| `decimal y.` | `double y;` |
| `texto s.` | `char* s;` |
| `x := expr.` | `x = expr;` |
| `escreva("msg").` | `printf("msg");` |
| `escreva(x).` | `printf("%d", x);` (int) ou `printf("%lf", x);` (double) |
| `leia(x).` | `scanf("%d", &x);` |
| `se (a < b) { }` | `if (a < b) { }` |
| `enquanto (a < b) { }` | `while (a < b) { }` |
| `faca { } enquanto (cond).` | `do { } while (cond);` |
| `para (i := 0; i < 10; i := i + 1) { }` | `for (i = 0; i < 10; i = i + 1) { }` |

---

## ETAPA 5 — Mensagens de Erro e Ajustes (Semana 5)

O prof. exige mensagens de erro tanto no léxico quanto no sintático. Exemplos de erros para cobrir:

**Erros Léxicos:**
- Caractere inválido: `ERRO LÉXICO na linha 5: caractere '@' não reconhecido`
- String não fechada: `ERRO LÉXICO na linha 3: string não finalizada`

**Erros Sintáticos:**
- Token inesperado: `ERRO SINTÁTICO na linha 7: esperado '.', encontrado 'fimprog'`
- Bloco não fechado: `ERRO SINTÁTICO na linha 12: esperado '}', encontrado EOF`
- Comando inválido: `ERRO SINTÁTICO na linha 4: 'decimal' é inválido aqui`

---

## Como Rodar o Compilador (estrutura do main)

```python
# main.py
import sys

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo.ext>")
        exit(1)

    arquivo_entrada = sys.argv[1]
    arquivo_saida   = arquivo_entrada.replace('.ext', '.c')

    # 1. Leitura do arquivo
    with open(arquivo_entrada, 'r') as f:
        codigo = f.read()

    # 2. Análise Léxica
    lexico = Lexico(codigo)
    tokens = lexico.tokenizar()
    lexico.imprimir_tokens(tokens)  # para o ponto da impressão de tokens

    # 3. Análise Sintática
    parser = Parser(tokens)
    arvore = parser.prog()
    arvore.imprimir()  # para o ponto da árvore de derivação

    # 4. Geração de Código
    gerador = Gerador(arvore)
    gerador.gerar(arvore)
    gerador.escrever_arquivo(arquivo_saida)

    print(f"\nCódigo gerado em: {arquivo_saida}")

if __name__ == '__main__':
    main()
```

---

## Divisão de Tarefas no Grupo (sugestão para 4-5 pessoas)

| Pessoa | Responsabilidade |
|--------|-----------------|
| 1 | Gramática + tokens (define tudo, documenta) |
| 2 | Analisador Léxico completo |
| 3 | Analisador Sintático — estruturas (prog, bloco, cmd, declara, if, while) |
| 4 | Analisador Sintático — expressões (expr, termo, fator) + árvore |
| 5 | Gerador de código + testes + integração |

> Todos precisam entender o projeto inteiro para a apresentação — o prof. é eliminatório se alguém não souber responder.

---

## Checklist Final (antes de entregar)

### Documentação (até 11/05)
- [ ] Título e componentes do grupo
- [ ] Expressões regulares de todos os tokens
- [ ] Gramática completa (sem recursividade à esquerda)
- [ ] Instruções de execução
- [ ] Exemplos de código na sua linguagem com a tradução equivalente

### Projeto (até 13/05)
- [ ] Léxico funciona e imprime lista de tokens
- [ ] Léxico NÃO usa biblioteca de regex
- [ ] Parser aceita programas válidos
- [ ] Parser gera árvore de derivação
- [ ] Parser apresenta mensagens de erro úteis
- [ ] Gerador produz código correto na linguagem destino
- [ ] O código gerado compila/executa sem erros
- [ ] Testado com: declarações, if/else encadeado, while, do/while, for, expressões com precedência, leia, escreva

---

## Exemplo completo de programa na linguagem sugerida

```
programa

inteiro a.
inteiro b.
inteiro resultado.
decimal media.

escreva("Digite dois numeros").
leia(a).
leia(b).

se (a > b) {
    resultado := a - b.
} senao {
    resultado := b - a.
}

escreva("Diferenca: ").
escreva(resultado).

media := (a + b) / 2.

inteiro i.
i := 0.
enquanto (i < resultado) {
    escreva(i).
    i := i + 1.
}

fimprog.
```

---

*Roteiro elaborado com base no enunciado do Prof. Diogo F. S. Ramos e nos conteúdos das aulas (Introdução, Análise Léxica, Gramáticas, Análise Sintática Descendente Recursiva) — FEI, CC6252, 2026.*
