#include<stdio.h>
#include<string.h>
int main()
{
	char a[100];
    scanf("%s",a);
	int len = strlen(a);
	for (int i = 1; i <= len; i++)
	{
		for (int j = 1; j <= len - i; j++)
			printf(" ");
		for (int j = 0; j < i; j++)
			printf("%c", a[j]);
		for (int j = i-2; j >= 0; j--)
			printf("%c", a[j]);
		printf("\n");
	}
	for (int i = 1; i < len; i++)
	{
		for (int j = 1; j <= i; j++)
		{
			printf(" ");
		}
		for (int j = i; j < len; j++)
			printf("%c", a[j]);
		for (int j = len-2; j >= i; j--)
			printf("%c", a[j]);
		printf("\n");
	}
	return 0;
}