//https://data--flair-training.translate.goog/blogs/fibonacci-series-in-c-using-recursion/?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=es&_x_tr_pto=tc
#include <stdio.h>

int fib(int n) {
  if (n == 0) { 
    return 0;
  }
  if (n == 1) {
    return 1;
  }
  return fib(n-1) + fib(n-2); 
}

int main() {
  int n = 6;
  printf("Fibonacci number %d is %d", n, fib(n));
  return 0;
}