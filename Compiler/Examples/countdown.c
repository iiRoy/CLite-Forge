// https://www.w3schools.com/c/c_functions_recursion.php
// Modified manually
#include <stdio.h>

void countdown(int n)
{
    if (n >= 0) {
        printf("%d \n", n);
        countdown(n - 1);
    }

    return;
}

int main()
{
    countdown(5);
    return 0;
}