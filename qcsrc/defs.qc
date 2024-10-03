/*  Copyright (C) 1996-1997  Id Software, Inc.

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

    See file, 'COPYING', for details.
*/

/*==============================================================================

			SOURCE FOR GLOBALVARS_T C STRUCTURE

==============================================================================*/

//
// system globals
//
entity		self;
entity		other;
entity		world;
float		time;
float		frametime;

#ifdef __QW__ // NQ defines this outside of C-referenced vars
entity		newmis;				// if this is set, the entity that just
								// run created a new missile that should
								// be simulated immediately
#endif

float		force_retouch;		// force all entities to touch triggers
								// next frame.  this is needed because
								// non-moving things don't normally scan
								// for triggers, and when a trigger is
								// created (like a teleport trigger), it
								// needs to catch everything.
								// decremented each frame, so set to 2
								// to guarantee everything is touched
string		mapname;

#ifndef __QW__ // QW defines these outside of C-referenced vars
float		deathmatch;
float		coop;
float		teamplay;
#endif

float		serverflags;		// propagated from level to level, used to
								// keep track of completed episodes

float		total_secrets;
float		total_monsters;

float		found_secrets;		// number of secrets found
float		killed_monsters;	// number of monsters killed


// spawnparms are used to encode information about clients across server
// level changes
float		parm1, parm2, parm3, parm4, parm5, parm6, parm7, parm8, parm9, parm10, parm11, parm12, parm13, parm14, parm15, parm16;

//
// global variables set by built in functions
//	
vector		v_forward, v_up, v_right;	// set by makevectors()
	
// set by traceline / tracebox
float		trace_allsolid;
float		trace_startsolid;
float		trace_fraction;
vector		trace_endpos;
vector		trace_plane_normal;
float		trace_plane_dist;
entity		trace_ent;
float		trace_inopen;
float		trace_inwater;

entity		msg_entity;				// destination of single entity writes

//
// required prog functions
//
void() 		main;						// only for testing

void()		StartFrame;

void() 		PlayerPreThink;
void() 		PlayerPostThink;

void()		ClientKill;
void()		ClientConnect;
void() 		PutClientInServer;		// call after setting the parm1... parms
void()		ClientDisconnect;

void()		SetNewParms;			// called when a client first connects to
									// a server. sets parms so they can be
									// saved off for restarts

void()		SetChangeParms;			// call to set parms for self so they can
									// be saved for a level transition


//================================================
void		end_sys_globals;		// flag for structure dumping
//================================================

/*
==============================================================================

			SOURCE FOR ENTVARS_T C STRUCTURE

==============================================================================
*/

//
// system fields (*** = do not set in prog code, maintained by C code)
//
.float		modelindex;		// *** model index in the precached list
.vector		absmin, absmax;	// *** origin + mins / maxs

.float		ltime;			// local time for entity

#ifdef __QW__ // Unused, as far as I can tell, but needed to keep the C struct intact
.float		lastruntime;
#endif

.float		movetype;
.float		solid;

.vector		origin;			// ***
.vector		oldorigin;		// ***
.vector		velocity;
.vector		angles;
.vector		avelocity;

#ifndef __QW__ // Differences in engine protocols
.vector		punchangle;		// temp angle adjust from damage or recoil
#endif

.string		classname;		// spawn function
.string		model;
.float		frame;
.float		skin;
.float		effects;

.vector		mins, maxs;		// bounding box extents reletive to origin
.vector		size;			// maxs - mins

.void()		touch;
.void()		use;
.void()		think;
.void()		blocked;		// for doors or plats, called when can't push other

.float		nextthink;
.entity		groundentity;

// stats
.float		health;
.float		frags;
.float		weapon;			// one of the IT_SHOTGUN, etc flags
.string		weaponmodel;
.float		weaponframe;
.float		currentammo;
.float		ammo_shells, ammo_nails, ammo_rockets, ammo_cells;

.float		items;			// bit flags

.float		takedamage;
.entity		chain;
.float		deadflag;

.vector		view_ofs;			// add to origin to get eye point


.float		button0;		// fire
.float		button1;		// use
.float		button2;		// jump

.float		impulse;		// weapon changes

.float		fixangle;
.vector		v_angle;		// view / targeting angle for players

#ifndef __QW__ // Unused, as far as I can tell, but needed to keep the C struct intact
.float		idealpitch;		// calculated pitch angle for lookup up slopes
#endif

.string		netname;

.entity 	enemy;

.float		flags;

.float		colormap;
.float		team;

.float		max_health;		// players maximum health is stored here

.float		teleport_time;	// don't back up

.float		armortype;		// save this fraction of incoming damage
.float		armorvalue;

.float		waterlevel;		// 0 = not in, 1 = feet, 2 = waist, 3 = eyes
.float		watertype;		// a contents value

.float		ideal_yaw;
.float		yaw_speed;

.entity		aiment;

.entity 	goalentity;		// a movetarget or an enemy

.float		spawnflags;

.string		target;
.string		targetname;

// damage is accumulated through a frame. and sent as one single
// message, so the super shotgun doesn't generate huge messages
.float		dmg_take;
.float		dmg_save;
.entity		dmg_inflictor;

.entity		owner;		// who launched a missile
.vector		movedir;	// mostly for doors, but also used for waterjump

.string		message;		// trigger messages

.float		sounds;		// either a cd track number or sound number

.string		noise, noise1, noise2, noise3;	// contains names of wavs to play

//================================================
void		end_sys_fields;			// flag for structure dumping
//================================================

/*
==============================================================================

				VARS NOT REFERENCED BY C CODE

==============================================================================
*/


//
// constants
//

#define FALSE	0
#define TRUE	1

// edict.flags
#define FL_FLY					1
#define FL_SWIM					2
#define FL_CLIENT				8		// set for all client edicts
#define FL_INWATER				16		// for enter / leave water splash
#define FL_MONSTER				32
#define FL_GODMODE				64		// player cheat
#define FL_NOTARGET				128		// player cheat
#define FL_ITEM					256		// extra wide size for bonus items
#define FL_ONGROUND				512		// standing on something
#define FL_PARTIALGROUND		1024	// not all corners are valid
#define FL_WATERJUMP			2048	// player jumping out of water
#define FL_JUMPRELEASED			4096	// for jump debouncing

// edict.movetype values
#define MOVETYPE_NONE			0		// never moves
//#define MOVETYPE_ANGLENOCLIP	1
//#define MOVETYPE_ANGLECLIP	2
#define MOVETYPE_WALK			3		// players only
#define MOVETYPE_STEP			4		// discrete, not real time unless fall
#define MOVETYPE_FLY			5
#define MOVETYPE_TOSS			6		// gravity
#define MOVETYPE_PUSH			7		// no clip to world, push and crush
#define MOVETYPE_NOCLIP			8
#define MOVETYPE_FLYMISSILE		9		// fly with extra size against monsters
#define MOVETYPE_BOUNCE			10
#define MOVETYPE_BOUNCEMISSILE	11		// bounce with extra size

// edict.solid values
#define SOLID_NOT				0	// no interaction with other objects
#define SOLID_TRIGGER			1	// touch on edge, but not blocking
#define SOLID_BBOX				2	// touch on edge, block
#define SOLID_SLIDEBOX			3	// touch on edge, but not an onground
#define SOLID_BSP				4	// bsp clip, touch on edge, block

// range values
#define RANGE_MELEE				0
#define RANGE_NEAR				1
#define RANGE_MID				2
#define RANGE_FAR				3

// deadflag values

#define DEAD_NO					0
#define DEAD_DYING				1
#define DEAD_DEAD				2
#define DEAD_RESPAWNABLE		3

// takedamage values

#define DAMAGE_NO				0
#define DAMAGE_YES				1
#define DAMAGE_AIM				2

// items
#define IT_AXE					4096
#define IT_SHOTGUN				1
#define IT_SUPER_SHOTGUN		2
#define IT_NAILGUN				4
#define IT_SUPER_NAILGUN		8
#define IT_GRENADE_LAUNCHER		16
#define IT_ROCKET_LAUNCHER		32
#define IT_LIGHTNING			64
#define IT_EXTRA_WEAPON			128

#define IT_SHELLS				256
#define IT_NAILS				512
#define IT_ROCKETS				1024
#define IT_CELLS				2048

#define IT_ARMOR1				8192
#define IT_ARMOR2				16384
#define IT_ARMOR3				32768
#define IT_SUPERHEALTH			65536

#define IT_KEY1					131072
#define IT_KEY2					262144

#define IT_INVISIBILITY			524288
#define IT_INVULNERABILITY		1048576
#define IT_SUIT					2097152
#define IT_QUAD					4194304

// point content values

#define CONTENT_EMPTY			-1
#define CONTENT_SOLID			-2
#define CONTENT_WATER			-3
#define CONTENT_SLIME			-4
#define CONTENT_LAVA			-5
#define CONTENT_SKY				-6

#define STATE_TOP				0
#define STATE_BOTTOM			1
#define STATE_UP				2
#define STATE_DOWN				3

#define VEC_ORIGIN				'0 0 0'
#define VEC_HULL_MIN			'-16 -16 -24'
#define VEC_HULL_MAX			'16 16 32'

#define VEC_HULL2_MIN			'-32 -32 -24'
#define VEC_HULL2_MAX			'32 32 64'

// protocol bytes
#define SVC_TEMPENTITY		23
#define SVC_KILLEDMONSTER	27
#define SVC_FOUNDSECRET		28
#define SVC_INTERMISSION	30
#define SVC_FINALE			31
#define SVC_CDTRACK			32
#define SVC_SELLSCREEN		33
#ifdef __QW__ // Differences in engine protocols
#define SVC_SMALLKICK		34
#define SVC_BIGKICK			35
#define SVC_MUZZLEFLASH		39
#else
#define SVC_CUTSCENE		34
#endif


#define TE_SPIKE			0
#define TE_SUPERSPIKE		1
#define TE_GUNSHOT			2
#define TE_EXPLOSION		3
#define TE_TAREXPLOSION		4
#define TE_LIGHTNING1		5
#define TE_LIGHTNING2		6
#define TE_WIZSPIKE			7
#define TE_KNIGHTSPIKE		8
#define TE_LIGHTNING3		9
#define TE_LAVASPLASH		10
#define TE_TELEPORT			11
#ifdef __QW__ // Differences in engine protocols
#define TE_BLOOD			12
#define TE_LIGHTNINGBLOOD	13
#endif

// sound channels
// channel 0 never willingly overrides
// other channels (1-7) allways override a playing sound on that channel
#define CHAN_AUTO			0
#define CHAN_WEAPON			1
#define CHAN_VOICE			2
#define CHAN_ITEM			3
#define CHAN_BODY			4
#ifdef __QW__ // NetQuake doesn't support CHAN_NO_PHS_ADD. Set it to 0 so it will have no effect when combined with another channel.
#define CHAN_NO_PHS_ADD 	8
#else
#define CHAN_NO_PHS_ADD 	0
#endif

#define ATTN_NONE			0
#define ATTN_NORM			1
#define ATTN_IDLE			2
#define ATTN_STATIC			3

// update types

#define UPDATE_GENERAL		0
#define UPDATE_STATIC		1
#define UPDATE_BINARY		2
#define UPDATE_TEMP			3

// entity effects

#ifdef __QW__ // Engines support different entity effects
#define EF_BRIGHTLIGHT 		4
#define EF_DIMLIGHT 		8
#define EF_FLAG1			16
#define EF_FLAG2			32
#define EF_BLUE				64	// Blue Globe effect for Quad
#define EF_RED				128
#else
#define EF_BRIGHTFIELD		1
#define EF_MUZZLEFLASH 		2
#define EF_BRIGHTLIGHT 		4
#define EF_DIMLIGHT 		8
#endif

// messages
#define MSG_BROADCAST		0		// unreliable to all
#define MSG_ONE				1		// reliable to one (msg_entity)
#define MSG_ALL				2		// reliable to all
#define MSG_INIT			3		// write to the init string

#ifdef __QW__ // Multicast is QW only
#define MSG_MULTICAST		4		// for multicast() call
#endif


// message levels
#define PRINT_LOW			0            // pickup messages
#define PRINT_MEDIUM		1            // death messages
#define PRINT_HIGH			2            // critical messages
#define PRINT_CHAT			3            // also goes to chat console

#ifdef __QW__ // Multicast is QW only
// multicast sets
#define MULTICAST_ALL		0            // every client
#define MULTICAST_PHS		1            // within hearing
#define MULTICAST_PVS		2            // within sight
#define MULTICAST_ALL_R		3            // every client, reliable
#define MULTICAST_PHS_R		4            // within hearing, reliable
#define MULTICAST_PVS_R		5            // within sight, reliable
#endif

#define AS_STRAIGHT			1
#define AS_SLIDING			2
#define AS_MELEE			3
#define AS_MISSILE			4

//================================================

//
// globals
//
#ifndef __QW__ // Used for monster code; not needed in QW
float	movedist;
#endif
float	gameover;		// set when a rule exits

string	string_null;	// null string, nothing should be held here

#ifndef __QW__ // QW defines this inside of C-referenced vars
entity	newmis;			// launch_spike sets this after spawning it
#endif

entity	activator;		// the entity that activated a trigger or brush

entity	damage_attacker;	// set by T_Damage
entity  damage_inflictor;
float	framecount;

//
// cvars checked each frame
//
float		skill;
float		timelimit;
float		fraglimit;
#ifdef __QW__ // NQ defines this inside of C-referenced vars
float		deathmatch;
float		coop;
float		teamplay;
#endif

//================================================

//
// world fields (FIXME: make globals)
//
.string		wad;
.string 	map;
.float		worldtype;	// 0=medieval 1=metal 2=base

//================================================

.string		killtarget;

//
// quakeed fields
//
.float		light_lev;		// not used by game, but parsed by light util
.float		style;


//
// monster ai
//
.void()		th_stand;
.void()		th_walk;
.void()		th_run;
.void()		th_missile;
.void()		th_melee;
.void(entity attacker, float damage)		th_pain;
.void()		th_die;

.entity		oldenemy;		// mad at this player before taking damage

.float		speed;

.float	lefty;

.float	search_time;
.float	attack_state;

//
// player only fields
//
.float		voided;
.float		walkframe;

// Zoid Additions
.float		maxspeed;		// Used to set Maxspeed on a player
.float		gravity;		// Gravity Multiplier (0 to 1.0)

.float 		attack_finished;
.float		pain_finished;

.float		invincible_finished;
.float		invisible_finished;
.float		super_damage_finished;
.float		radsuit_finished;

.float		invincible_time, invincible_sound;
.float		invisible_time, invisible_sound;
.float		super_time, super_sound;
.float		rad_time;
.float		fly_sound;

.float		axhitme;

.float		show_hostile;	// set to time+0.2 whenever a client fires a
							// weapon or takes damage.  Used to alert
							// monsters that otherwise would let the player go
.float		jump_flag;		// player jump flag
.float		swim_flag;		// player swimming sound flag
.float		air_finished;	// when time > air_finished, start drowning
.float		bubble_count;	// keeps track of the number of bubbles
.string		deathtype;		// keeps track of how the player died

//
// object stuff
//
.string		mdl;
.vector		mangle;			// angle at start

.vector		oldorigin;		// only used by secret door

.float		t_length, t_width;


//
// doors, etc
//
.vector		dest, dest1, dest2;
.float		wait;			// time from firing to restarting
.float		delay;			// time from activation to firing
.entity		trigger_field;	// door's trigger entity
.string		noise4;

//
// monsters
//
.float 		pausetime;
.entity 	movetarget;


//
// doors
//
.float		aflag;
.float		dmg;			// damage done by door when hit
	
//
// misc
//
.float		cnt; 			// misc flag
	
//
// subs
//
.void()		think1;
.vector		finaldest, finalangle;

//
// triggers
//
.float		count;			// for counting triggers


//
// plats / doors / buttons
//
.float		lip;
.float		state;
.vector		pos1, pos2;		// top and bottom positions
.float		height;

//
// sounds
//
.float		waitmin, waitmax;
.float		distance;
.float		volume;


//additions. --gnounc
.string		killstring;		//the message a monster or item leaves when it kills you "was mauled by a rottweiler" etc. //gnounc

//pitch (angles_x) is inverted in quake due to a bug
	//use makevectors2 for monsters with nonzero pitch
//anyone encountering this comment with a better understanding should update the comment to be more informative and useful to modders --gnounc
void(vector ang)	makevectors2;		

//===========================================================================
	

//
// builtin functions
//

void(vector ang)	makevectors		= #1;		// sets v_forward, etc globals
void(entity e, vector o) setorigin	= #2;
void(entity e, string m) setmodel	= #3;		// set movetype and solid first
void(entity e, vector min, vector max) setsize = #4;
// #5 was removed
void() break						= #6;
float() random						= #7;		// returns 0 - 1
void(entity e, float chan, string samp, float vol, float atten) sound = #8;
vector(vector v) normalize			= #9;
void(string e) error				= #10;
void(string e) objerror				= #11;
float(vector v) vlen				= #12;
float(vector v) vectoyaw			= #13;
entity() spawn						= #14;
void(entity e) remove				= #15;

// sets trace_* globals
// nomonsters can be:
// An entity will also be ignored for testing if forent == test,
// forent->owner == test, or test->owner == forent
// a forent of world is ignored
void(vector v1, vector v2, float nomonsters, entity forent) traceline = #16;	

entity() checkclient				= #17;	// returns a client to look for
entity(entity start, .string fld, string match) find = #18;
string(string s) precache_sound		= #19;
string(string s) precache_model		= #20;
void(entity client, string s)stuffcmd = #21;
entity(vector org, float rad) findradius = #22;

#ifdef __QW__ // QW supports print levels for console prints. NQ doesn't, so we just have it ignore the print level.
void(float level, string s) bprint					= #23;
void(entity client, float level, string s) sprint	= #24;
#else
void(string s) bprint_e								= #23;
void(entity client, string s) sprint_e				= #24;
void(float level, string s) bprint = { bprint_e(s); };
void(entity client, float level, string s) sprint = { sprint_e(client, s); };
#endif

void(string s) dprint				= #25;
string(float f) ftos				= #26;
string(vector v) vtos				= #27;
void() coredump						= #28;		// prints all edicts
void() traceon						= #29;		// turns statment trace on
void() traceoff						= #30;
void(entity e) eprint				= #31;		// prints an entire edict
float(float yaw, float dist) walkmove	= #32;	// returns TRUE or FALSE
// #33 was removed
float() droptofloor= #34;	// TRUE if landed on floor
void(float style, string value) lightstyle = #35;
float(float v) rint					= #36;		// round to nearest int
float(float v) floor				= #37;		// largest integer <= v
float(float v) ceil					= #38;		// smallest integer >= v
// #39 was removed
float(entity e) checkbottom			= #40;		// true if self is on ground
float(vector v) pointcontents		= #41;		// returns a CONTENT_*
// #42 was removed
float(float f) fabs = #43;
vector(entity e, float speed) aim = #44;		// returns the shooting vector
float(string s) cvar = #45;						// return cvar.value
void(string s) localcmd = #46;					// put string into local que
entity(entity e) nextent = #47;					// for looping through all ents

#ifndef __QW__ // Differences in engine protocols
void(vector o, vector d, float color, float count) particle = #48;// start a particle effect
#endif

void() ChangeYaw = #49;						// turn towards self.ideal_yaw
											// at self.yaw_speed
// #50 was removed
vector(vector v) vectoangles			= #51;

//
// direct client message generation
//
void(float to, float f) WriteByte		= #52;
void(float to, float f) WriteChar		= #53;
void(float to, float f) WriteShort		= #54;
void(float to, float f) WriteLong		= #55;
void(float to, float f) WriteCoord		= #56;
void(float to, float f) WriteAngle		= #57;
void(float to, string s) WriteString	= #58;
void(float to, entity s) WriteEntity	= #59;

//
// broadcast client message generation
//

// void(float f) bWriteByte		= #59;
// void(float f) bWriteChar		= #60;
// void(float f) bWriteShort		= #61;
// void(float f) bWriteLong		= #62;
// void(float f) bWriteCoord		= #63;
// void(float f) bWriteAngle		= #64;
// void(string s) bWriteString	= #65;
// void(entity e) bWriteEntity = #66;

void(float step) movetogoal				= #67;

string(string s) precache_file		= #68;	// no effect except for -copy
void(entity e) makestatic		= #69;
void(string s) changelevel = #70;

//#71 was removed

void(string var, string val) cvar_set = #72;	// sets cvar.value

void(entity client, string s) centerprint = #73;	// sprint, but in middle
void(entity client, string s, string s2) centerprint2 = #73;	// centerprint that concats two strings
void(entity client, string s, string s2, string s3) centerprint3 = #73;	// centerprint that concats three strings

void(vector pos, string samp, float vol, float atten) ambientsound = #74;

string(string s) precache_model2	= #75;		// registered version only
string(string s) precache_sound2	= #76;		// registered version only
string(string s) precache_file2		= #77;		// registered version only

void(entity e) setspawnparms		= #78;		// set parm1... to the
												// values at level start
												// for coop respawn

#ifdef __QW__ // logfrag is supported in QW, but not NQ. We just have NQ define it as an empty function.
void(entity killer, entity killee) logfrag = #79;    // add to stats
#else
void(entity killer, entity killee) logfrag = {};    // add to stats
#endif

#ifdef __QW__ // NQ does not support infokeys or stof
string(entity e, string key) infokey  = #80; // get a key value (world = serverinfo)
float(string s) stof              = #81;     // convert string to float
#endif

#ifdef __QW__ // NQ does not support multicast
void(vector where, float set) multicast = #82; // sends the temp message to a set
                                    // of clients, possibly in PVS or PHS 
#endif

//============================================================================

//
// subs.qc
//
void(vector tdest, float tspeed, void() func) SUB_CalcMove;
void(entity ent, vector tdest, float tspeed, void() func) SUB_CalcMoveEnt;
void(vector destangle, float tspeed, void() func) SUB_CalcAngleMove;
void() SUB_CalcMoveDone;
void() SUB_CalcAngleMoveDone;
void() SUB_Null;
void() SUB_UseTargets;
void() SUB_Remove;

//
//	combat.qc
//
void(entity targ, entity inflictor, entity attacker, float damage) T_Damage;


float (entity e, float healamount, float ignore) T_Heal; // health function

float(entity targ, entity inflictor) CanDamage;


