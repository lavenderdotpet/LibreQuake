//Deathmatch settings

//For if weapons should stay instead of disappearing once picked up
float() weaponstay =
{
	if (deathmatch || coop)
	{
		if (deathmatch != 1 && deathmatch != 8)
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
	if (deathmatch == 8)
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
