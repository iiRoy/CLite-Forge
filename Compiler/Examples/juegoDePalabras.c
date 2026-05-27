// Made with ChatGPT
#include <stdio.h>

void printWord(int code)
{
    switch (code) {
        case 1:
            printf("Choco ");
            break;

        case 2:
            printf("La ");
            break;

        case 3:
            printf("Te ");
            break;
    }

    return;
}

void wordGame(int index)
{
    int sequence[15];

    sequence[0] = 1;
    sequence[1] = 1;
    sequence[2] = 2;
    sequence[3] = 2;
    sequence[4] = 1;
    sequence[5] = 1;
    sequence[6] = 3;
    sequence[7] = 3;
    sequence[8] = 1;
    sequence[9] = 2;
    sequence[10] = 1;
    sequence[11] = 3;
    sequence[12] = 1;
    sequence[13] = 2;
    sequence[14] = 3;

    if (index >= 15) {
        printf("\n");
        return;
    }

    printWord(sequence[index]);
    wordGame(index + 1);

    return;
}

int main()
{
    wordGame(0);
    return 0;
}