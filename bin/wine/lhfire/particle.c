
#include <stdlib.h>
#include <memory.h>
#include <stdio.h>

#include "particle.h"

#define FALSE 0
#define TRUE 1

extern void drawflare(float px, float py, float pz, float size, float red, float green, float blue);
extern void drawdirt(float px, float py, float pz);
extern float world_minx, world_maxx, world_miny, world_maxy, world_minz, world_maxz;

particle_t* particle;
int particles;

void particles_clear()
{
	if (particle)
		memset(particle, 0, particles * sizeof(particle_t));
}

int particles_alloc(int number)
{
	if (particle)
		free(particle);
	if ((particle = malloc(number * sizeof(particle_t))))
	{
		particles = number;
		particles_clear();
		return TRUE;
	}
	return FALSE;
}

//int lastparticle; // used by spawning code

void particle_spawn(int rendertype, float starttime, float life, float size, float x, float y, float z, float vx, float vy, float vz, float color_r, float color_g, float color_b, float color_a, float decaystart, float decayend, float weightstart, float weightend, float pressurestart, float pressureend, float mass)
{
	int i;
/*
	if (lastparticle >= particles)
		lastparticle = 0;
	for (i = lastparticle + 1;i != lastparticle;i++)
	{
		if (i >= particles) // loop around
			i = 0;
*/
	for (i = 0;i < particles;i++)
	{
		if (!particle[i].active)
		{
			particle[i].active = TRUE;
			particle[i].rendertype = rendertype;
			particle[i].time = starttime;
			particle[i].life = particle[i].lifetime = life;
			particle[i].size = size;
			particle[i].x = x;
			particle[i].y = y;
			particle[i].z = z;
			particle[i].vx = vx;
			particle[i].vy = vy;
			particle[i].vz = vz;
			particle[i].color_red = color_r;
			particle[i].color_green = color_g;
			particle[i].color_blue = color_b;
			particle[i].color_alpha = color_a;
			particle[i].decaystart = decaystart;
			particle[i].decayend = decayend;
			particle[i].starttime = starttime;
			particle[i].weightstart = weightstart;
			particle[i].weightend = weightend;
			particle[i].pressurestart = pressurestart;
			particle[i].pressureend = pressureend;
			particle[i].mass = mass;
			return;
		}
	}
	printf("particle_spawn: ran out of particles\n");
}

extern float gravity_x, gravity_y, gravity_z, airfriction;

void particles_advance(float currenttime)
{
	int i, world_box;
	float time, f;
	particle_t *p;
	// kill off dead particles and update life values
	for (i = 0, p = particle;i < particles;i++, p++)
	{
		if (p->active)
		{
			if ((p->lifetime + p->starttime) > currenttime)
			{
				p->lifeprogress = (currenttime - p->starttime) / p->lifetime;
				p->life = p->lifetime + p->starttime - currenttime;
			}
			else
				p->active = FALSE;
		}
	}

	// apply pressure physics
	for (i = 0, p = particle;i < particles;i++, p++)
	{
		if (p->active)
		{
			float pressure, weight;
			pressure = (p->pressureend - p->pressurestart) * p->lifeprogress + p->pressurestart;
			weight = (p->weightend - p->weightstart) * p->lifeprogress + p->weightstart;
			if (pressure < 0.0f)
				pressure = 0.0f;
			if (weight < 0.0f)
				weight = 0.0f;
			pressure -= weight;
			if (fabs(pressure) >= 0.01)
			{
				int j;
				// turn pressure into acceleration
				pressure *= currenttime - p->time;
				for (j = 0;j < particles;j++)
				{
					if (particle[j].active && j != i && particle[j].mass > 0.0f)
					{
						float distx, disty, distz, distance2, scale;
						distx = particle[j].x - p->x;
						disty = particle[j].y - p->y;
						distz = particle[j].z - p->z;
						distance2 = distx*distx+disty*disty+distz*distz;
						scale = particle[j].mass * pressure / (distance2+1);
						particle[j].vx += distx * scale;
						particle[j].vy += disty * scale;
						particle[j].vz += distz * scale;
					}
				}
			}
		}
	}

	world_box = world_minx || world_maxx || world_miny || world_maxy || world_minz || world_maxz;
	// physics
	for (i = 0, p = particle;i < particles;i++, p++)
	{
		if (p->active)
		{
			time = currenttime - p->time;
			p->time = currenttime;
			// a minimum of 100fps gravity and friction processing (coarse calculations look bad)
			if (gravity_x || gravity_y || gravity_z || p->mass * airfriction > 0)
			{
				f = 1 - (p->mass * airfriction * 0.01f);
				while (time >= 0.01f)
				{
					p->x += p->vx * 0.01f;
					p->y += p->vy * 0.01f;
					p->z += p->vz * 0.01f;
					p->vx = (p->vx - gravity_x * 0.01f) * f;
					p->vy = (p->vy - gravity_y * 0.01f) * f;
					p->vz = (p->vz - gravity_z * 0.01f) * f;
					time -= 0.01f;
				}
				// do the remaining time
				f = 1 - (p->mass * airfriction * time);
				p->x += p->vx * time;
				p->y += p->vy * time;
				p->z += p->vz * time;
				p->vx = (p->vx - gravity_x * time) * f;
				p->vy = (p->vy - gravity_y * time) * f;
				p->vz = (p->vz - gravity_z * time) * f;
			}
			else
			{
				p->x += p->vx * time;
				p->y += p->vy * time;
				p->z += p->vz * time;
			}
			// FIXME: implement BSP tree world and add BSP tree collisions here?
			if (world_box)
			{
				if (p->x < world_minx)
				{
					p->x = world_minx - (p->x - world_minx);
					p->vx = (float) fabs(p->vx);
				}
				if (p->y < world_miny)
				{
					p->y = world_miny - (p->y - world_miny);
					p->vy = (float) fabs(p->vy);
				}
				if (p->z < world_minz)
				{
					p->z = world_minz - (p->z - world_minz);
					p->vz = (float) fabs(p->vz);
				}
				if (p->x > world_maxx)
				{
					p->x = world_maxx - (p->x - world_maxx);
					p->vx = (float) -fabs(p->vx);
				}
				if (p->y > world_maxy)
				{
					p->y = world_maxy - (p->y - world_maxy);
					p->vy = (float) -fabs(p->vy);
				}
				if (p->z > world_maxz)
				{
					p->z = world_maxz - (p->z - world_maxz);
					p->vz = (float) -fabs(p->vz);
				}
			}
		}
	}
}
