//
// deathmatch_settings.qc -- Centralized location for defining which deathmatch
// settings are in which modes
//

// Weapons stay when picked up
#define deathmatch_weapon_stay() \
    (deathmatch >= 2)

// Items respawn after a timer
#define deathmatch_item_respawn() \
    (deathmatch && (deathmatch != 2))

// Ammo pickups take twice as long to respawn
#define deathmatch_slow_ammo() \
    (deathmatch == 1)

// When picking up a backpack that contains a Rocket or Grenade Launcher, set the
// player's rocket count to 5 if they have less than 5
#define deathmatch_backpack_min_rockets() \
    (deathmatch >= 3)

// All of the special rules that apply in deathmatch 4
#define deathmatch_supermode() \
    (deathmatch == 4)

// All of the special rules that apply in deathmatch 5
#define deathmatch_supermode2() \
    (deathmatch == 5)

// Increases the axe's damage from 20 to 75
float() deathmatch_buffed_axe =
{
    if (deathmatch_supermode() || deathmatch_supermode2())
        return TRUE;

#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "ba")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Restricts players to axes only
float() deathmatch_axe_only =
{
#ifdef __QW__ // NQ does not support infokeys
    // Legacy support for "axe" infokey that only works on deathmatch 4
    if (deathmatch_supermode() && stof(infokey(world, "axe")) != 0)
        return TRUE;
    
    if (deathmatch && stof(infokey(world, "ao")) != 0)
        return TRUE;
#endif
    return FALSE;
}

// Players have unlimited ammo
float() deathmatch_unlimited_ammo =
{
    if (deathmatch_supermode())
        return TRUE;

#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "ua")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Players start with some ammo
float() deathmatch_starting_ammo =
{
    if (deathmatch_supermode2())
        return TRUE;

#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "sa")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Weapons are removed on map load
float() deathmatch_no_weapons =
{
    if (deathmatch_supermode() || deathmatch_supermode2() || deathmatch_axe_only())
        return TRUE;

#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "nw")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Ammo pickups are removed on map load
float() deathmatch_no_ammo_pickups =
{
    if (deathmatch_unlimited_ammo() || deathmatch_axe_only())
        return TRUE;

#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "na")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Powerups are removed on map load
float() deathmatch_no_powerups =
{
#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "np")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Armor pickups are removed on map load
float() deathmatch_no_armor =
{
#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "nr")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Health pickups are removed on map load
float() deathmatch_no_health =
{
#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "nh")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Mega-health pickups are removed on map load
float() deathmatch_no_mega_health =
{
#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "nmh")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Quad is dropped on death
float() deathmatch_drop_quad =
{
    if (!deathmatch)
        return FALSE;

#ifdef __QW__ // NQ does not support infokeys
	return stof(infokey(world,"dq")) != 0;
#else
    return TRUE;
#endif
};

// Ring is dropped on death
float() deathmatch_drop_ring =
{
    if (!deathmatch)
        return FALSE;

#ifdef __QW__ // NQ does not support infokeys
	return stof(infokey(world,"dr")) != 0;
#else
    return TRUE;
#endif
};

// Multiplier for explosion force from rocket and grenade jumps
float() deathmatch_rocket_jump_multiplier =
{
    if (!deathmatch)
        return 0;

#ifdef __QW__ // NQ does not support infokeys
	return stof(infokey(world,"rj"));
#else
    return 0;
#endif
};
