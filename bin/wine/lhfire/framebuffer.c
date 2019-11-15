
#include <stdlib.h>
#include <memory.h>
#include <stdio.h>
#include <math.h>
#include <string.h>

#define FALSE 0
#define TRUE 1

int FBWidth, FBHeight;

float *FB, *aFB; // aFB = accumulation frame buffer
//float *izbuffer;
char *outputname; // setup by script.c

extern float imagebrightness_min, imagebrightness_max;
extern int spritetype;

void framebuffer_free()
{
	if (FB)
		free(FB);
	if (aFB)
		free(aFB);
//	if (izbuffer)
//		free(izbuffer);
}

int framebuffer_alloc(int width, int height, char* filename)
{
	if (width < 1 || height < 1)
		return FALSE;
	framebuffer_free();
	FBWidth = width;
	FBHeight = height;
	outputname = filename;
	if ((FB = malloc(FBWidth * FBHeight * 4 * sizeof(float))))
		if ((aFB = malloc(FBWidth * FBHeight * 4 * sizeof(float))))
//		if (izbuffer = malloc(FBWidth * FBHeight * sizeof(float)))
			return TRUE;
	return FALSE;
}

void clearFB()
{
	memset(FB, 0, FBWidth*FBHeight*4*sizeof(float));
}

void clearaFB()
{
	memset(aFB, 0, FBWidth*FBHeight*4*sizeof(float));
}

//void clearizbuffer()
//{
//	memset(izbuffer, 0, FBWidth*FBHeight*sizeof(float));
//}

void motionblurfinishFB(int passes)
{
	float s;
	int i, j;
	s = 1.0f / passes;
	j = FBWidth*FBHeight*4;
	for (i = 0;i < j;i++)
		FB[i] = aFB[i] * s;
}

void accumulateFB()
{
	int i, j;
	j = FBWidth*FBHeight*4;
	for (i = 0;i < j;i++)
		aFB[i] += FB[i]; // add it up
}

void fput_littleshort(int num, FILE* file)
{
	fputc(num & 0xFF, file);
	fputc((num >> 8) & 0xFF, file);
}

void fput_littleint(int num, FILE* file)
{
	fputc(num & 0xFF, file);
	fputc((num >> 8) & 0xFF, file);
	fputc((num >> 16) & 0xFF, file);
	fputc((num >> 24) & 0xFF, file);
}

void fput_littlefloat(float num, FILE* file)
{
	/*
	// although this is guarenteed to write out IEEE compliant floats,
	// it is slow and silly unless the machine uses a non-IEEE compliant float...
	int exponent;
	double mantissa;
	int mantissabits;
	int data, *test;
	mantissa = frexp(num, &exponent);
	mantissabits = (int) (mantissa * 16777216.0);
	mantissabits &= 0x007FFFFF;
	if (exponent < -127) exponent = -127;
	if (exponent > 127) exponent = 127;
	data = ((exponent + 126) << 23) | mantissabits; // 126 seems a bit odd to me, but worked...
	if (num < 0.0f)
		data |= 0x80000000;
//	test = (void*) &num; // just for testing the results if needed
//	if (data != *test)
//		data = *test;
	*/
	int *data;
	data = (void*) &num; // note: this is *NOT* byte order dependent
	fput_littleint(*data, file);
}

char outputnamebuffer[1024];

char* frame_getoutputname(int frame)
{
	sprintf(outputnamebuffer, outputname, frame);
	return outputnamebuffer;
}

char* getfilenamesuffix(char* filename)
{
	int i, j;
	j = -1;
	for (i = 0;filename[i];i++)
	{
		if (filename[i] == '.')
			j = i + 1;
	}
	if (j < 0) j = i;
	return &filename[j];
}

void writetarga32frame(int frame, char* filename)
{
	int x, y, c, i;
	FILE* file;
	float min, range, f;
	unsigned char *buf;
	min = imagebrightness_min * 256.0f;
	range = imagebrightness_max - imagebrightness_min;
	if ((file = fopen(filename, "wb")))
	{
		fputc(0, file); //id_length - no comment in this file
		fputc(0, file); //colormap_type -  no colormap
		fputc(2, file); //image_type - type 2 (uncompressed)
		fput_littleshort(0, file); // colormap_index
		fput_littleshort(0, file); // colormap_length
		fputc(0, file); //colormap_size
		fput_littleshort(0, file); //x_origin
		fput_littleshort(0, file); //y_origin
		fput_littleshort(FBWidth, file); //width
		fput_littleshort(FBHeight, file); //height
		fputc(32, file); //pixel_size - 32bit, 4 bytes per pixel
		fputc(8, file); //attributes
		buf = malloc(FBWidth*4);
		for (y = FBHeight - 1;y >= 0;y--) // targa files are upside down
		{
			i = y * FBWidth * 4;
			for (x = 0;x < FBWidth;x++)
			{
				f = FB[i+2];f = f*range+min;c = (int) f;if (c <= 0) *buf++ = 0;else if (c >= 255) *buf++ = 255;else *buf++ = c;
				f = FB[i+1];f = f*range+min;c = (int) f;if (c <= 0) *buf++ = 0;else if (c >= 255) *buf++ = 255;else *buf++ = c;
				f = FB[i  ];f = f*range+min;c = (int) f;if (c <= 0) *buf++ = 0;else if (c >= 255) *buf++ = 255;else *buf++ = c;
				f = FB[i+3];f = f*range+min;c = (int) f;if (c <= 0) *buf++ = 0;else if (c >= 255) *buf++ = 255;else *buf++ = c;
				i+=4; // advance a pixel
			}
			buf -= FBWidth * 4;
			fwrite(buf, 4, FBWidth, file);
		}
		free(buf);
		fclose(file);
	}
}

void writetarga24frame(int frame, char* filename)
{
	int x, y, c, i;
	FILE* file;
	float min, range, f;
	unsigned char *buf;
	min = imagebrightness_min * 256.0f;
	range = imagebrightness_max - imagebrightness_min;
	if ((file = fopen(filename, "wb")))
	{
		fputc(0, file); //id_length - no comment in this file
		fputc(0, file); //colormap_type -  no colormap
		fputc(2, file); //image_type - type 2 (uncompressed)
		fput_littleshort(0, file); // colormap_index
		fput_littleshort(0, file); // colormap_length
		fputc(0, file); //colormap_size
		fput_littleshort(0, file); //x_origin
		fput_littleshort(0, file); //y_origin
		fput_littleshort(FBWidth, file); //width
		fput_littleshort(FBHeight, file); //height
		fputc(24, file); //pixel_size - 24bit, 3 bytes per pixel
		fputc(8, file); //attributes
		buf = malloc(FBWidth*3);
		for (y = FBHeight - 1;y >= 0;y--) // targa files are upside down
		{
			i = y * FBWidth * 4;
			for (x = 0;x < FBWidth;x++)
			{
				f = FB[i+2];f = f*range+min;c = (int) f;if (c <= 0) *buf++ = 0;else if (c >= 255) *buf++ = 255;else *buf++ = c;
				f = FB[i+1];f = f*range+min;c = (int) f;if (c <= 0) *buf++ = 0;else if (c >= 255) *buf++ = 255;else *buf++ = c;
				f = FB[i  ];f = f*range+min;c = (int) f;if (c <= 0) *buf++ = 0;else if (c >= 255) *buf++ = 255;else *buf++ = c;
				i += 4;
			}
			buf -= FBWidth * 3;
			fwrite(buf, 3, FBWidth, file);
		}
		free(buf);
		fclose(file);
	}
}

int spriteinitialized;

// frame types
#define SPR_SINGLE					0
#define SPR_GROUP					1

unsigned char* quakepalette;

unsigned char findcolor_black, findcolor_white;

// generic little palette searcher written by Forest "LordHavoc" Hale
// searchs for the nearest color in the palette, not optimized for perfect matchs.
// red, green, and blue can be far outside of the 0-255 range of the palette.
int directfindcolor(unsigned char* p, int start, int end, int red, int green, int blue)
{
	int i, best;
	int dist, bestdist, rd, gd, bd;
	p += start*3;
	best = start;bestdist = 2000000000;
	for (i = start;i < end;i++)
	{
		rd = *p++ - red;
		gd = *p++ - green;
		bd = *p++ - blue;
		// tuned roughly for human vision, humans notice green then red then blue
		dist = rd*rd*2 + gd*gd*4 + bd*bd;
		if (dist < bestdist)
		{
			best = i;
			bestdist = dist;
		}
	}
	return best;
}

int findcolor(unsigned char* p, int start, int end, int red, int green, int blue)
{
	if (red <= 0 && green <= 0 && blue <= 0)
		return findcolor_black;
	else if (red >= 255 && green >= 255 && blue >= 255)
		return findcolor_white;
	else
		return directfindcolor(p, start, end, red, green, blue);
}

extern int frame_start, frame_end;

void writespriteframe(int frame, char* filename, int sprite32)
{
	int i;
	FILE* file;
	float f, min, range;
	unsigned char *buf;
	min = imagebrightness_min * 256.0f;
	range = imagebrightness_max - imagebrightness_min;
	if (!spriteinitialized)
	{
		if (!sprite32)
		{
			if (!quakepalette && !(quakepalette = malloc(768)))
			{
				printf("unable to allocate 768 bytes of memory to store quake palette\n");
				return;
			}
			if ((file = fopen("palette.lmp", "rb")))
			{
				i = fread(quakepalette, 1, 768, file);
				fclose(file);
				if (i < 768)
				{
					printf("unable to read 768 bytes from palette.lmp, incomplete or wrong file?\n");
					return;
				}
				findcolor_black = directfindcolor(quakepalette, 0, 255,   0,   0,   0);
				findcolor_white = directfindcolor(quakepalette, 0, 255, 256, 256, 256);
			}
			else
			{
				printf("unable to open quake palette file palette.lmp, missing perhaps?\n");
				return;
			}
		}
		if ((file = fopen(filename, "wb")))
		{
			fputc('I', file);fputc('D', file);fputc('S', file);fputc('P', file); // ident
			if (sprite32)
				fput_littleint(32, file); // 32bit color
			else
				fput_littleint(1, file); // version
			fput_littleint(spritetype, file); // type
			fput_littlefloat((float) sqrt((FBWidth*0.5)*(FBWidth*0.5)+(FBHeight*0.5)*(FBHeight*0.5)), file); // boundingradius
			fput_littleint(FBWidth, file); // width
			fput_littleint(FBHeight, file); // height
			fput_littleint(frame_end - frame_start, file); // numframes
			fput_littlefloat(0.0f, file); // beamlength  (pushs the sprite away, strange legacy from DOOM?)
			fput_littleint(0, file); // synctype (synchronized, 1 would be random sync)
			fclose(file);
		}
		else
		{
			printf("unable to write to file %s\n", filename);
			return;
		}
		spriteinitialized = TRUE;
	}
	if (spriteinitialized) // write the frame
	{
		if ((file = fopen(filename, "ab"))) // append mode
		{
			fput_littleint(SPR_SINGLE, file); // type
			fput_littleint(FBWidth / -2, file); // origin[0]
			fput_littleint(FBHeight / 2, file); // origin[1]
			fput_littleint(FBWidth, file); // width
			fput_littleint(FBHeight, file); // height
			if (sprite32) // 32bit RGBA8 raw, ready for OpenGL
			{
				buf = malloc(FBWidth*FBHeight*4);
				for (i = 0;i < FBWidth*FBHeight*4;i++)
				{
					f = (float) FB[i]*range+min;
					if (f <= 0)
						*buf++ = 0;
					else if (f >= 255)
						*buf++ = 255;
					else
						*buf++ = (unsigned char) f;
				}
				buf -= FBWidth*FBHeight*4;
				fwrite(buf, 4, FBWidth*FBHeight, file);
				free(buf);
			}
			else
			{
				buf = malloc(FBWidth*FBHeight);
				for (i = 0;i < FBWidth*FBHeight*4;i+=4)
				{
					if (((float) FB[i+3]*range+min) < 128) // too transparent
						*buf++ = 255;
					else // do a palette search for the best match, and avoid 255 as that's special
						*buf++ = findcolor(quakepalette, 0, 255, (int) (FB[i]*range+min), (int) (FB[i+1]*range+min), (int) (FB[i+2]*range+min));
				}
				buf -= FBWidth*FBHeight;
				fwrite(buf, 1, FBWidth*FBHeight, file);
				free(buf);
			}
			fclose(file);
		}
	}
}

void writeframe(int frame)
{
	if (strcmp(getfilenamesuffix(outputname), "spr32") == 0)
	{
		writespriteframe(frame, outputname, TRUE);
		return;
	}
	if (strcmp(getfilenamesuffix(outputname), "spr") == 0)
	{
		writespriteframe(frame, outputname, FALSE);
		return;
	}
	if (strcmp(getfilenamesuffix(outputname), "tga") == 0)
	{
		writetarga32frame(frame, frame_getoutputname(frame));
//		writetarga24frame(frame, frame_getoutputname(frame));
		return;
	}
	if (strlen(getfilenamesuffix(outputname)) < 1)
		printf("writeframe: no file type specified in filename (render command), please use .tga (Targa) or .spr (Quake Sprite)\n");
	else
		printf("writeframe: unsupported format '%s', supported formats are Targa (.tga) and Quake Sprite (.spr)\n", getfilenamesuffix(outputname));
}
