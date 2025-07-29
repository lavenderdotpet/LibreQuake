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

// prototypes
void () W_WeaponFrame;
void() W_SetCurrentAmmo;
void() player_pain;
void() player_stand1;
void (vector org) spawn_tfog;
void (vector org, entity death_owner) spawn_tdeath;

float	modelindex_eyes, modelindex_player;

/*=============================================================================

				LEVEL CHANGING / INTERMISSION

=============================================================================*/

string nextmap;

float	intermission_running;
float	intermission_exittime;

/*QUAKED info_intermission (1 0.5 0.5) (-16 -16 -16) (16 16 16)
This is the camera point for the intermission.
Use mangle instead of angle, so you can set pitch or roll as well as yaw.  'pitch roll yaw'
*/
void() info_intermission =
{
};



void() SetChangeParms =
{
	if (self.health <= 0)
	{
		SetNewParms ();
		return;
	}

// remove items
	self.items = self.items - (self.items & (IT_KEY1 | IT_KEY2 | IT_INVISIBILITY | IT_INVULNERABILITY | IT_SUIT | IT_QUAD) );

// cap super health
	if (self.health > 100)
		self.health = 100;

	if (self.health < 50)
		self.health = 50;

	parm1 = self.items;
	parm2 = self.health;
	parm3 = self.armorvalue;

	if (self.ammo_shells < 25)
		parm4 = 25;

	else
		parm4 = self.ammo_shells;

	parm5 = self.ammo_nails;
	parm6 = self.ammo_rockets;
	parm7 = self.ammo_cells;
	parm8 = self.weapon;
	parm9 = self.armortype * 100;

	parm16 = (serverflags & 15);
};

void() SetNewParms =
{
	parm1 = IT_SHOTGUN | IT_AXE;
	parm2 = 100;
	parm3 = 0;
	parm4 = 25;
	parm5 = 0;
	parm6 = 0;
	parm7 = 0;
	parm8 = 1;
	parm9 = 0;
	parm16 = (serverflags & 15);
};

void() DecodeLevelParms =
{
	if (serverflags && world.model == "maps/start.bsp")
	{
		SetNewParms ();		// take away all stuff on starting new episode
	}
	else if (deathmatch)
		SetNewParms ();

	self.items = parm1;
	self.health = parm2;
	self.armorvalue = parm3;
	self.ammo_shells = parm4;
	self.ammo_nails = parm5;
	self.ammo_rockets = parm6;
	self.ammo_cells = parm7;
	self.weapon = parm8;
	self.armortype = parm9 * 0.01;

	serverflags = serverflags | parm16;
};

/*============
FindIntermission

Returns the entity to view from
============*/
entity() FindIntermission =
{
	local	entity spot;
	local	float cyc;

	// look for info_intermission first
	spot = find (world, classname, "info_intermission");
	if (spot)
	{	// pick a random one
		cyc = random() * 4;
		while (cyc > 1)
		{
			spot = find (spot, classname, "info_intermission");

			if (!spot)
				spot = find (spot, classname, "info_intermission");
			cyc = cyc - 1;
		}

		return spot;
	}

	// then look for the start position
	spot = find (world, classname, "info_player_start");
	if (spot)
		return spot;

	// testinfo_player_start is only found in regioned levels
	spot = find (world, classname, "testplayerstart");
	if (spot)
		return spot;

	objerror ("FindIntermission: no spot");

	return world;
};


void() GotoNextMap =
{
	local string newmap;

	if (cvar("samelevel"))	// if samelevel is set, stay on same level
	{
		changelevel (mapname);
	}
	else
	{

#ifdef __QW__ // NQ does not support infokeys
		newmap = infokey(world, mapname);
		if (newmap != "")
			changelevel (newmap);
		else
			changelevel (nextmap);
#else
			changelevel (nextmap);
#endif
	}
};

// cypress (09 mar 2024) -- use struct for epilogue levels.
var struct
{
	string 	map_name;
	float	cd_track;
	string 	epilogue_text;
	string 	freeware_text;
} intermission_levels[] =
{

#ifdef __LIBREQUAKE__

	{"maps/lq_e0m7.bsp", 2, LOC_EPILOGUE_0, __NULL__},

#endif // __LIBREQUAKE__

	{"maps/lq_e1m7.bsp", 2, LOC_EPILOGUE_1, LOC_EPILOGUE_1_FREEWARE},
	{"maps/lq_e2m6.bsp", 2, LOC_EPILOGUE_2, __NULL__},
	{"maps/lq_e3m6.bsp", 2, LOC_EPILOGUE_3, __NULL__},
	{"maps/lq_e4m7.bsp", 2, LOC_EPILOGUE_4, __NULL__}
};
// --cypress

void() ExitIntermission =
{
	// skip any text in deathmatch
	if (deathmatch)
	{
		GotoNextMap ();
		return;
	}

	intermission_exittime = time + 1;
	intermission_running = intermission_running + 1;

//
// run some text if at the end of an episode
//
	if (intermission_running == 2)
	{
		// cypress (09 mar 2024) -- use struct for epilogue levels.
		for (float i = 0; i < intermission_levels.length; i++)
		{
			if (world.model == intermission_levels[i].map_name)
			{
				WriteByte (MSG_ALL, SVC_CDTRACK);
				WriteByte (MSG_ALL, intermission_levels[i].cd_track);	// [cdtrack]
				WriteByte (MSG_ALL, 3);									// [looptrack], unused.

				WriteByte(MSG_ALL, SVC_FINALE);

				if (!cvar("registered") && intermission_levels[i].freeware_text != __NULL__)
				{
					WriteString(MSG_ALL, intermission_levels[i].freeware_text);
				}
				else
				{
					WriteString(MSG_ALL, intermission_levels[i].epilogue_text);
				}
				return;
			}
		}
		// --cypress

		GotoNextMap();
	}

	if (intermission_running == 3)
	{
		if (!cvar("registered"))
		{	// shareware episode has been completed, go to sell screen
			WriteByte (MSG_ALL, SVC_SELLSCREEN);

			return;
		}

		if ( (serverflags&15) == 15)
		{
			WriteByte (MSG_ALL, SVC_FINALE);
			WriteString (MSG_ALL, LOC_EPILOGUE_RUNES);

			return;
		}

	}

	GotoNextMap();
};

/*============
IntermissionThink

When the player presses attack or jump, change to the next level
============*/
void() IntermissionThink =
{
	if (time < intermission_exittime)
		return;

	if (!self.button0 && !self.button1 && !self.button2)
		return;

	ExitIntermission ();
};

void() execute_changelevel =
{
	local entity	pos;

	intermission_running = 1;

	// enforce a wait time before allowing changelevel
	if (deathmatch)
		intermission_exittime = time + 5;

	else
		intermission_exittime = time + 2;

	pos = FindIntermission ();

	other = find (world, classname, "player");

	while (other != world)
	{
		other.view_ofs = '0 0 0';
		other.angles = other.v_angle = pos.mangle;
		other.fixangle = TRUE;		// turn this way immediately
		other.nextthink = time + 0.5;
		other.takedamage = DAMAGE_NO;
		other.solid = SOLID_NOT;
		other.movetype = MOVETYPE_NONE;
		other.modelindex = 0;
		setorigin (other, pos.origin);
		other = find (other, classname, "player");
	}

#ifdef __QW__ // Differences in engine protocols
	WriteByte (MSG_ALL, SVC_CDTRACK);
	WriteByte (MSG_ALL, 3);

	WriteByte (MSG_ALL, SVC_INTERMISSION);
	WriteCoord (MSG_ALL, pos.origin_x);
	WriteCoord (MSG_ALL, pos.origin_y);
	WriteCoord (MSG_ALL, pos.origin_z);
	WriteAngle (MSG_ALL, pos.mangle_x);
	WriteAngle (MSG_ALL, pos.mangle_y);
	WriteAngle (MSG_ALL, pos.mangle_z);
#else
	WriteByte (MSG_ALL, SVC_CDTRACK);
	WriteByte (MSG_ALL, 3);
	WriteByte (MSG_ALL, 3);
	WriteByte (MSG_ALL, SVC_INTERMISSION);
#endif
};


void() changelevel_touch =
{
	if (other.classname != "player")
		return;

#ifdef __QW__ // noexit cvar is not supported in QW
	if ((cvar("samelevel") == 2) || ((cvar("samelevel") == 3) && (mapname != "start")))
	{
		T_Damage (other, self, self, 50000);
		return;
	}
#else
	if ((cvar("noexit") == 1) || ((cvar("noexit") == 2) && (mapname != "start")))
	{
		T_Damage (other, self, self, 50000);
		return;
	}
#endif

	if (deathmatch || coop)
	{
		bprint (PRINT_HIGH, other.netname);
		bprint (PRINT_HIGH, LOC_CLIENT_EXIT_LEVEL);
		bprint (PRINT_HIGH, "\n");
	}

	nextmap = self.map;

	SUB_UseTargets ();

	if ( (self.spawnflags & 1) && (deathmatch == 0) )
	{	// NO_INTERMISSION
		GotoNextMap();

		return;
	}

	self.touch = __NULL__;

	// we can't move people right now, because touch functions are called
	// in the middle of C movement code, so set a think time to do it
	self.think = execute_changelevel;
	self.nextthink = time + 0.1;
};

/*QUAKED trigger_changelevel (0.5 0.5 0.5) ? NO_INTERMISSION
When the player touches this, he gets sent to the map listed in the "map" variable.
Unless the NO_INTERMISSION flag is set, the view will go to the info_intermission
spot and display stats.
*/
void() trigger_changelevel =
{
	if (!self.map)
		objerror ("changelevel trigger doesn't have map");

	//gnounc
	self.netname = "changelevel";
	self.killstring = LOC_DEATH_LEAVE;

	InitTrigger ();
	self.touch = changelevel_touch;
};


/*=============================================================================

				PLAYER GAME EDGE FUNCTIONS

=============================================================================*/

void() set_suicide_frame;

// called by ClientKill and DeadThink
void() respawn =
{
	if (coop)
	{
		// make a copy of the dead body for appearances sake
		CopyToBodyQueue (self);
		// get the spawn parms as they were at level start
		setspawnparms (self);
		// respawn
		PutClientInServer ();
	}

	else if (deathmatch)
	{
		// make a copy of the dead body for appearances sake
		CopyToBodyQueue (self);
		// respawn
		PutClientInServer ();
	}

	else
	{	// restart the entire server
		localcmd ("restart\n");
	}
};


/*
============
ClientKill

Player entered the suicide command
============
*/
void() ClientKill =
{
	bprint (PRINT_MEDIUM, self.netname);
	bprint (PRINT_MEDIUM, LOC_DEATH_SUICIDE);
	bprint (PRINT_MEDIUM, "\n");
	set_suicide_frame ();
	self.modelindex = modelindex_player;
	logfrag (self, self);
	self.frags = self.frags - 2;	// extra penalty
	respawn ();
};

float(vector v) CheckSpawnPoint =
{
	return FALSE;
};

/*============
SelectSpawnPoint

Returns the entity to spawn at
============*/
entity() SelectSpawnPoint =
{
	local   entity spot, thing;
	local   float   numspots, totalspots;
	local   float   pcount;
	local entity spots;

	numspots = 0;
	totalspots = 0;

	// testinfo_player_start is only found in regioned levels
	spot = find (world, classname, "testplayerstart");
	if (spot)
		return spot;

	// choose a info_player_deathmatch point
	if (coop)
	{
		lastspawn = find(lastspawn, classname, "info_player_coop");
		if (lastspawn == world)
			lastspawn = find (lastspawn, classname, "info_player_start");
		if (lastspawn != world)
			return lastspawn;
	}
	else if (deathmatch)
	{

		// ok, find all spots that don't have players nearby
		spots = world;
		spot = find (world, classname, "info_player_deathmatch");

		while (spot)
		{
			totalspots = totalspots + 1;

			thing=findradius(spot.origin, 84);
			pcount=0;

			while (thing)
			{
				if (thing.classname == "player")
					pcount=pcount + 1;

				thing=thing.chain;
			}

			if (pcount == 0)
			{
				spot.goalentity = spots;
				spots = spot;
				numspots = numspots + 1;
			}

			// Get the next spot in the chain
			spot = find (spot, classname, "info_player_deathmatch");
		}
		totalspots=totalspots - 1;

		if (!numspots)
		{
			// ack, they are all full, just pick one at random
			totalspots = rint((random() * totalspots));
			spot = find (world, classname, "info_player_deathmatch");

			while (totalspots > 0)
			{
				totalspots = totalspots - 1;
				spot = find (spot, classname, "info_player_deathmatch");
			}
			return spot;
		}

		// We now have the number of spots available on the map in numspots
		// Generate a random number between 1 and numspots
		numspots = numspots - 1;

		numspots = rint((random() * numspots ) );

		spot = spots;
		while (numspots > 0)
		{
			spot = spot.goalentity;
			numspots = numspots - 1;
		}

		return spot;
	}

	if (serverflags)
	{	// return with a rune to start
		spot = find (world, classname, "info_player_start2");

		if (spot)
			return spot;
	}

	spot = find (world, classname, "info_player_start");
	if (!spot)
		error ("PutClientInServer: no info_player_start on level");

	return spot;
};

/*===========
PutClientInServer

called each time a player is spawned
============*/
void() DecodeLevelParms;
void() PlayerDie;


void() PutClientInServer =
{
	local	entity spot;
	local	float  axes_only;

	self.classname = "player";
	self.health = 100;
	self.takedamage = DAMAGE_AIM;
	self.solid = SOLID_SLIDEBOX;
	self.movetype = MOVETYPE_WALK;
	self.show_hostile = 0;
	self.max_health = 100;
	self.flags = FL_CLIENT;
	self.air_finished = time + 12;
	self.dmg = 2;   		// initial water damage
	self.super_damage_finished = 0;
	self.radsuit_finished = 0;
	self.invisible_finished = 0;
	self.invincible_finished = 0;
	self.effects = 0;
	self.invincible_time = 0;

	DecodeLevelParms ();

	W_SetCurrentAmmo ();

	self.attack_finished = time;
	self.th_pain = (void(entity attacker, float damage)) player_pain;
	self.th_die = PlayerDie;

	self.deadflag = DEAD_NO;
	// pausetime is set by teleporters to keep the player from moving a while
	self.pausetime = 0;

	spot = SelectSpawnPoint ();

	self.origin = spot.origin + '0 0 1';
	self.angles = spot.angles;
	self.fixangle = TRUE;		// turn this way immediately

	// oh, this is a hack!
	setmodel (self, "progs/eyes.mdl");
	modelindex_eyes = self.modelindex;

	setmodel (self, "progs/player.mdl");
	modelindex_player = self.modelindex;

	setsize (self, VEC_HULL_MIN, VEC_HULL_MAX);

	self.view_ofs = '0 0 22';

	self.velocity = '0 0 0';

	player_stand1 ();

	if (deathmatch || coop)
	{
		makevectors2(self.angles);
		spawn_tfog (self.origin + v_forward*20);
	}

	spawn_tdeath (self.origin, self);

	stuffcmd(self, "-attack\n");            // Supa, prevent shooting after respawning in MP

#ifdef __QW__ // NQ does not support infokeys
	axes_only = stof(infokey(world, "axe"));
#endif

	// Deathmatch 4 starting items
	if (deathmatch_supermode())
	{
		self.items = self.items - (self.items & (IT_ARMOR1 | IT_ARMOR2 | IT_ARMOR3)) + IT_ARMOR3;
		self.armorvalue = 200;
		self.armortype = 0.8;
		self.health = 250;
		self.items = self.items | IT_INVULNERABILITY;
		self.invincible_time = 1;
		self.invincible_finished = time + 3;
	}

	// Deathmatch 5 starting items
	if (deathmatch_supermode2())
	{
		self.items = self.items - (self.items & (IT_ARMOR1 | IT_ARMOR2 | IT_ARMOR3)) + IT_ARMOR3;
		self.armorvalue = 200;
		self.armortype = 0.8;
		self.health = 200;
		self.items = self.items | IT_INVULNERABILITY;
		self.invincible_time = 1;
		self.invincible_finished = time + 3;
	}

	if (deathmatch_no_shotgun())
	{
		self.items = self.items - (self.items & IT_SHOTGUN);
		self.ammo_shells = 0;
	}

	if (deathmatch_starting_nailgun())
	{
		self.items = self.items | IT_NAILGUN;
		self.ammo_nails = 80;
		self.weapon = IT_NAILGUN;
	}
	if (deathmatch_starting_super_shotgun())
	{
		self.items = self.items | IT_SUPER_SHOTGUN;
		self.ammo_shells = 30;
		self.weapon = IT_SUPER_SHOTGUN;
	}
	if (deathmatch_starting_super_nailgun())
	{
		self.items = self.items | IT_SUPER_NAILGUN;
		self.ammo_nails = 80;
		self.weapon = IT_SUPER_NAILGUN;
	}
	if (deathmatch_starting_grenade_launcher())
	{
		self.items = self.items | IT_GRENADE_LAUNCHER;
		self.ammo_rockets = 10;
		self.weapon = IT_GRENADE_LAUNCHER;
	}
	if (deathmatch_starting_lightning_gun())
	{
		self.items = self.items | IT_LIGHTNING;
		self.ammo_cells = 30;
		self.weapon = IT_LIGHTNING;
	}
	if (deathmatch_starting_rocket_launcher())
	{
		self.items = self.items | IT_ROCKET_LAUNCHER;
		self.ammo_rockets = 10;
		self.weapon = IT_ROCKET_LAUNCHER;
	}

	if (deathmatch_unlimited_ammo())
	{
		self.ammo_nails = 255;
		self.ammo_shells = 255;
		self.ammo_rockets = 255;
		self.ammo_cells = 255;
	}

	// Axes only
	if (deathmatch_axe_only())
	{
		self.ammo_nails = 0;
		self.ammo_shells = 0;
		self.ammo_rockets = 0;
		self.ammo_cells = 0;
		self.items = self.items - (self.items & (
			IT_SHOTGUN |
			IT_SUPER_SHOTGUN |
			IT_NAILGUN |
			IT_SUPER_NAILGUN |
			IT_GRENADE_LAUNCHER |
			IT_ROCKET_LAUNCHER |
			IT_LIGHTNING
		));
		self.weapon = IT_AXE;
	}
	
	W_SetCurrentAmmo ();
};


/*=============================================================================

				QUAKED FUNCTIONS

=============================================================================*/


/*QUAKED info_player_start (1 0 0) (-16 -16 -24) (16 16 24)
{
    model({"path": "progs/player.mdl", "skin": 0, "frame": 0});
}
The normal starting point for a level.
*/
void() info_player_start =
{
};


/*QUAKED info_player_start2 (1 0 0) (-16 -16 -24) (16 16 24)
{
    model({"path": "progs/player.mdl", "skin": 0, "frame": 0});
}
Only used on start map for the return point from an episode.
*/
void() info_player_start2 =
{
};


/*
saved out by quaked in region mode
*/
void() testplayerstart =
{
};

/*QUAKED info_player_deathmatch (1 0 1) (-16 -16 -24) (16 16 24)
{
    model({"path": "progs/player.mdl", "skin": 0, "frame": 0});
}
potential spawning position for deathmatch games
*/
void() info_player_deathmatch =
{
};

/*QUAKED info_player_coop (1 0 1) (-16 -16 -24) (16 16 24)
{
    model({"path": "progs/player.mdl", "skin": 0, "frame": 0});
}
potential spawning position for coop games
*/
void() info_player_coop =
{
};

/*
===============================================================================

RULES

===============================================================================
*/

/*
go to the next level for deathmatch
*/
void() NextLevel =
{
	local entity o;

	if (nextmap != string_null)
		return; // already done

	if (mapname == "start")
	{
		if (!cvar("registered"))
		{
			mapname = "lq_e1m1";
		}

		else if (!(serverflags & 1))
		{
			mapname = "lq_e1m1";
			serverflags = serverflags | 1;
		}

		else if (!(serverflags & 2))
		{
			mapname = "lq_e2m1";
			serverflags = serverflags | 2;
		}

		else if (!(serverflags & 4))
		{
			mapname = "lq_e3m1";
			serverflags = serverflags | 4;
		}

		else if (!(serverflags & 8))
		{
			mapname = "lq_e4m1";
			serverflags = serverflags - 7;
		}

		o = spawn();
		o.map = mapname;
	}

	else
	{
		// find a trigger changelevel
		o = find(world, classname, "trigger_changelevel");

		if (!o || mapname == "start")
		{       // go back to same map if no trigger_changelevel
			o = spawn();
			o.map = mapname;
		}
	}

	nextmap = o.map;
	gameover = TRUE; // gb

	if (o.nextthink < time)
	{
		o.think = execute_changelevel;
		o.nextthink = time + 0.1;
	}
};

/*============
CheckRules

Exit deathmatch games upon conditions
============*/
void() CheckRules =
{
	if (gameover)	// someone else quit the game already
		return;

	if (timelimit && time >= timelimit)
	{
		NextLevel ();
		return;
	}

	if (fraglimit && self.frags >= fraglimit)
	{
		NextLevel ();
		return;
	}
};

//============================================================================

void() PlayerDeathThink =
{
	local float		forward;

	if ((self.flags & FL_ONGROUND))
	{
		forward = vlen (self.velocity);
		forward = forward - 20;

		if (forward <= 0)
			self.velocity = '0 0 0';

		else
			self.velocity = forward * normalize(self.velocity);
	}

	// Anti-stall: If the player has been dead for too long, auto-respawn them against their will
	if (deathmatch && (time > self.search_time + 10)) {
		respawn();
		return;
	}

	// wait for all buttons released
	if (self.deadflag == DEAD_DEAD)
	{
		if (self.button2 || self.button1 || self.button0)
			return;

		self.deadflag = DEAD_RESPAWNABLE;

		return;
	}

	// wait for any button down
	if (!self.button2 && !self.button1 && !self.button0)
		return;

	self.button0 = 0;
	self.button1 = 0;
	self.button2 = 0;
	respawn();
};


void() PlayerJump =
{
	if (self.flags & FL_WATERJUMP)
		return;

	if (self.waterlevel >= 2)
	{

#ifndef __QW__ // QW handles this movement code in the engine for client-side prediction
		if (self.watertype == CONTENT_WATER)
			self.velocity_z = 100;

		else if (self.watertype == CONTENT_SLIME)
			self.velocity_z = 80;

		else
			self.velocity_z = 50;
#endif

		// play swimming sound
		if (self.swim_flag < time)
		{
			self.swim_flag = time + 1;

			if (random() < 0.5)
				sound (self, CHAN_BODY, "misc/water1.wav", 1, ATTN_NORM);

			else
				sound (self, CHAN_BODY, "misc/water2.wav", 1, ATTN_NORM);
		}

		return;
	}

	if (!(self.flags & FL_ONGROUND))
		return;

	if ( !(self.flags & FL_JUMPRELEASED) )
		return;		// don't pogo stick

	self.flags = self.flags - (self.flags & FL_JUMPRELEASED);



	self.button2 = 0;
	// player jumping sound
	sound (self, CHAN_AUTO, "player/plyrjmp8.wav", 1, ATTN_NORM);

#ifndef __QW__ // QW handles this movement code in the engine for client-side prediction
	self.flags = self.flags - FL_ONGROUND;	// don't stairwalk
	self.velocity_z = self.velocity_z + 270;
#endif

};


/*===========
WaterMove

============*/
.float	dmgtime;

void() WaterMove =
{
	if (self.movetype == MOVETYPE_NOCLIP)
		return;

	if (self.health < 0)
		return;

	if (self.waterlevel != 3)
	{
		if (self.air_finished < time)
			sound (self, CHAN_VOICE, "player/gasp2.wav", 1, ATTN_NORM);

		else if (self.air_finished < time + 9)
			sound (self, CHAN_VOICE, "player/gasp1.wav", 1, ATTN_NORM);
		self.air_finished = time + 12;
		self.dmg = 2;
	}

	else if (self.air_finished < time)
	{	// drown!
		if (self.pain_finished < time)
		{
			self.dmg = self.dmg + 2;

			if (self.dmg > 15)
				self.dmg = 10;

			self.deathtype = "drowning";
			T_Damage (self, world, world, self.dmg);
			self.pain_finished = time + 1;
		}
	}

	if (!self.waterlevel)
	{
		if (self.flags & FL_INWATER)
		{
			// play leave water sound
			sound (self, CHAN_BODY, "misc/outwater.wav", 1, ATTN_NORM);
			self.flags = self.flags - FL_INWATER;
		}

		return;
	}

	if (self.watertype == CONTENT_LAVA)
	{	// do damage
		if (self.dmgtime < time)
		{
			if (self.radsuit_finished > time)
				self.dmgtime = time + 1;

			else
				self.dmgtime = time + 0.2;

			self.deathtype = "lava";
			T_Damage (self, world, world, 10*self.waterlevel);
		}
	}
	else if (self.watertype == CONTENT_SLIME)
	{	// do damage
		if (self.dmgtime < time && self.radsuit_finished < time)
		{
			self.dmgtime = time + 1;
			self.deathtype = "slime";
			T_Damage (self, world, world, 4*self.waterlevel);
		}
	}

	if ( !(self.flags & FL_INWATER) )
	{

		// player enter water sound

		if (self.watertype == CONTENT_LAVA)
			sound (self, CHAN_BODY, "player/inlava.wav", 1, ATTN_NORM);

		if (self.watertype == CONTENT_WATER)
			sound (self, CHAN_BODY, "player/inh2o.wav", 1, ATTN_NORM);

		if (self.watertype == CONTENT_SLIME)
			sound (self, CHAN_BODY, "player/slimbrn2.wav", 1, ATTN_NORM);

		self.flags = self.flags + FL_INWATER;
		self.dmgtime = 0;
	}

#ifndef __QW__ // QW handles this movement code in the engine for client-side prediction
	if (! (self.flags & FL_WATERJUMP) )
		self.velocity = self.velocity - 0.8*self.waterlevel*frametime*self.velocity;
#endif
};

void() CheckWaterJump =
{
#ifndef __QW__ // QW handles this movement code in the engine for client-side prediction
	local vector start, end;

// check for a jump-out-of-water
	makevectors2 (self.angles);
	start = self.origin;
	start_z = start_z + 8;
	v_forward_z = 0;
	normalize(v_forward);
	end = start + v_forward*24;
	traceline (start, end, TRUE, self);

	if (trace_fraction < 1)
	{	// solid at waist
		start_z = start_z + self.maxs_z - 8;
		end = start + v_forward*24;
		self.movedir = trace_plane_normal * -50;
		traceline (start, end, TRUE, self);

		if (trace_fraction == 1)
		{	// open at eye level
			self.flags = self.flags | FL_WATERJUMP;
			self.velocity_z = 225;
			self.flags = self.flags - (self.flags & FL_JUMPRELEASED);
			self.teleport_time = time + 2;	// safety net

			return;
		}
	}
#endif
};


/*================
PlayerPreThink

Called every frame before physics are run
================*/
void() PlayerPreThink =
{
	if (intermission_running)
	{
		IntermissionThink ();	// otherwise a button could be missed between
		return;					// the think tics
	}

	if (self.view_ofs == '0 0 0')
		return;		// intermission or finale

	makevectors (self.v_angle);		// is this still used

	if (deathmatch || coop)	// gb, this is a waste in SP
		CheckRules ();

	WaterMove ();

	if (self.waterlevel == 2)
		CheckWaterJump ();

	if (self.deadflag >= DEAD_DEAD)
	{
		PlayerDeathThink ();
		return;
	}

	if (self.deadflag == DEAD_DYING)
		return;	// dying, so do nothing

	if (self.button2)
	{
		PlayerJump ();
	}

	else
		self.flags = self.flags | FL_JUMPRELEASED;

	// teleporters can force a non-moving pause time
	if (time < self.pausetime)
		self.velocity = '0 0 0';

	if(time > self.attack_finished && self.currentammo == 0 && self.weapon != IT_AXE)
	{
		self.weapon = W_BestWeapon ();
		W_SetCurrentAmmo ();
	}
};

/*================
CheckPowerups

Check for turning off powerups
================*/
void() CheckPowerups =
{
	if (self.health <= 0)
		return;

	// invisibility
	if (self.invisible_finished)
	{
		// sound and screen flash when items starts to run out
		if (self.invisible_sound < time)
		{
			sound (self, CHAN_AUTO, "items/inv3.wav", 0.5, ATTN_IDLE);
			self.invisible_sound = time + ((random() * 3) + 1);
		}


		if (self.invisible_finished < time + 3)
		{
			if (self.invisible_time == 1)
			{
				sprint (self, PRINT_HIGH, LOC_ITEM_FADE_SHADRING);
				sprint (self, PRINT_HIGH, "\n");
				stuffcmd (self, "bf\n");
				sound (self, CHAN_AUTO, "items/inv2.wav", 1, ATTN_NORM);
				self.invisible_time = time + 1;
			}

			if (self.invisible_time < time)
			{
				self.invisible_time = time + 1;
				stuffcmd (self, "bf\n");
			}
		}

		if (self.invisible_finished < time)
		{	// just stopped
			self.items = self.items - IT_INVISIBILITY;
			self.invisible_finished = 0;
			self.invisible_time = 0;
		}

	// use the eyes
		self.frame = 0;
		self.modelindex = modelindex_eyes;
	}

	else
		self.modelindex = modelindex_player;	// don't use eyes

	// invincibility
	if (self.invincible_finished)
	{
	// sound and screen flash when items starts to run out
		if (self.invincible_finished < time + 3)
		{
			if (self.invincible_time == 1)
			{
				sprint (self, PRINT_HIGH, LOC_ITEM_FADE_PENTPROT);
				sprint (self, PRINT_HIGH, "\n");
				stuffcmd (self, "bf\n");
				sound (self, CHAN_AUTO, "items/protect2.wav", 1, ATTN_NORM);
				self.invincible_time = time + 1;
			}

			if (self.invincible_time < time)
			{
				self.invincible_time = time + 1;
				stuffcmd (self, "bf\n");
			}
		}

		if (self.invincible_finished < time)
		{	// just stopped
			self.items = self.items - IT_INVULNERABILITY;
			self.invincible_time = 0;
			self.invincible_finished = 0;
		}
		if (self.invincible_finished > time)
		{
			self.effects = self.effects | EF_DIMLIGHT;
#ifdef __QW__ // EF_RED is not supported in NQ
			self.effects = self.effects | EF_RED;
#endif
		}
		else
		{
			self.effects = self.effects - (self.effects & EF_DIMLIGHT);
#ifdef __QW__ // EF_RED is not supported in NQ
			self.effects = self.effects - (self.effects & EF_RED);
#endif
		}
	}

	// super damage
	if (self.super_damage_finished)
	{

		// sound and screen flash when items starts to run out
		if (self.super_damage_finished < time + 3)
		{
			if (self.super_time == 1)
			{
				if (deathmatch_supermode())
					sprint (self, PRINT_HIGH, LOC_ITEM_FADE_OCTDMG);
				else
					sprint (self, PRINT_HIGH, LOC_ITEM_FADE_QUADDMG);
				sprint (self, PRINT_HIGH, "\n");
				stuffcmd (self, "bf\n");
				sound (self, CHAN_AUTO, "items/damage2.wav", 1, ATTN_NORM);
				self.super_time = time + 1;
			}

			if (self.super_time < time)
			{
				self.super_time = time + 1;
				stuffcmd (self, "bf\n");
			}
		}

		if (self.super_damage_finished < time)
		{	// just stopped
			self.items = self.items - IT_QUAD;
			if (deathmatch_supermode())
			{
				self.ammo_cells = 255;
				self.armorvalue = 1;
				self.armortype = 0.8;
				self.health = 100;
			}
			self.super_damage_finished = 0;
			self.super_time = 0;
		}
		if (self.super_damage_finished > time)
		{
			self.effects = self.effects | EF_DIMLIGHT;
#ifdef __QW__ // EF_BLUE is not supported in NQ
			self.effects = self.effects | EF_BLUE;
#endif
		}

		else
		{
			self.effects = self.effects - (self.effects & EF_DIMLIGHT);
#ifdef __QW__ // EF_BLUE is not supported in NQ
			self.effects = self.effects - (self.effects & EF_BLUE);
#endif
		}
	}

	// suit
	if (self.radsuit_finished)
	{
		self.air_finished = time + 12;		// don't drown

		// sound and screen flash when items starts to run out
		if (self.radsuit_finished < time + 3)
		{
			if (self.rad_time == 1)
			{
				sprint (self, PRINT_HIGH, LOC_ITEM_FADE_BIOSUIT);
				sprint (self, PRINT_HIGH, "\n");
				stuffcmd (self, "bf\n");
				sound (self, CHAN_AUTO, "items/suit2.wav", 1, ATTN_NORM);
				self.rad_time = time + 1;
			}

			if (self.rad_time < time)
			{
				self.rad_time = time + 1;
				stuffcmd (self, "bf\n");
			}
		}

		if (self.radsuit_finished < time)
		{	// just stopped
			self.items = self.items - IT_SUIT;
			self.rad_time = 0;
			self.radsuit_finished = 0;
		}
	}

};


/*================
PlayerPostThink

Called every frame after physics are run
================*/
void() PlayerPostThink =
{
	if (self.view_ofs == '0 0 0')
		return;		// intermission or finale

	if (self.deadflag)
		return;

	// check to see if player landed and play landing sound
	if ((self.jump_flag < -300) && (self.flags & FL_ONGROUND) && (self.health > 0))
	{
		if (self.watertype == CONTENT_WATER)
			sound (self, CHAN_BODY, "player/h2ojump.wav", 1, ATTN_NORM);

		else if (self.jump_flag < -650)
		{
			self.deathtype = "falling"; // Moved up so it happens before damage	// ZungryWare
			T_Damage (self, world, world, 5);
			sound (self, CHAN_VOICE, "player/land2.wav", 1, ATTN_NORM);
		}

		else
			sound (self, CHAN_VOICE, "player/land.wav", 1, ATTN_NORM);

		self.jump_flag = 0;
	}

#ifdef __QW__ // Honestly not sure why this branch is necessary. Possibly related to movement physics differences.
	self.jump_flag = self.velocity_z;
#else
	if (!(self.flags & FL_ONGROUND))
		self.jump_flag = self.velocity_z;
#endif

	CheckPowerups ();

	W_WeaponFrame (); // do weapon stuff
};


/*===========
ClientConnect

called when a player connects to a server
============*/
void() ClientConnect =
{
	bprint (PRINT_HIGH, self.netname);
	bprint (PRINT_HIGH, LOC_CLIENT_JOIN);
	bprint (PRINT_HIGH, "\n");

	// a client connecting during an intermission can cause problems
	if (intermission_running)
		ExitIntermission ();
};


/*===========
ClientDisconnect

called when a player disconnects from a server
============*/
void() ClientDisconnect =
{
	if (gameover)
		return;

	// if the level end trigger has been activated, just return
	// since they aren't *really* leaving

	// let everyone else know
	bprint (PRINT_HIGH, self.netname);
	bprint (PRINT_HIGH, LOC_CLIENT_DISCON_A);
	bprint (PRINT_HIGH, ftos(self.frags));
	bprint (PRINT_HIGH, LOC_CLIENT_DISCON_B);
	bprint (PRINT_HIGH, "\n");
	sound (self, CHAN_BODY, "player/tornoff2.wav", 1, ATTN_NONE);
	set_suicide_frame ();
};

/*===========
ClientObituary

called when a player dies
============*/
void(entity targ, entity attacker) ClientObituary =
{
	local	float	rnum;
	local	float	attacker_weapon;

	local	string	deathstring, deathstring2;

	local	float	on_team;

#ifdef __QW__ // QW handles teams differently
	local	string	attackerteam, targteam;
#else
	local	float	attackerteam, targteam;
#endif

#ifdef __QW__ // QW handles teams differently
	attackerteam = infokey(attacker, "team");
	targteam = infokey(targ, "team");
	on_team = attackerteam != "";
#else
	// gb
	attackerteam = attacker.team;
	targteam = targ.team;
	on_team = attackerteam != 0;
#endif

	deathstring = deathstring2 = string_null;

	rnum = random();

	if (targ.deathtype == "selfwater")
	{
		bprint (PRINT_MEDIUM, targ.netname);
		bprint (PRINT_MEDIUM, LOC_DEATH_DISCHARGE_SELF);
		bprint (PRINT_MEDIUM, "\n");
		targ.frags = targ.frags - 1;
		return;
	}

	if (targ.classname == "player")
	{
		if (attacker.classname == "teledeath" || attacker.classname == "teledeath3")
		{
			bprint (PRINT_MEDIUM, targ.netname);
			bprint (PRINT_MEDIUM, LOC_DEATH_TELEFRAG);
			bprint (PRINT_MEDIUM, attacker.owner.netname);
			bprint (PRINT_MEDIUM, "\n");

			attacker.owner.frags = attacker.owner.frags + 1;
			logfrag (attacker.owner, targ);

			return;
		}

		if (attacker.classname == "teledeath2")
		{
			bprint (PRINT_MEDIUM, LOC_DEATH_DEFLECT_A);
			bprint (PRINT_MEDIUM, targ.netname);
			bprint (PRINT_MEDIUM, LOC_DEATH_DEFLECT_B);
			bprint (PRINT_MEDIUM, attacker.owner.netname);
			bprint (PRINT_MEDIUM, "\n");

			attacker.owner.frags = attacker.owner.frags + 1;
			logfrag (attacker.owner, targ);

			return;
		}

		if (attacker.classname == "trigger_hurt")
		{
			// Custom death messages for trigger_hurt
			if (attacker.dmg == 666000) {
				bprint(PRINT_MEDIUM, targ.netname);

#ifdef __LIBREQUAKE__

				if (random() < 0.01)
					bprint(PRINT_MEDIUM, LOC_DEATH_FALL2);
				else
					bprint(PRINT_MEDIUM, LOC_DEATH_FALL1);

#else

				bprint(PRINT_MEDIUM, LOC_DEATH_FALL);

#endif // __LIBREQUAKE__

				bprint(PRINT_MEDIUM, "\n");
				return;
			}

			if (attacker.dmg == 666001) {
				bprint(PRINT_MEDIUM, targ.netname);

#ifdef __LIBREQUAKE__

				if (random() < 0.01)
					bprint(PRINT_MEDIUM, LOC_DEATH_SPACE2);
				else
					bprint(PRINT_MEDIUM, LOC_DEATH_SPACE1);

#else

				bprint(PRINT_MEDIUM, LOC_DEATH_FALL);

#endif // __LIBREQUAKE__

				bprint(PRINT_MEDIUM, "\n");
				return;
			}

			if (attacker.dmg == 666002) {
				bprint(PRINT_MEDIUM, targ.netname);

#ifdef __LIBREQUAKE__

				if (random() < 0.01)
					bprint(PRINT_MEDIUM, LOC_DEATH_VOID2);
				else
					bprint(PRINT_MEDIUM, LOC_DEATH_VOID1);

#else

				bprint(PRINT_MEDIUM, LOC_DEATH_FALL);

#endif // __LIBREQUAKE__

				bprint(PRINT_MEDIUM, "\n");
				return;
			}
		}

		if (targ.deathtype == "squish")
		{
			if (teamplay && targteam == attackerteam && on_team && targ != attacker)
			{
				logfrag (attacker, attacker);
				attacker.frags = attacker.frags - 1; 
				bprint (PRINT_MEDIUM, attacker.netname);
				bprint (PRINT_MEDIUM, LOC_TEAMKILL_SQUISH);
				bprint (PRINT_MEDIUM, "\n");
				return;
			}
			else if (attacker.classname == "player" && attacker != targ)
			{
				bprint (PRINT_MEDIUM, targ.netname);
				bprint (PRINT_MEDIUM, LOC_DEATH_SQUISH2);
				bprint (PRINT_MEDIUM, attacker.netname);
				bprint (PRINT_MEDIUM, "\n");
				logfrag (attacker, targ);
				attacker.frags = attacker.frags + 1;
				return;
			}
			else
			{
				logfrag (targ, targ);
				targ.frags = targ.frags - 1;            // killed self
				bprint (PRINT_MEDIUM, targ.netname);
				bprint (PRINT_MEDIUM, " was squished\n");
				return;
			}
		}

		if (attacker.classname == "player")
		{
			if (targ == attacker)
			{
				// killed self
				logfrag (attacker, attacker);
				attacker.frags = attacker.frags - 1;
				bprint (PRINT_MEDIUM, targ.netname);
				
				if (targ.deathtype == "grenade")
				{
					bprint (PRINT_MEDIUM, LOC_DEATH_SELF_GRENADE);
					bprint (PRINT_MEDIUM, "\n");
				}
				else if (targ.deathtype == "rocket")
				{
					bprint (PRINT_MEDIUM, LOC_DEATH_SELF_ROCKET);
					bprint (PRINT_MEDIUM, "\n");
				}
				else if (targ.deathtype == "discharge")
				{
					if (targ.watertype == CONTENT_SLIME)
						bprint (PRINT_MEDIUM, LOC_DEATH_DISCHARGE_SLIME);

					else if (targ.watertype == CONTENT_LAVA)
						bprint (PRINT_MEDIUM, LOC_DEATH_DISCHARGE_LAVA);
					else
						bprint (PRINT_MEDIUM, LOC_DEATH_DISCHARGE_WATER);

					bprint (PRINT_MEDIUM, "\n");
					return;
				}
				else {
					bprint (PRINT_MEDIUM, LOC_DEATH_SELF_OTHER);
					bprint (PRINT_MEDIUM, "\n");
				}
				return;
			}

			else if ( (teamplay) && (targteam == attackerteam) && on_team )	// gb
			{
				if (rnum < 0.25)
					deathstring = LOC_TEAMKILL_1;

				else if (rnum < 0.50)
					deathstring = LOC_TEAMKILL_2;

				else if (rnum < 0.75)
					deathstring = LOC_TEAMKILL_3;

				else
					deathstring = LOC_TEAMKILL_4;

				bprint (PRINT_MEDIUM, attacker.netname);
				bprint (PRINT_MEDIUM, deathstring);
				bprint (PRINT_MEDIUM, "\n");
				attacker.frags = attacker.frags - 1;
				//ZOID 12-13-96:  killing a teammate logs as suicide
				logfrag (attacker, attacker);
				return;
			}

			else
			{
				logfrag (attacker, targ);
				attacker.frags = attacker.frags + 1;

				attacker_weapon = attacker.weapon;

				// Axe
				if (targ.deathtype == "axe")
				{
					deathstring = LOC_DEATH_AXE_1A;
					deathstring2 = LOC_DEATH_AXE_1B;

#ifdef __LIBREQUAKE__
					if (attacker.super_damage_finished > 0) {
						deathstring = LOC_DEATH_AXE_QA;
						deathstring2 = LOC_DEATH_AXE_QB;
					}
					else if (random() < 0.01) {
						deathstring = LOC_DEATH_AXE_2A;
						deathstring2 = LOC_DEATH_AXE_2B;
					}
#endif
				}

				// Shotgun
				else if (targ.deathtype == "shotgun")
				{
					deathstring = LOC_DEATH_SHOTGUN_1A;
					deathstring2 = LOC_DEATH_SHOTGUN_1B;

#ifdef __LIBREQUAKE__
					if (attacker.super_damage_finished > 0) {
						deathstring = LOC_DEATH_SHOTGUN_QA;
						deathstring2 = LOC_DEATH_SHOTGUN_QB;
					}
					else if (random() < 0.01) {
						deathstring = LOC_DEATH_SHOTGUN_2A;
						deathstring2 = LOC_DEATH_SHOTGUN_2B;
					}
#endif
				}

				// Super Shotgun
				else if (targ.deathtype == "supershotgun")
				{
					deathstring = LOC_DEATH_SUPER_SHOTGUN_1A;
					deathstring2 = LOC_DEATH_SUPER_SHOTGUN_1B;

#ifdef __LIBREQUAKE__
					if (attacker.super_damage_finished > 0) {
						deathstring = LOC_DEATH_SUPER_SHOTGUN_QA;
						deathstring2 = LOC_DEATH_SUPER_SHOTGUN_QB;
					}
					else if (random() < 0.01) {
						deathstring = LOC_DEATH_SUPER_SHOTGUN_2A;
						deathstring2 = LOC_DEATH_SUPER_SHOTGUN_2B;
					}
#endif
				}

				// Nailgun
				else if (targ.deathtype == "nail")
				{
					deathstring = LOC_DEATH_NAILGUN_1A;
					deathstring2 = LOC_DEATH_NAILGUN_1B;

#ifdef __LIBREQUAKE__
					if (attacker.super_damage_finished > 0) {
						deathstring = LOC_DEATH_NAILGUN_QA;
						deathstring2 = LOC_DEATH_NAILGUN_QB;
					}
					else if (random() < 0.01) {
						deathstring = LOC_DEATH_NAILGUN_2A;
						deathstring2 = LOC_DEATH_NAILGUN_2B;
					}
#endif
				}

				// Super Nailgun
				else if (targ.deathtype == "supernail")
				{
					deathstring = LOC_DEATH_SUPER_NAILGUN_1A;
					deathstring2 = LOC_DEATH_SUPER_NAILGUN_1B;

#ifdef __LIBREQUAKE__
					if (attacker.super_damage_finished > 0) {
						deathstring = LOC_DEATH_SUPER_NAILGUN_QA;
						deathstring2 = LOC_DEATH_SUPER_NAILGUN_QB;
					}
					else if (random() < 0.01) {
						deathstring = LOC_DEATH_SUPER_NAILGUN_2A;
						deathstring2 = LOC_DEATH_SUPER_NAILGUN_2B;
					}
#endif
				}

				// Grenade Launcher
				else if (targ.deathtype == "grenade")
				{
					deathstring = LOC_DEATH_GRENADE_LAUNCHER_1A;
					deathstring2 = LOC_DEATH_GRENADE_LAUNCHER_1B;

#ifdef __LIBREQUAKE__
					if (attacker.super_damage_finished > 0) {
						deathstring = LOC_DEATH_GRENADE_LAUNCHER_QA;
						deathstring2 = LOC_DEATH_GRENADE_LAUNCHER_QB;
					}
					else if (targ.health < -40) {
						deathstring = LOC_DEATH_GRENADE_LAUNCHER_GA;
						deathstring2 = LOC_DEATH_GRENADE_LAUNCHER_GB;
					}
					else if (random() < 0.01) {
						deathstring = LOC_DEATH_GRENADE_LAUNCHER_2A;
						deathstring2 = LOC_DEATH_GRENADE_LAUNCHER_2B;
					}
#else
					if (targ.health < -40) {
						deathstring = LOC_DEATH_GRENADE_LAUNCHER_GA;
						deathstring2 = LOC_DEATH_GRENADE_LAUNCHER_GB;
					}
#endif
				}

				// Rocket Launcher
				else if (targ.deathtype == "rocket")
				{
					deathstring = LOC_DEATH_ROCKET_LAUNCHER_1A;
					deathstring2 = LOC_DEATH_ROCKET_LAUNCHER_1B;

#ifdef __LIBREQUAKE__
					if (attacker.super_damage_finished > 0) {
						deathstring = LOC_DEATH_ROCKET_LAUNCHER_Q1A;
						deathstring2 = LOC_DEATH_ROCKET_LAUNCHER_Q1B;
					}
					else if (targ.health < -40) {
						deathstring = LOC_DEATH_ROCKET_LAUNCHER_GA;
						deathstring2 = LOC_DEATH_ROCKET_LAUNCHER_GB;
					}
					else if (random() < 0.01) {
						deathstring = LOC_DEATH_ROCKET_LAUNCHER_2A;
						deathstring2 = LOC_DEATH_ROCKET_LAUNCHER_2B;
					}
#else
					if (targ.health < -40) {
						if (attacker.super_damage_finished > 0) {
							rnum = random();
							if (rnum < 0.3) {
								deathstring = LOC_DEATH_ROCKET_LAUNCHER_Q1A;
								deathstring2 = LOC_DEATH_ROCKET_LAUNCHER_Q1B;
							}
							else if (rnum < 0.6) {
								deathstring = LOC_DEATH_ROCKET_LAUNCHER_Q2A;
								deathstring2 = LOC_DEATH_ROCKET_LAUNCHER_Q2B;
							}
							else {
								// This one flips the order of attacker and target
								bprint (PRINT_MEDIUM, attacker.netname);
								bprint (PRINT_MEDIUM, LOC_DEATH_ROCKET_LAUNCHER_Q3A);
								bprint (PRINT_MEDIUM, targ.netname);
								bprint (PRINT_MEDIUM, LOC_DEATH_ROCKET_LAUNCHER_Q3B);
								bprint (PRINT_MEDIUM, "\n");
								return;
							}
						}
						else 
						{
							deathstring = LOC_DEATH_ROCKET_LAUNCHER_GA;
							deathstring2 = LOC_DEATH_ROCKET_LAUNCHER_GB;
						}
					}
#endif
				}

				// Lightning Gun
				else if (targ.deathtype == "lightning") {
					deathstring = LOC_DEATH_LIGHTNING_1A;
					deathstring2 = LOC_DEATH_LIGHTNING_1B;

#ifdef __LIBREQUAKE__
					if (attacker.super_damage_finished > 0) {
						deathstring = LOC_DEATH_LIGHTNING_QA;
						deathstring2 = LOC_DEATH_LIGHTNING_QB;
					}
					else if (random() < 0.01) {
						deathstring = LOC_DEATH_LIGHTNING_2A;
						deathstring2 = LOC_DEATH_LIGHTNING_2B;
					}
#endif
				}

				// Lightning Gun Discharge
				else if (targ.deathtype == "discharge") {
					deathstring = LOC_DEATH_LIGHTNING_DA;
					deathstring2 = LOC_DEATH_LIGHTNING_DB;
				}

				// Unknown Cause
				else {
					deathstring = LOC_DEATH_KILL;
					deathstring2 = LOC_DEATH_KILL;
				}

				bprint (PRINT_MEDIUM, targ.netname);
				bprint (PRINT_MEDIUM, deathstring);
				bprint (PRINT_MEDIUM, attacker.netname);
				bprint (PRINT_MEDIUM, deathstring2);
				bprint (PRINT_MEDIUM, "\n");
			}
			return;
		}
		else
		{
			logfrag (targ, targ);
			targ.frags = targ.frags - 1;		// killed self
			bprint (PRINT_MEDIUM, targ.netname);

			if (attacker.solid == SOLID_BSP && attacker != world)
			{
				bprint (PRINT_MEDIUM, LOC_DEATH_SQUISH);
				bprint (PRINT_MEDIUM, "\n");
				return;
			}

			if (targ.deathtype == "falling")
			{
				targ.deathtype = string_null;
				
#ifdef __LIBREQUAKE__

				if (random() < 0.01)
					bprint(PRINT_MEDIUM, LOC_DEATH_FALL2);
				else
					bprint(PRINT_MEDIUM, LOC_DEATH_FALL1);

#else

				bprint(PRINT_MEDIUM, LOC_DEATH_FALL);

#endif // __LIBREQUAKE__

				bprint(PRINT_MEDIUM, "\n");
				return;
			}

			if (targ.deathtype == "drowning")
			{
				rnum = random();

				if (rnum < 0.5) {
					bprint (PRINT_MEDIUM, LOC_DEATH_DROWN1);
					bprint (PRINT_MEDIUM, "\n");
				} else {
					bprint (PRINT_MEDIUM, LOC_DEATH_DROWN2);
					bprint (PRINT_MEDIUM, "\n");
				}

				return;
			}

			if (targ.deathtype == "slime")
			{
				if (random() < 0.5) {
					bprint (PRINT_MEDIUM, LOC_DEATH_SLIME1);
					bprint (PRINT_MEDIUM, "\n");
				}
				else {
					bprint (PRINT_MEDIUM, LOC_DEATH_SLIME2);
					bprint (PRINT_MEDIUM, "\n");
				}
				return;
			}

			if (targ.deathtype == "lava")
			{
				if (targ.health < -15)
				{
					bprint (PRINT_MEDIUM, LOC_DEATH_LAVA3);
					bprint (PRINT_MEDIUM, "\n");
					return;
				}

				if (random() < 0.5) {
					bprint (PRINT_MEDIUM, LOC_DEATH_LAVA1);
					bprint (PRINT_MEDIUM, "\n");
				}
				else {
					bprint (PRINT_MEDIUM, LOC_DEATH_LAVA2);
					bprint (PRINT_MEDIUM, "\n");
				}
				return;
			}

			//FIXME string_nul ??? maybe not necessary	//gnounc
			// yes, a null-check makes sense here       //SavageX
			if(attacker.killstring != string_null)
			{//gnounc
				bprint (PRINT_MEDIUM, attacker.killstring);
				bprint (PRINT_MEDIUM, "\n"); // Added since killstrings in LOC don't have \n	// ZungryWare
				return;
			}

			bprint (PRINT_MEDIUM, LOC_DEATH_OTHER);
			bprint (PRINT_MEDIUM, "\n");
		}
	}
};
