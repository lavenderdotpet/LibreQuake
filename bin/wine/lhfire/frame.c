
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "particle.h"

float frame_starttime, frame_endtime, frame_time, frame_currenttime;
int frame_start, frame_end;

int drawflarecount;

extern float camera_x, camera_y, camera_z;

extern void drawflare(float px, float py, float pz, int rendertype, float size, float red, float green, float blue, float alpha);
//extern void drawdirt(float px, float py, float pz);

__inline int LH_GetTime()
{
	return (time(NULL));
};

int particle_distancesort(const void *ve1, const void *ve2)
{
	const particle_t *e1 = ve1, *e2 = ve2;
	if (e1->active)
	{
		if (e2->active) // both active
		{
			if (e1->z > e2->z)
				return -1; // e1 less than e2
			else if (e1->z < e2->z)
				return 1; // e1 greater than e2
			else
				return 0; // e1 equal to e2
		}
		else
			return 1; // e1 greater than e2
	}
	else
	{
		if (e2->active)
			return -1; // e1 less than e2
		else
			return 0; // e1 equal to e2
	}
	return 0;
}

void frame_renderparticles()
{
	int i; //, notdone; //, p;
	float decay;
	//particle_t p;
	/*
	particle_t* particlelist;
	if (!(particlelist = malloc(particles * sizeof(particle_t*))))
		return;
	memset(particlelist, 0, particles * sizeof(particle_t*));
	for (i = 0;i < particles;i++)
	{
		if (particle[i].active)
		{
			for (j = 0;j < p;j++)
			{
				if (particle[i].z < *particlelist[j].z)
				{
					for (k = j+1;k < particles;k++)
					{
						particlelist[k] = particlelist[k-1];
						if (!particlelist[k])
							break; // done sliding them
					}
					particlelist[j] = &particle[i];
				}
			}
		}
	}
	*/
	// first sort the particles
//	printf("sorting particles for rendering\n");
	qsort(&particle[0], (size_t) particles, sizeof(particle_t), particle_distancesort);
	/*
	do
	{
		notdone = 0;
		for (i = 0;i < (particles-1);i++)
		{
			if (particle[i].z > particle[i+1].z)
			{
				notdone = 1;
				memcpy(&p, &particle[i], sizeof(particle_t));
				memcpy(&particle[i], &particle[i+1], sizeof(particle_t));
				memcpy(&particle[i+1], &p, sizeof(particle_t));
			}
		}
	}
	while(notdone);
	*/
//	printf("rendering particles\n");
	for (i = 0;i < particles;i++)
	{
		if (particle[i].active && particle[i].size >= 0.01f && particle[i].color_alpha >= 0.005f)
		{
			drawflarecount++;
			decay = (particle[i].decayend - particle[i].decaystart) * particle[i].lifeprogress + particle[i].decaystart;
			if (decay >= 0.01f)
				drawflare(particle[i].x - camera_x, particle[i].y - camera_y, particle[i].z - camera_z, particle[i].rendertype, particle[i].size, particle[i].color_red, particle[i].color_green, particle[i].color_blue, particle[i].color_alpha * decay);
		}
	}
	//free(particlelist);
}

extern void script_executeuntiltime(float time);
extern void framebuffer_clear();
extern char* frame_getoutputname(int frame);
extern void writeframe(int frame);
extern int motionblurpasses;
extern void motionblurfinishFB(int passes);
extern void accumulateFB();
extern void clearFB();
extern void clearaFB();
//extern void clearizbuffer();

//extern int quickdistcalls;
//extern int quickdisthits;
//extern int quickdistmisses;
//extern int quickdistcalculated;

void frame_render(int framenumber)
{
	float f, fstep;
	int pass;
//	printf("frame %d\n", framenumber);
	fstep = 1.0f / motionblurpasses;
	// step half into the frame, to be stepping on 'time centers',
	// just like pixels should be stepped on 'pixel centers'
	f = (float) (framenumber - frame_start) + (fstep * 0.5f);
	clearaFB();
//	clearizbuffer();
	for (pass = 0;pass < motionblurpasses;pass++)
	{
		clearFB();
//		clearizbuffer();
		frame_currenttime = f * frame_time + frame_starttime;
		printf("frame %d motion blur pass %2d of %2d\n", framenumber, pass + 1, motionblurpasses);
//		printf("motion blur pass %d of %d, frame number %f at time %f\n", pass + 1, motionblurpasses, f + frame_start, frame_currenttime);
//		printf("executing script\n");
		script_executeuntiltime(frame_currenttime); // execute script
		frame_renderparticles(); // render the particles
		f += fstep;
		accumulateFB();
	}
//	printf("motion blur processing\n");
	motionblurfinishFB(motionblurpasses);
	printf("saving frame %d to %s\n", framenumber, frame_getoutputname(framenumber));
	writeframe(framenumber); // write the image to disk
}

extern int script_setup();

//extern int drawflareemptylines, drawflarelines;
extern int drawflarepixels, drawflarepixelstested;

void frame_renderframes()
{
	int f, framestartdrawflarecount;
	int starttime, endtime, framestarttime, frameendtime, drawflarepixelstestedstart;
	starttime = LH_GetTime();
	drawflarepixelstestedstart = drawflarepixelstested;
	// setup the framebuffer
	script_setup();
	for (f = frame_start;f < frame_end;f++)
	{
		//drawflareemptylines = 0;
		//drawflarelines = 0;
		framestartdrawflarecount = drawflarecount;
		framestarttime = LH_GetTime();
		frame_render(f);
		frameendtime = LH_GetTime();
		printf("frame %d: %d seconds, %d flares, pixels tested:%d rendered:%d efficiency:%.2f%% tested per second: %d\n", f, frameendtime - framestarttime, drawflarecount - framestartdrawflarecount, drawflarepixelstested, drawflarepixels, drawflarepixelstested > 0 ? drawflarepixels * 100.0f / drawflarepixelstested : 0.0f, frameendtime - framestarttime > 0 ? (drawflarepixelstested - drawflarepixelstestedstart) / (frameendtime - starttime) : drawflarepixelstested - drawflarepixelstestedstart);
//		printf("rendered frame %d in %d seconds, %d flares, quickdistance calls:%d drawflare line usage accuracy %02.03f\n", f, frameendtime - framestarttime, drawflarecount - framestartdrawflarecount, quickdistcalls, (drawflareoccupiedlines * 100.0f / drawflarelines));
		//printf("quicksqrt calls:%d hits:%d misses:%d calculated:%d hitratio:%.3f%% tableusage:%.3f%%\n", quicksqrtcalls, quicksqrtcalls - quicksqrtmisses, quicksqrtmisses, quicksqrtcalculated, quicksqrtcalls > 0 ? (quicksqrtcalls - quicksqrtmisses) * 100.0f / quicksqrtcalls : 0.0f, quicksqrtcalculated * 100.0f / 262145.0f);
	}
	endtime = LH_GetTime();
	printf("%d images rendered containing a total of %d flares, time elapsed: %d\n", (frame_end - frame_start) * motionblurpasses, drawflarecount, endtime - starttime);
}
