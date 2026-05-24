//Aproxima e^x usando la serie e^x = 1 + x + x^2/2! + x^3/3! + [...]

double taylor() {
    double x = 1;
    double result = 1;
    double term = 1;
    int n = 5;
    int i = 1;

    for (i = 1; i <= n; i = i + 1) {
        term = term * x / i;
        result = result + term;
    }

    return result;
}