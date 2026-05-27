// https://www-geeksforgeeks-org.translate.goog/dsa/program-to-calculate-ex-by-recursion/?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=es&_x_tr_pto=tc&_x_tr_hist=true
// Modified with ChatGPT

#include <stdio.h>

float e(int x, int n)
{
    float result = 1;
    float term = 1;
    int i = 1;

    while (i <= n) {
        term = term * x / i;
        result = result + term;
        i = i + 1;
    }

    return result;
}

int main()
{
    int x = 4;
    int n = 15;

    printf("%lf \n", e(x, n));

    return 0;
}