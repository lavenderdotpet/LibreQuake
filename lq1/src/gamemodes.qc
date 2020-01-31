//Gamemode Settings

//Skill 3
float() nightmare = 
{
	if (skill == 3 && !(cvar("temp1") & SET_COPPERNIGHTMARE))
		return TRUE;
	else
		return FALSE;
}

//Skill 3 with copper settings
float() coppernightmare = 
{
	if (skill == 3 && cvar("temp1") & SET_COPPERNIGHTMARE)
		return TRUE;
	else
		return FALSE;
}

//For if weapons should stay instead of disappearing once picked up
float() weaponstay =
{
	if (deathmatch || coop)
	{
		if (deathmatch != 1)
		{
			return 1;
		}
	}
	return 0;
};

//Items don't respawn in deathmatch 2
float() itemrespawn =
{
	if (deathmatch && deathmatch != 2)
	{
		return 1;
	}
	else
	{
		return 0;
	}
};

//For deathmatch 1, which uses the old ammo respawn time
float() slowammo =
{
	if (deathmatch == 1)
	{
		return 1;
	}
	else
	{
		return 0;
	}
};

//For deathmatch 4
//Starts each player off with every weapon and infinite ammo
float() supermode =
{
	if (deathmatch == 4)
	{
		return 1;
	}
	else
	{
		return 0;
	}
};

//For deathmatch 5
//Starts each player off with every weapon and a fair amount of ammo
float() supermode2 =
{
	if (deathmatch == 5)
	{
		return 1;
	}
	else
	{
		return 0;
	}
};

//Rebalances the weapons to play more like Quake III
float() arenamode =
{
	if (deathmatch == 8 || deathmatch == 9)
	{
		return 1;
	}
	else
	{
		return 0;
	}
};

//Disables powerups. Useful for 1v1 modes.
float() powerupdisable =
{
	//In duel and all odd-numbered modes above that, powerups are turned off.
	if (deathmatch == 6 || (deathmatch >= 7 && (deathmatch / 2) != floor(deathmatch / 2)))
	{
		return 1;
	}
	else
	{
		return 0;
	}
};

//Like duel, but the game resets everytime a player dies
float() lastmanstanding =
{
	if (deathmatch == 7)
	{
		return 1;
	}
	else
	{
		return 0;
	}
};

//Disables the Rocket Launcher and Lightning Gun
float() mediumweapons =
{
	if (deathmatch == 10 || deathmatch == 11)
	{
		return 1;
	}
	else
	{
		return 0;
	}
};

//Disables all weapons except for the Super Shotgun and Nailgun
float() weakweapons =
{
	if (deathmatch == 12 || deathmatch == 13)
	{
		return 1;
	}
	else
	{
		return 0;
	}
};
