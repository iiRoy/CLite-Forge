int summation() {
    int n = 5;
    int result = 0;

    do {
        result = result + n;
        n = n - 1;
    } while (n > 0);

    return result;
}