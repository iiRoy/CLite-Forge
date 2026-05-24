int operationSwitch() {
    int a = 10;
    int b = 5;
    int option = 3;
    int result = 0;

    switch (option) {
        case 1:
            result = a + b;
            break;

        case 2:
            result = a - b;
            break;

        case 3:
            result = a * b;
            break;

        case 4:
            result = a / b;
            break;

        default:
            result = 0;
            break;
    }

    return result;
}