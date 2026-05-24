// Retorna el término número n de Fibonacci.

int fibonacci() {
    int n = 6;
    int a = 0;
    int b = 1;
    int temp = 0;
    int i = 2;

    if (n == 0) {
        return a;
    } else if (n == 1) {
        return b;
    } else {
        while (i <= n) {
            temp = a + b;
            a = b;
            b = temp;
            i = i + 1;
        }

        return b;
    }
}