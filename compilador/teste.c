#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    int a;
    int b;
    int resultado;
    double media;
    char* mensagem;
    printf("Digite o primeiro numero\n");
    scanf("%d", &a);
    printf("Digite o segundo numero\n");
    scanf("%d", &b);
    resultado = (a + (b * 2));
    media = ((a + b) / 2);
    if (a > b)
    {
        printf("A e maior\n");
        resultado = (a - b);
    }
    else
    {
        printf("B e maior ou igual\n");
        resultado = (b - a);
    }
    if (resultado > 10)
    {
        printf("Grande\n");
    }
    else
    {
        if (resultado > 5)
        {
            printf("Medio\n");
        }
        else
        {
            printf("Pequeno\n");
        }
    }
    int i;
    i = 0;
    while (i < resultado)
    {
        printf("%d\n", i);
        i = (i + 1);
    }
    do
    {
        printf("Pelo menos uma vez\n");
        i = (i - 1);
    }
    while (i > 0);
    int j;
    for (j = 0; j < 5; j = (j + 1))
    {
        printf("%d\n", j);
    }
    if (a <= b)
    {
        printf("a menor ou igual b\n");
    }
    if (a >= b)
    {
        printf("a maior ou igual b\n");
    }
    if (a == b)
    {
        printf("iguais\n");
    }
    if (a != b)
    {
        printf("diferentes\n");
    }
    
    return 0;
}