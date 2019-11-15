
#include <stdlib.h>
#include <stdio.h>
#include <time.h>

extern int script_load(char* filename);
extern void frame_renderframes();

extern int tokens;
extern void quicksqrtinit(int increaserange);
extern void quickrecipinit(int increaserange);
extern int spriteinitialized;

int main(int argc, char** argv)
{
	int i;
	int starttime;
	int endtime;
	printf("lhfire 1.10 by Forest \"LordHavoc\" Hale\n");
	if (argc >= 2 && argv[1])
	{
		starttime = time(NULL);
		quicksqrtinit(0);
		quickrecipinit(0);
		for (i = 1;i < argc;i++)
		{
			spriteinitialized = 0;
			script_load(argv[i]);
			if (tokens > 0)
				frame_renderframes();
			else
				printf("unable to load script %s\n", argv[i]);
		}
		endtime = time(NULL);
		printf("%d scenes rendered in %d seconds\n", argc-1, endtime - starttime);
	}
	else
		printf("usage: lhfire script.txt\nfor information on the script commands and such, read lhfire.txt\n");
	return 0;
}
