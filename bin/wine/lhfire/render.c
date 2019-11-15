
#include <math.h>
#include <stdio.h>
#include "particle.h"

#define FALSE 0
#define TRUE 1

extern int FBWidth, FBHeight;
extern float* FB;
//extern float* izbuffer;

int drawflarepixelstested, drawflarepixels;

/*
#define quickdistsize 65536
float quickdisttable[quickdistsize];
float quickdistscale;
void quickdistinit(int increaserange)
{
	int i;
	double scaler;
	if (increaserange)
		quickdistscale *= 0.5f;
	else
		quickdistscale = 64.0f; // first time
	scaler = 1.0 / quickdistscale;
	for (i = 0;i < quickdistsize;i++)
		quickdisttable[i] = (float) ((double) 1.0 / (sqrt(i * scaler) + (1.0 / 256.0)));
}

__inline float quickrecipdist(float n)
{
	int i;
	while ((i = (int) ((float) (n * quickdistscale))) >= quickdistsize)
		quickdistinit(1); // increase range
	return quickdisttable[i];
}
*/

/*
#define quicksqrtsize 2048
float quicksqrttable[quicksqrtsize];
float quicksqrtscale;
*/
void quicksqrtinit(int increaserange)
{
	/*
	int i;
	double scaler;
	if (increaserange)
	{
		quicksqrtscale *= 0.5f;
		printf("expanding square root table\n");
	}
	else
	{
		printf("initializing square root table\n");
		quicksqrtscale = 64.0f; // first time
	}
	scaler = 1.0 / quicksqrtscale;
	for (i = 0;i < quicksqrtsize;i++)
		quicksqrttable[i] = (float) sqrt(i * scaler);
	*/
}

/*
__inline float quicksqrt(float n)
{
	int i;
	while ((i = (int) ((float) (n * quicksqrtscale))) >= quicksqrtsize)
		quicksqrtinit(1); // increase range
	return quicksqrttable[i];
}
*/

/*
#define quickrecipsize 2048
float quickreciptable[quickrecipsize];
float quickrecipscale;
*/
void quickrecipinit(int increaserange)
{
	/*
	int i;
	float scaler;
	if (increaserange)
	{
		printf("expanding recipricol table\n");
		quickrecipscale *= 0.5f;
	}
	else
	{
		printf("initializing recipricol table\n");
		quickrecipscale = 64.0f; // first time
	}
	scaler = 1.0f / quickrecipscale;
	for (i = 0;i < quickrecipsize;i++)
		quickreciptable[i] = 1.0f / (i * scaler);
	*/
}

/*
__inline float quickrecip(float n)
{
	int i;
	while ((i = (int) ((float) (n * quickrecipscale))) >= quickrecipsize)
		quickrecipinit(1); // increase range
	return quickreciptable[i];
}
*/

// renders a particle
void drawflare(float px, float py, float pz, int rendertype, float size, float red, float green, float blue, float alpha)
{
	int x, y, ix, iy; //minx, miny, maxx, maxy, sx, sy;
	float a, a2, c, c2, e, e2, cx, cy, d1, d2, f2; //, maxcolor;
	int add, ya, yaa;
	float iFBWidth, iFBHeight;
	if (size < 0.0001f)
		return;
	alpha *= (1.0f / 256.0f);
	cx = ((px / pz) + 0.5f) * FBWidth;
	cy = ((py / pz) + 0.5f) * FBHeight;
	yaa = FBWidth * 4;
	iFBWidth = 1.0f / FBWidth;
	iFBHeight = 1.0f / FBHeight;
	f2 = pz * pz;

// tolerance for minimum brightness that will still be rendered
#define dfmin (1.0f / 65536.0f)
// see below for dopixel defines for each render type
// per pixel loop
#define xloop c=(x-cx)*iFBWidth;dopixel if(a>=dfmin){drawflarepixels++;if(a>=1.0f){FB[add]=red;FB[add+1]=green;FB[add+2]=blue;FB[add+3]+=256.0f;}else{a2=1.0f-a;FB[add]=FB[add]*a2+red*a;FB[add+1]=FB[add+1]*a2+green*a;FB[add+2]=FB[add+2]*a2+blue*a;FB[add+3]+=256.0f*a;}}else break;
// per scanline loop (uses xloop twice, for left and right half)
#define yloop c=c2;e=(y-cy)*iFBHeight;e2 = e*e*1024.0f+f2;dopixel if(a>=dfmin){for(x=ix,add=ya;x>=0;x--,add-=4){xloop}for(x=ix+1,add=ya+4;x<FBWidth;x++,add+=4){xloop}}else break;
// uses yloop twice, for upper and lower half
#define renderloop for(y=iy,ya=y*yaa+ix*4;y>=0;y--,ya-=yaa){yloop}for(y=iy+1,ya=y*yaa+ix*4;y<FBHeight;y++,ya+=yaa){yloop}

	// center pixel, only used for loops
	ix = (int) cx;if (ix < 0) ix = 0;if (ix > (FBWidth-1)) ix = FBWidth-1;
	iy = (int) cy;if (iy < 0) iy = 0;if (iy > (FBHeight-1)) iy = FBHeight-1;

	// find the nearest pixel column and measure distance from it, to be 100% accurate when testing scanlines
	x = (int) (cx + 0.5f);if (x < 0) x = 0;if ((x > FBWidth-1)) x = FBWidth-1;c2 = (x - cx) * iFBWidth;

	switch (rendertype)
	{
	case prender_circle:
		d1 = size / pz;
		d1 *= d1;
#define dopixel drawflarepixelstested++;a = (c*c+e*e) < d1 ? alpha : 0.0f;
		renderloop
#undef dopixel
		break;
	case prender_globe:
		d1 = size / pz;d2 = 1.0f / d1;
#define dopixel drawflarepixelstested++;a = (d1 - (float) sqrt(c*c+e*e)) * d2 * alpha;
		renderloop
#undef dopixel
		break;
	case prender_glow:
		d1 = size * (0.125f / 1024.0f) * alpha / pz;
#define dopixel drawflarepixelstested++;a = d1 / (c*c+e*e);
		renderloop
#undef dopixel
		break;
	}
}

/*
// renders a dirt particle (blocks all light behind it using izbuffer)
void drawdirt(float px, float py, float pz)
{
	int x, y, minx, miny, maxx, maxy;
	float d, cx, cy, sx, sy;
	cy = ((py / pz) + 0.5f) * FBHeight;
	cx = ((px / pz) + 0.5f) * FBWidth;
	sx = ((1.0f/4.0f) / pz) * FBWidth;
	sy = ((1.0f/4.0f) / pz) * FBHeight;
	minx = (int) ((float) cx - sx);
	maxx = (int) ((float) cx + sx);
	miny = (int) ((float) cy - sy);
	maxy = (int) ((float) cy + sy);
	if (minx < 0) minx = 0;
	if (maxx > FBWidth-1) maxx = FBWidth-1;
	if (miny < 0) miny = 0;
	if (maxy > FBHeight-1) maxy = FBHeight-1;
	if (minx >= maxx || miny >= maxy) return;
	d = 1.0f/pz; // recipricol distance (used by good 3D engines because it's fast for texturing)
	for (y = miny;y < maxy;y++)
		for (x = minx;x < maxx;x++)
			if (izbuffer[y * FBWidth + x] < d) // old z is farther away
				izbuffer[y * FBWidth + x] = d;
}
*/
