//Retorna la cantidad mínima de movimientos necesarios para n discos.

int hanoiTower() {
    int n = 3;
    int moves = 1;
    int i = 0;

    while (i < n) {
        moves = moves * 2;
        i = i + 1;
    }

    moves = moves - 1;

    return moves;
}