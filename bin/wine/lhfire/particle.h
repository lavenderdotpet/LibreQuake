
#ifndef FIRE_PARTICLE_H
#define FIRE_PARTICLE_H

#include <math.h>

// circle = x<size (a perfect circle, no falloff, only size, antialiased)
// globe = size-x (fades linearly with distance from the center, good for most things)
// glow = 1/(x*x) falloff (great for explosions, very bright in the center, quickly fades, but extends quite far)

#define prender_circle 0
#define prender_globe 1
#define prender_glow 2

typedef struct particlestruct
{
	int active;
	int rendertype;
	float time, life, size, decaystart, decayend, weightstart, weightend, pressurestart, pressureend, starttime, lifeprogress, lifetime, mass;
	float x, y, z;
	float vx, vy, vz;
	float color_red, color_green, color_blue, color_alpha;
} particle_t;

extern particle_t* particle;
extern int particles;

extern void particles_clear();
extern void particle_spawn(int rendertype, float starttime, float life, float size, float x, float y, float z, float vx, float vy, float vz, float color_r, float color_g, float color_b, float color_a, float decaystart, float decayend, float weightstart, float weightend, float pressurestart, float pressureend, float mass);
extern void particles_advance(float currenttime);
extern int particles_alloc(int number);

#endif
