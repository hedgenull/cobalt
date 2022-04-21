#include <stdio.h>

int main (void) {
float a;
float b;
float i;
float c;
Begin:
a = 1;
b = 1;
printf("Enter a number: \n");
if (0 == scanf("%f", &i)) {
i = 0;
scanf("%*s");
}
while (i>0) {
printf("%.2f\n", (float)(a+b));
c = a;
a = b;
b = b+c;
i = i-1;
}
goto Begin;
return 0;
}
