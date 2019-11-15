
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>

#include "particle.h"

#define FALSE 0
#define TRUE 1

extern float frame_starttime, frame_endtime, frame_time, frame_currenttime;
extern int frame_start, frame_end;

extern int FBWidth, FBHeight;

extern float* FB;
extern float* izbuffer;
extern char* outputname; // setup by script.c

float script_time; // current time
float script_endtime; // executing up to this time
int script_token; // current token number
int script_init; // render and frames do nothing unless this is set
int script_commandcounter; // used to detect runaway loops

int spritetype;
int rendertype;
float camera_x, camera_y, camera_z;
float color1_r, color1_g, color1_b, color1_a;
float color2_r, color2_g, color2_b, color2_a;
float minlife, maxlife;
float minsize, maxsize;
float area_x, area_y, area_z, area_minradius, area_maxradius;
float velocity_x, velocity_y, velocity_z, velocity_minradius, velocity_maxradius;
float gravity_x, gravity_y, gravity_z;
float airfriction;
float decaystart, decayend;
float weightstart, weightend;
float pressurestart, pressureend;
float minmass, maxmass;
int motionblurpasses;
float imagebrightness_min, imagebrightness_max;
float world_minx, world_maxx, world_miny, world_maxy, world_minz, world_maxz;

unsigned char** token; // array of tokens
int tokens; // how many are in the array

unsigned char* tokendata;
int tokendatasize;

int script_counttokens()
{
	int tokencount, i, intoken;
	tokencount = 0;
	intoken = FALSE;
	for (i = 0;i < tokendatasize;i++)
	{
		if (tokendata[i] > ' ') // a non-whitespace character
		{
			if (!intoken)
			{
				tokencount++;
				intoken = TRUE;
			}
		}
		else
			intoken = FALSE;
	}
	return tokencount;
}

int script_alloctokenlist(int tokencount)
{
	if (tokencount < 1)
		return 0; // failed
	if ((token = malloc(tokencount * sizeof(unsigned char*))))
		return (tokens = tokencount);
	return 0; // failed
}

int script_maketokens()
{
	int tokencount, i, intoken;
	tokencount = 0;
	intoken = FALSE;
	for (i = 0;i < tokendatasize;i++)
	{
		if (tokendata[i] > ' ') // a non-whitespace character
		{
			if (!intoken)
			{
				token[tokencount] = &tokendata[i];
				tokencount++;
				intoken = TRUE;
			}
		}
		else
		{
			tokendata[i] = 0; // null terminate the strings
			intoken = FALSE;
		}
	}
	// null terminate it incase it did not end with a newline
	// (note: the array is 1 byte bigger than needed to allow this)
	tokendata[tokendatasize] = 0;
	return tokencount;
}

int script_load(char* filename)
{
	FILE *file;
	int length, result;
	result = FALSE;
	if (tokendata)
		free(tokendata);
	if (token)
		free(token);
	tokendatasize = 0;
	printf("loading script %s\n", filename);
	if ((file = fopen(filename, "rb")))
	{
		fseek(file, 0, SEEK_END);
		length = ftell(file);
		fseek(file, 0, SEEK_SET);
		if (length >= 1) // 1 byte wouldn't be very interesting...
		{
			if ((tokendata = malloc(length+1)))
			{
				tokendatasize = length;
				fread(tokendata, 1, length, file);
				if (script_alloctokenlist(script_counttokens()) && script_maketokens())
				{
					printf("script %s loaded, %d words\n", filename, tokens);
					result = TRUE;
				}
				else
				{
					free(tokendata);
					if (token)
						free(token);
					tokendatasize = 0;
					printf("script %s failed to load\n", filename);
				}
			}
		}
		fclose(file);
	}
	else
		printf("unable to read file %s\n", filename);
	return result;
}

float lhrandom(float min, float max);

int scwantstring(int t)
{
	if (t >= tokens)
		return FALSE;
	return TRUE; // anything is a string
}

int scwantint(int t)
{
	int i;
	char* s;
	int num;
	if (t >= tokens)
		return FALSE;
	s = token[t];
	for (i = 0;s[i];i++)
	{
		if ((s[i] < '0' || s[i] > '9') && s[i] != '-')
			return FALSE;
	}
	if (sscanf(token[t], "%d", &num) != 1)
		return FALSE;
	return TRUE;
}

int scwantfloat(int t)
{
	int i;
	char* s;
	float num;
	if (t >= tokens)
		return FALSE;
	s = token[t];
	for (i = 0;s[i];i++)
	{
		if ((s[i] < '0' || s[i] > '9') && s[i] != '-' && s[i] != '.')
			return FALSE;
	}
	if (sscanf(token[t], "%f", &num) != 1)
		return FALSE;
	return TRUE;
}

char* scgetstring(int t)
{
	if (t >= tokens)
		return 0;
	return token[t];
}

int scgetint(int t)
{
	int num;
	if (t >= tokens)
		return 0;
	if (sscanf(token[t], "%d", &num) == 1)
		return num;
	else
		printf("'%s' is not an integer\n", token[t]);
	return 0;
}

float scgetfloat(int t)
{
	float num;
	if (t >= tokens)
		return 0.0f;
	if (sscanf(token[t], "%f", &num) == 1)
		return num;
	else
		printf("'%s' is not a float (decimal number with optional fraction)\n", token[t]);
	return 0.0f;
}

void sc_spawn(int t)
{
	int i, count, world_box;
	float ax, ay, az, vx, vy, vz, x, y, z, cr, cg, cb, ca, r, r2;
	if (scwantint(t+1))
	{
		script_token = t + 2;
		count = scgetint(t+1);
		if (count < 1)
		{
			printf("spawn: number of particles must be at least 1\n");
			return;
		}
//		printf(" %d\n ", count);
		world_box = world_minx || world_maxx || world_miny || world_maxy || world_minz || world_maxz;
		for (i = 0;i < count;i++)
		{
//			printf("*\n");
			do
			{
				do { x = lhrandom(-1.0f, 1.0f);y = lhrandom(-1.0f, 1.0f);z = lhrandom(-1.0f, 1.0f);} while ((r = x*x+y*y+z*z) >= 1.0f && r >= 0.01f);
				r = 1.0f / (float) sqrt(r);x *= r;y *= r;z *= r;
				r = lhrandom(area_minradius, area_maxradius);
				ax = area_x + x * r;
				ay = area_y + y * r;
				az = area_z + z * r;
			}
			while(world_box && (ax < world_minx || ax > world_maxx || ay < world_miny || ay > world_maxy || az < world_minz || az > world_maxz));
			do { x = lhrandom(-1.0f, 1.0f);y = lhrandom(-1.0f, 1.0f);z = lhrandom(-1.0f, 1.0f);} while ((r = x*x+y*y+z*z) >= 1.0f && r >= 0.01f);
			r = 1.0f / (float) sqrt(r);x *= r;y *= r;z *= r;
			r = lhrandom(velocity_minradius, velocity_maxradius);
			vx = velocity_x + x * r;
			vy = velocity_y + y * r;
			vz = velocity_z + z * r;
			r = lhrandom(0.0f, 1.0f);
			r2 = 1.0f - r;
			cr = color1_r * r + color2_r * r2;
			cg = color1_g * r + color2_g * r2;
			cb = color1_b * r + color2_b * r2;
			ca = color1_a * r + color2_a * r2;
			particle_spawn(rendertype, script_time, lhrandom(minlife, maxlife), lhrandom(minsize, maxsize), ax, ay, az, vx, vy, vz, cr, cg, cb, ca, decaystart, decayend, weightstart, weightend, pressurestart, pressureend, lhrandom(minmass, maxmass));
//			printf("\n");
		}
	}
	else
		printf("spawn: wrong parameter type.  usage: spawn numberofparticles\n");
}

void sc_boxspawn(int t)
{
	int i, j, k, countx, county, countz;
	float ax, ay, az, vx, vy, vz, x, y, z, cr, cg, cb, ca, r, r2, minx, miny, minz, maxx, maxy, maxz, stepx, stepy, stepz;
	if (scwantint(t+1) && scwantint(t+2) && scwantint(t+3) && scwantfloat(t+4) && scwantfloat(t+5) && scwantfloat(t+6) && scwantfloat(t+7) && scwantfloat(t+8) && scwantfloat(t+9))
	{
		script_token = t + 10;
		countx = scgetint(t+1);
		county = scgetint(t+2);
		countz = scgetint(t+3);
		minx = scgetfloat(t+4);
		miny = scgetfloat(t+5);
		minz = scgetfloat(t+6);
		maxx = scgetfloat(t+7);
		maxy = scgetfloat(t+8);
		maxz = scgetfloat(t+9);
//		printf(" %d\n ", count);
		if (countx < 1)
		{
			printf("boxspawn: number of particles on x must be at least 1\n");
			return;
		}
		if (county < 1)
		{
			printf("boxspawn: number of particles on y must be at least 1\n");
			return;
		}
		if (countz < 1)
		{
			printf("boxspawn: number of particles on z must be at least 1\n");
			return;
		}
		if (world_minx || world_maxx || world_miny || world_maxy || world_minz || world_maxz)
		{
			if (minx < world_minx)
			{
				printf("boxspawn: minx < worldbox minx\n");
				return;
			}
			if (miny < world_miny)
			{
				printf("boxspawn: miny < worldbox miny\n");
				return;
			}
			if (minz < world_minz)
			{
				printf("boxspawn: minz < worldbox minz\n");
				return;
			}
			if (maxx > world_maxx)
			{
				printf("boxspawn: maxx > worldbox maxx\n");
				return;
			}
			if (maxy > world_maxy)
			{
				printf("boxspawn: maxy > worldbox maxy\n");
				return;
			}
			if (maxz > world_maxz)
			{
				printf("boxspawn: maxz > worldbox maxz\n");
				return;
			}
		}
		stepx = (maxx - minx) / (float) countx;
		stepy = (maxy - miny) / (float) county;
		stepz = (maxz - minz) / (float) countz;
		for (i = 0, ax = minx + 0.5f * stepx;i < countx;i++, ax += stepx)
		{
			for (j = 0, ay = miny + 0.5f * stepy;j < county;j++, ay += stepy)
			{
				for (k = 0, az = minz + 0.5f * stepz;k < countz;k++, az += stepz)
				{
					do { x = lhrandom(-1.0f, 1.0f);y = lhrandom(-1.0f, 1.0f);z = lhrandom(-1.0f, 1.0f);} while ((r = x*x+y*y+z*z) >= 1.0f && r >= 0.01f);
					r = 1.0f / (float) sqrt(r);x *= r;y *= r;z *= r;
					r = lhrandom(velocity_minradius, velocity_maxradius);
					vx = velocity_x + x * r;
					vy = velocity_y + y * r;
					vz = velocity_z + z * r;
					r = lhrandom(0.0f, 1.0f);
					r2 = 1.0f - r;
					cr = color1_r * r + color2_r * r2;
					cg = color1_g * r + color2_g * r2;
					cb = color1_b * r + color2_b * r2;
					ca = color1_a * r + color2_a * r2;
					particle_spawn(rendertype, script_time, lhrandom(minlife, maxlife), lhrandom(minsize, maxsize), ax, ay, az, vx, vy, vz, cr, cg, cb, ca, decaystart, decayend, weightstart, weightend, pressurestart, pressureend, lhrandom(minmass, maxmass));
				}
			}
		}
	}
	else
		printf("boxspawn: wrong parameter type.  usage: spawn particlesx particlesy particlesz minx miny minz maxx maxy maxz\n");
}

// because wait is relative rather than absolute, aborting the script during the wait
// can cause undesired behavior (waiting indefinitely infact), to get around this
// we store the time we're waiting for when script_endtime is reached
// and restore it on the next call (which would be the next execution)
float sc_waithack;
void sc_wait(int t)
{
	float time, time2;
	if (scwantfloat(t+1))
	{
		time = scgetfloat(t+1);
		time += script_time;
		if (sc_waithack) // restore the time we were waiting for
			time = sc_waithack;
		sc_waithack = 0.0f;
		time2 = time; // store a copy before limiting to script_endtime
		if (time > script_endtime)
			time = script_endtime;
		script_time = time;
		particles_advance(time);
		if (time < script_endtime) // only advance if during a pass
			script_token = t + 2;
		else
			sc_waithack = time2; // remember what time we're waiting for
//		script_commandcounter = 0;
	}
	else
		printf("wait: wrong parameter type.  usage: wait howinttowait\n");
}

void sc_time(int t)
{
	float time;
	if (scwantfloat(t+1))
	{
		time = scgetfloat(t+1);
		if (time > script_endtime)
			time = script_endtime;
		script_time = time;
		particles_advance(time);
		if (time < script_endtime) // leave the token pointing at this for next pass
			script_token = t + 2;
//		script_commandcounter = 0;
	}
	else
		printf("time: wrong parameter type.  usage: time timetowaitfor\n");
}

void sc_goto(int t)
{
	int i;
	if (scwantstring(t+1))
	{
		for (i = 0;i < tokens;i++)
		{
			if (strcmp(token[i], "label") == 0 && strcmp(token[i+1], token[t+1]) == 0)
			{
				script_token = i + 2;
				return;
			}
		}
		printf("goto: unable to find label %s.\n", token[t+1]);
	}
	else
		printf("label: wrong parameter type.  usage: label name\n");
}

void sc_label(int t)
{
	if (scwantstring(t+1))
		script_token = t + 2;
	else
		printf("label: wrong parameter type.  usage: label name\n");
}

void sc_area(int t)
{
	if (scwantfloat(t+1) && scwantfloat(t+2) && scwantfloat(t+3) && scwantfloat(t+4) && scwantfloat(t+5))
	{
		script_token = t + 6;
		area_x = scgetfloat(t+1);
		area_y = scgetfloat(t+2);
		area_z = scgetfloat(t+3);
		area_minradius = scgetfloat(t+4);
		area_maxradius = scgetfloat(t+5);
	}
	else
		printf("area: wrong parameter types.  usage: area x y z minradius maxradius\n");
}

void sc_velocity(int t)
{
	if (scwantfloat(t+1) && scwantfloat(t+2) && scwantfloat(t+3) && scwantfloat(t+4) && scwantfloat(t+5))
	{
		script_token = t + 6;
		velocity_x = scgetfloat(t+1);
		velocity_y = scgetfloat(t+2);
		velocity_z = scgetfloat(t+3);
		velocity_minradius = scgetfloat(t+4);
		velocity_maxradius = scgetfloat(t+5);
	}
	else
		printf("velocity: wrong parameter types.  usage: velocity x y z minradius maxradius\n");
}

void sc_life(int t)
{
	if (scwantfloat(t+1) && scwantfloat(t+2))
	{
		script_token = t + 3;
		minlife = scgetfloat(t+1);
		maxlife = scgetfloat(t+2);
	}
	else
		printf("life: wrong parameter types.  usage: life minimum maximum\n");
}

void sc_size(int t)
{
	if (scwantfloat(t+1) && scwantfloat(t+2))
	{
		script_token = t + 3;
		minsize = scgetfloat(t+1);
		maxsize = scgetfloat(t+2);
	}
	else
		printf("size: wrong parameter types.  usage: size minimum maximum\n");
}

void sc_color(int t)
{
	if (scwantfloat(t+1) && scwantfloat(t+2) && scwantfloat(t+3) && scwantfloat(t+4))
	{
		script_token = t + 5;
		color1_r = color2_r = scgetfloat(t+1);
		color1_g = color2_g = scgetfloat(t+2);
		color1_b = color2_b = scgetfloat(t+3);
		color1_a = color2_a = scgetfloat(t+4);
	}
	else
		printf("color: wrong parameter types.  usage: color red green blue alpha  (alpha = opacity, 0 to 256 usually)\n");
}

void sc_color1(int t)
{
	if (scwantfloat(t+1) && scwantfloat(t+2) && scwantfloat(t+3) && scwantfloat(t+4))
	{
		script_token = t + 5;
		color1_r = scgetfloat(t+1);
		color1_g = scgetfloat(t+2);
		color1_b = scgetfloat(t+3);
		color1_a = scgetfloat(t+4);
	}
	else
		printf("color1: wrong parameter types.  usage: color1 red green blue alpha  (alpha = opacity, 0 to 256 usually)\n");
}

void sc_color2(int t)
{
	if (scwantfloat(t+1) && scwantfloat(t+2) && scwantfloat(t+3) && scwantfloat(t+4))
	{
		script_token = t + 5;
		color2_r = scgetfloat(t+1);
		color2_g = scgetfloat(t+2);
		color2_b = scgetfloat(t+3);
		color2_a = scgetfloat(t+4);
	}
	else
		printf("color2: wrong parameter types.  usage: color2 red green blue alpha  (alpha = opacity, 0 to 256 usually)\n");
}

void sc_camera(int t)
{
	if (scwantfloat(t+1) && scwantfloat(t+2) && scwantfloat(t+3))
	{
		script_token = t + 4;
		camera_x = scgetfloat(t+1);
		camera_y = scgetfloat(t+2);
		camera_z = scgetfloat(t+3);
	}
	else
		printf("camera: wrong parameter types.  usage: camera x y z\n");
}

extern int framebuffer_alloc(int width, int height, char* filename);

void sc_render(int t)
{
	if (scwantint(t+1) && scwantint(t+2) && scwantstring(t+3))
	{
		script_token = t + 4;
		if (!script_init)
			return;
		framebuffer_alloc(scgetint(t+1), scgetint(t+2), token[t+3]);
	}
	else
		printf("render: wrong parameter types.  usage: render width height outputfilename\n");
}

void sc_frames(int t)
{
	if (scwantfloat(t+1) && scwantfloat(t+2) && scwantint(t+3) && scwantint(t+4))
	{
		script_token = t + 5;
		if (!script_init)
			return;
		frame_starttime = scgetfloat(t+1);
		frame_endtime = scgetfloat(t+2);
		frame_start = scgetint(t+3);
		frame_end = scgetint(t+4);
		if (frame_start < frame_end)
			frame_time = (frame_endtime - frame_starttime) / (frame_end - frame_start);
		else
			frame_time = frame_endtime - frame_starttime;
	}
	else
		printf("frames: wrong parameter types.  usage: frames starttime endtime startframe endframe\n");
}

void sc_particles(int t)
{
	if (scwantint(t+1))
	{
		script_token = t + 2;
		if (!script_init)
			return;
		particles_alloc(scgetint(t+1));
	}
	else
		printf("particles: wrong parameter type.  usage: particles numberofparticles\n");
}

void sc_seed(int t)
{
	if (scwantint(t+1))
	{
		script_token = t + 2;
		srand(scgetint(t+1));
	}
	else
		printf("particles: wrong parameter type.  usage: particles numberofparticles\n");
}

void sc_passes(int t)
{
	if (scwantint(t+1))
	{
		script_token = t + 2;
		if (!script_init)
			return;
		motionblurpasses = scgetint(t+1);
		if (motionblurpasses < 1)
			motionblurpasses = 1;
	}
	else
		printf("passes: wrong parameter type.  usage: passes numberofmotionblurpasses\n");
}

void sc_clear(int t)
{
	script_token = t + 1;
	particles_clear();
}

void sc_decay(int t)
{
	if (scwantfloat(t+1) && scwantfloat(t+2))
	{
		script_token = t + 3;
		decaystart = scgetfloat(t+1);
		decayend = scgetfloat(t+2);
	}
	else
		printf("decay: wrong parameter types.  usage: decay start end\n");
}

void sc_weight(int t)
{
	if (scwantfloat(t+1) && scwantfloat(t+2))
	{
		script_token = t + 3;
		weightstart = scgetfloat(t+1);
		weightend = scgetfloat(t+2);
	}
	else
		printf("weight: wrong parameter types.  usage: weight start end\n");
}

void sc_pressure(int t)
{
	if (scwantfloat(t+1) && scwantfloat(t+2))
	{
		script_token = t + 3;
		pressurestart = scgetfloat(t+1);
		pressureend = scgetfloat(t+2);
	}
	else
		printf("pressure: wrong parameter types.  usage: pressure start end\n");
}

void sc_mass(int t)
{
	if (scwantfloat(t+1) && scwantfloat(t+2))
	{
		script_token = t + 3;
		minmass = scgetfloat(t+1);
		maxmass = scgetfloat(t+2);
	}
	else
		printf("mass: wrong parameter types.  usage: mass minimum maximum\n");
}

void sc_gravity(int t)
{
	if (scwantfloat(t+1) && scwantfloat(t+2) && scwantfloat(t+3))
	{
		script_token = t + 4;
		gravity_x = scgetfloat(t+1);
		gravity_y = scgetfloat(t+2);
		gravity_z = scgetfloat(t+3);
	}
	else
		printf("gravity: wrong parameter types.  usage: gravity x y z\n");
}

void sc_airfriction(int t)
{
	if (scwantfloat(t+1))
	{
		script_token = t + 2;
		airfriction = scgetfloat(t+1);
	}
	else
		printf("airfriction: wrong parameter types.  usage: airfriction value\n");
}

void sc_rendertype(int t)
{
	int i;
	if (scwantint(t+1))
	{
		script_token = t + 2;
		i = scgetint(t+1);
		if (i >= 0 && i < 3)
			rendertype = i;
		else
			printf("rendertype: invalid rendertype %i, should be 0 (circle), 1 (globe), or 2 (glow)\n", i);
	}
	else
		printf("rendertype: wrong parameter type.  usage: rendertype particletype\n");
}

void sc_imagebrightness(int t)
{
	if (scwantfloat(t+1) && scwantfloat(t+2))
	{
		script_token = t + 3;
		imagebrightness_min = scgetfloat(t+1);
		imagebrightness_max = scgetfloat(t+2);
	}
	else
		printf("imagebrightness: wrong parameter type.  usage: imagebrightness min max\n");
}

void sc_worldbox(int t)
{
	if (scwantfloat(t+1) && scwantfloat(t+2) && scwantfloat(t+3) && scwantfloat(t+4) && scwantfloat(t+5) && scwantfloat(t+6))
	{
		script_token = t + 7;
		world_minx = scgetfloat(t+1);
		world_miny = scgetfloat(t+2);
		world_minz = scgetfloat(t+3);
		world_maxx = scgetfloat(t+4);
		world_maxy = scgetfloat(t+5);
		world_maxz = scgetfloat(t+6);
	}
	else
		printf("worldbox: wrong parameter types.  usage: worldbox minx miny minz maxx maxy maxz\n");
}

void sc_spritetype(int t)
{
	if (scwantstring(t+1))
	{
		script_token = t + 2;
		if (!strcmp(token[t+1], "vp_parallel_upright"))
			spritetype = 0;
		else if (!strcmp(token[t+1], "facing_upright"))
			spritetype = 1;
		else if (!strcmp(token[t+1], "vp_parallel"))
			spritetype = 2;
		else if (!strcmp(token[t+1], "oriented"))
			spritetype = 3;
		else if (!strcmp(token[t+1], "vp_parallel_oriented"))
			spritetype = 4;
		else
		{
			printf("spritetype: unknown sprite type \"%s\" (valid sprite types: vp_parallel_upright facing_upright vp_parallel oriented vp_parallel_oriented)\n", token[t+1]);
			spritetype = 2;
		}
	}
	else
		printf("spritetype: wrong parameter types.  usage: spritetype value (valid sprite types: vp_parallel_upright facing_upright vp_parallel oriented vp_parallel_oriented)\n");
}

void script_execute(int t)
{
//	printf("%s\n", token[t]);
	     if (!strcmp(token[t], "wait")) sc_wait(t);
	else if (!strcmp(token[t], "spawn")) sc_spawn(t);
	else if (!strcmp(token[t], "time")) sc_time(t);
	else if (!strcmp(token[t], "goto")) sc_goto(t);
	else if (!strcmp(token[t], "boxspawn")) sc_boxspawn(t);
	else if (!strcmp(token[t], "area")) sc_area(t);
	else if (!strcmp(token[t], "velocity")) sc_velocity(t);
	else if (!strcmp(token[t], "life")) sc_life(t);
	else if (!strcmp(token[t], "size")) sc_size(t);
	else if (!strcmp(token[t], "color")) sc_color(t);
	else if (!strcmp(token[t], "color1")) sc_color1(t);
	else if (!strcmp(token[t], "color2")) sc_color2(t);
	else if (!strcmp(token[t], "label")) sc_label(t);
	else if (!strcmp(token[t], "seed")) sc_seed(t);
	else if (!strcmp(token[t], "camera")) sc_camera(t);
	else if (!strcmp(token[t], "clear")) sc_clear(t);
	else if (!strcmp(token[t], "render")) sc_render(t);
	else if (!strcmp(token[t], "frames")) sc_frames(t);
	else if (!strcmp(token[t], "particles")) sc_particles(t);
	else if (!strcmp(token[t], "passes")) sc_passes(t);
	else if (!strcmp(token[t], "decay")) sc_decay(t);
	else if (!strcmp(token[t], "weight")) sc_weight(t);
	else if (!strcmp(token[t], "pressure")) sc_pressure(t);
	else if (!strcmp(token[t], "mass")) sc_mass(t);
	else if (!strcmp(token[t], "gravity")) sc_gravity(t);
	else if (!strcmp(token[t], "airfriction")) sc_airfriction(t);
	else if (!strcmp(token[t], "rendertype")) sc_rendertype(t);
	else if (!strcmp(token[t], "imagebrightness")) sc_imagebrightness(t);
	else if (!strcmp(token[t], "worldbox")) sc_worldbox(t);
	else if (!strcmp(token[t], "spritetype")) sc_spritetype(t);
	else
	{
		script_time = script_endtime;
		printf("unknown command '%s', aborting script at time %f\n", token[t], script_time);
	}
}

int script_findandexecutecommand(unsigned char* commandname)
{
	int i;
	for (i = 0;i < tokens;i++)
	{
		if (!strcmp(token[i], commandname)) // found it
		{
			script_token = i;
			script_execute(i);
			return TRUE;
		}
	}
	return FALSE;
}

// this merely finds the render and frames commands and interprets them
int script_setup()
{
	spritetype = 2;
	rendertype = 0;
	camera_x = 0.0f;camera_y = 0.0f;camera_z = -128.0f;
	color1_r = color2_r = 256.0f;color1_g = color2_g = 256.0f;color1_b = color2_b = 256.0f;color1_a = color2_a = 256.0f;
	minlife = 0.0f;maxlife = 1.0f;
	minsize = 0.0f;maxsize = 1.0f;
	area_x = 0.0f;area_y = 0.0f;area_z = 0.0f;area_minradius = 0.0f;area_maxradius = 16.0f;
	velocity_x = 0.0f;velocity_y = 0.0f;velocity_z = 0.0f;velocity_minradius = 0.0f;velocity_maxradius = 32.0f;
	gravity_x = gravity_y = gravity_z = 0.0f;
	airfriction = 0.0f;
	decaystart = decayend = 1.0f;
	weightstart = weightend = pressurestart = pressureend = 0.0f;
	minmass = maxmass = 1.0f;
	motionblurpasses = 1;
	imagebrightness_min = 0.0f;
	imagebrightness_max = 1.0f;
	world_minx = 0.0f;world_miny = 0.0f;world_minz = 0.0f;world_maxx = 0.0f;world_maxy = 0.0f;world_maxz = 0.0f;

	script_init = TRUE;
	script_time = 0.0f;
	script_endtime = 0.0f;
	script_token = 0;
	script_commandcounter = 0; // used to detect infinite loops
	particles_clear();
	frame_start = -1;
	if (script_findandexecutecommand("render") && script_findandexecutecommand("frames") && script_findandexecutecommand("particles"))
	{
		if (FB && frame_start >= 0) // make sure the commands succeeded
		{
			script_findandexecutecommand("passes"); // not required
			script_init = FALSE;
			return TRUE;
		}
		else
		{
			script_init = FALSE;
			return FALSE;
		}
	}
	script_init = FALSE;
	return FALSE;
}

void script_reset()
{
	script_init = FALSE;
	script_time = 0.0f;
	script_endtime = 0.0f;
	script_token = 0;
	script_commandcounter = 0; // used to detect infinite loops
	particles_clear();
}

void script_executeuntiltime(float time)
{
	int t;
//	printf("executing until time %.0f\n", time);
	script_endtime = time;
	while (script_time < script_endtime && script_token < tokens)
	{
//		printf("+\n");
		t = script_token;
		script_execute(script_token);
		if (script_token == t && script_time < script_endtime)
		{
			printf("script_execute: aborting due to error\n");
			break;
		}
		if (script_commandcounter >= 50000)
		{
			printf("script_execute: command counter hit 50000, aborting; probably a runaway loop.  time = %f\n", script_time);
			//printf("script_execute: command counter hit 2000 between waits; probably a runaway loop, if not just use more waits.  time = %d\n", script_time);
			break;
		}
	}
//	printf("script done\n");
}
