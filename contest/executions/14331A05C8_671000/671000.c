#include <stdio.h>
int main()
{
    int n, reversedNumber = 0, remainder,flag=0;

    scanf("%d", &n);
	if(n<0)
      flag=1;
    while(n != 0)
    {
        remainder = n%10;
        reversedNumber = reversedNumber*10 + remainder;
        n /= 10;
    }
	if(flag==1)
    	printf("-%d\n", reversedNumber);
  	else
     printf("%d\n", reversedNumber);

    return 0;
}