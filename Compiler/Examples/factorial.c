// LLVM IR: Estructuras de control
// Modified Manually
#include <stdio.h>

int factorial(int n)
{
    int f = 1;
    int i = 1;
    while (i <= n) {
        f = f * i;
        i = i + 1;
    }
    return f;
}

int main()
{
    int result;

    result = factorial(5);

    printf("Factorial de 5 = %d\n", result);

    return result;
}