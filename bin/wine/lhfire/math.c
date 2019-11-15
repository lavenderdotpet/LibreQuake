#include <stdlib.h>

float lhrandom(float min, float max)
{
	return ((float) ((int) (rand()&32767))/32768.0f)*(max-min)+min;
}

// sets the random number seed, useful for looping particle animations
void setseed(int randomseed)
{
	srand(randomseed);
}
