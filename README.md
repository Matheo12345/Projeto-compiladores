# Compilador -- CC6252

Projeto da disciplina de Compiladores (CC6252), Prof. Charles Ferreira -- FEI.

Implementacao de um compilador completo para uma linguagem imperativa criada pelo grupo, escrita em portugues. O compilador e desenvolvido em Python e traduz programas na linguagem criada para codigo em C.

---

## Como executar

```bash
cd compilador
python main.py <arquivo.prog>

# Exemplo com o arquivo de teste incluso:
python main.py teste.prog
```

**Requisito:** Python 3.6 ou superior.

---

## Estrutura do projeto

```
compilador/
|-- tokens.py      # Definicao dos tipos de tokens e classe Token
|-- lexico.py      # Analisador lexico (Etapa 2)
|-- main.py        # Ponto de entrada do compilador
|-- teste.prog     # Programa de teste cobrindo toda a linguagem
```

---

## Tokens da linguagem

O reconhecimento e feito caractere a caractere, sem uso de nenhuma biblioteca de expressoes regulares.

### Palavras reservadas

| Token        | Lexema       | Descricao                      |
|--------------|--------------|--------------------------------|
| `PROGRAMA`   | `programa`   | Inicio do programa             |
| `FIMPROG`    | `fimprog`    | Fim do programa                |
| `INTEIRO`    | `inteiro`    | Tipo inteiro                   |
| `DECIMAL`    | `decimal`    | Tipo decimal (ponto flutuante) |
| `TEXTO_TIPO` | `texto`      | Tipo texto (string)            |
| `SE`         | `se`         | Condicional if                 |
| `SENAO`      | `senao`      | Alternativa else               |
| `ENQUANTO`   | `enquanto`   | Laco while                     |
| `FACA`       | `faca`       | Inicio do laco do-while        |
| `PARA`       | `para`       | Laco for                       |
| `LEIA`       | `leia`       | Entrada de dados               |
| `ESCREVA`    | `escreva`    | Saida de dados                 |
| `VERDADEIRO` | `verdadeiro` | Literal booleano verdadeiro    |
| `FALSO`      | `falso`      | Literal booleano falso         |

### Literais e identificadores

| Token      | Expressao regular (conceitual)       | Exemplo          |
|------------|--------------------------------------|------------------|
| `ID`       | `[a-zA-Z_][a-zA-Z0-9_]*`            | `contador`, `x1` |
| `NUM_INT`  | `[0-9]+`                             | `42`, `100`      |
| `NUM_DEC`  | `[0-9]+ '.' [0-9]+`                 | `3.14`, `0.5`    |
| `TEXTO_LIT`| `'"' [qualquer char exceto \n]* '"'` | `"ola mundo"`    |

### Operadores

| Token      | Lexema | Descricao        |
|------------|--------|------------------|
| `ATRIB`    | `:=`   | Atribuicao       |
| `MAIS`     | `+`    | Adicao           |
| `MENOS`    | `-`    | Subtracao        |
| `MULT`     | `*`    | Multiplicacao    |
| `DIV`      | `/`    | Divisao          |
| `MENOR`    | `<`    | Menor que        |
| `MAIOR`    | `>`    | Maior que        |
| `MENOR_IG` | `<=`   | Menor ou igual   |
| `MAIOR_IG` | `>=`   | Maior ou igual   |
| `IGUAL`    | `==`   | Igual a          |
| `DIF`      | `!=`   | Diferente de     |

### Delimitadores

| Token        | Lexema | Descricao                     |
|--------------|--------|-------------------------------|
| `ABRE_PAR`   | `(`    | Abre parentese                |
| `FECHA_PAR`  | `)`    | Fecha parentese               |
| `ABRE_CHAVE` | `{`    | Abre bloco                    |
| `FECHA_CHAVE`| `}`    | Fecha bloco                   |
| `PONTO`      | `.`    | Fim de comando/declaracao     |
| `PONTO_VIRG` | `;`    | Separador no comando `para`   |
| `EOF`        | --     | Fim do arquivo                |

### Comentarios

Linhas iniciadas com `//` sao ignoradas pelo lexico.

---

## Gramatica da linguagem

A gramatica e livre de recursividade a esquerda e utiliza analise **descendente recursiva** (uma funcao por regra). A precedencia de operadores e garantida pela hierarquia `expr -> termo -> fator`.

```
prog        ->  'programa' bloco 'fimprog' '.'

bloco       ->  cmd bloco  |  <vazio>

cmd         ->  declara
            |   cmdAtrib
            |   cmdSe
            |   cmdEnquanto
            |   cmdFaca
            |   cmdPara
            |   cmdLeia
            |   cmdEscreva

declara     ->  tipo ID '.'
tipo        ->  'inteiro'  |  'decimal'  |  'texto'

cmdAtrib    ->  ID ':=' expr '.'

cmdSe       ->  'se' '(' exprRel ')' '{' bloco '}' senaoOpt
senaoOpt    ->  'senao' '{' bloco '}'  |  <vazio>

cmdEnquanto ->  'enquanto' '(' exprRel ')' '{' bloco '}'

cmdFaca     ->  'faca' '{' bloco '}' 'enquanto' '(' exprRel ')' '.'

cmdPara     ->  'para' '(' ID ':=' expr ';' exprRel ';' ID ':=' expr ')' '{' bloco '}'

cmdLeia     ->  'leia' '(' ID ')' '.'

cmdEscreva  ->  'escreva' '(' conteudo ')' '.'
conteudo    ->  TEXTO_LIT  |  ID  |  expr

exprRel     ->  expr opRel expr
opRel       ->  '<'  |  '>'  |  '<='  |  '>='  |  '=='  |  '!='

expr        ->  termo exprLinha
exprLinha   ->  '+' termo exprLinha  |  '-' termo exprLinha  |  <vazio>

termo       ->  fator termoLinha
termoLinha  ->  '*' fator termoLinha  |  '/' fator termoLinha  |  <vazio>

fator       ->  NUM_INT  |  NUM_DEC  |  ID  |  '(' expr ')'
```

> `expr/exprLinha` e `termo/termoLinha` eliminam a recursividade a esquerda de `expr -> expr + termo`.
> Isso garante que `*` e `/` tenham precedencia sobre `+` e `-`.

---

## Exemplo de programa

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

## Estado de desenvolvimento

| Etapa | Descricao                                       | Status    |
|-------|-------------------------------------------------|-----------|
| 1     | Definicao da linguagem (tokens + gramatica)     | Concluida |
| 2     | Analisador lexico                               | Concluida |
| 3     | Analisador sintatico (parser + arvore)          | Pendente  |
| 4     | Gerador de codigo                               | Pendente  |
| 5     | Mensagens de erro e ajustes finais              | Pendente  |
