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
    if (deathmatch && stof(infokey(world, "buffed_axe")) != 0)
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
    
    if (deathmatch && stof(infokey(world, "have_axe_only")) != 0)
        return TRUE;
#endif
    return FALSE;
}

// Shotgun is removed from players' starting items
float() deathmatch_no_shotgun =
{
#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "disable_shotgun")) != 0)
        return TRUE;
#endif
    return FALSE;
}

// Super Shotgun is removed from players' starting items
float() deathmatch_no_super_shotgun =
{
#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "disable_super_shotgun")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Nailgun is removed from players' starting items
float() deathmatch_no_nailgun =
{
#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "disable_nailgun")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Super Nailgun is removed from players' starting items
float() deathmatch_no_super_nailgun =
{
#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "disable_super_nailgun")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Grenade Launcher is removed from players' starting items
float() deathmatch_no_grenade_launcher =
{
#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "disable_grenade_launcher")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Rocket Launcher is removed from players' starting items
float() deathmatch_no_rocket_launcher =
{
#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "disable_rocket_launcher")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Lightning Gun is removed from players' starting items
float() deathmatch_no_lightning_gun =
{
#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "disable_lightning_gun")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Players start with the Super Shotgun
float() deathmatch_starting_super_shotgun =
{
    if (deathmatch_no_super_shotgun())
        return FALSE;
    
    if (deathmatch_supermode() || deathmatch_supermode2())
        return TRUE;
    
#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "have_super_shotgun")) != 0)
        return TRUE;
#endif
    return FALSE;
}

// Players start with the Super Nailgun
float() deathmatch_starting_nailgun =
{
    if (deathmatch_no_nailgun())
        return FALSE;
    
    if (deathmatch_supermode() || deathmatch_supermode2())
        return TRUE;
    
#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "have_nailgun")) != 0)
        return TRUE;
#endif
    return FALSE;
}

// Players start with the Super Nailgun
float() deathmatch_starting_super_nailgun =
{
    if (deathmatch_no_super_nailgun())
        return FALSE;
    
    if (deathmatch_supermode() || deathmatch_supermode2())
        return TRUE;
    
#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "have_super_nailgun")) != 0)
        return TRUE;
#endif
    return FALSE;
}

// Players start with the Grenade Launcher
float() deathmatch_starting_grenade_launcher =
{
    if (deathmatch_no_grenade_launcher())
        return FALSE;

    if (deathmatch_supermode2())
        return TRUE;
    
#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "have_grenade_launcher")) != 0)
        return TRUE;
#endif
    return FALSE;
}

// Players start with the Rocket Launcher
float() deathmatch_starting_rocket_launcher =
{
    if (deathmatch_no_rocket_launcher())
        return FALSE;
    
    if (deathmatch_supermode() || deathmatch_supermode2())
        return TRUE;
    
#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "have_rocket_launcher")) != 0)
        return TRUE;
#endif
    return FALSE;
}

// Players start with the Lightning Gun
float() deathmatch_starting_lightning_gun =
{
    if (deathmatch_no_lightning_gun())
        return FALSE;
    
    if (deathmatch_supermode() || deathmatch_supermode2())
        return TRUE;
    
#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "have_lightning_gun")) != 0)
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
    if (deathmatch && stof(infokey(world, "have_unlimited_ammo")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Super Shotgun is removed on map load
float() deathmatch_no_super_shotgun_on_map =
{
    if (deathmatch_no_super_shotgun())
        return TRUE;
    
    if (deathmatch_starting_super_shotgun())
        return TRUE;

    return FALSE;
};

// Nailgun is removed from players' starting items
float() deathmatch_no_nailgun_on_map =
{
    if (deathmatch_no_nailgun())
        return TRUE;
    
    if (deathmatch_starting_nailgun())
        return TRUE;

    return FALSE;
};

// Super Nailgun is removed from players' starting items
float() deathmatch_no_super_nailgun_on_map =
{
    if (deathmatch_no_super_nailgun())
        return TRUE;
    
    if (deathmatch_starting_super_nailgun())
        return TRUE;

    return FALSE;
};

// Grenade Launcher is removed from players' starting items
float() deathmatch_no_grenade_launcher_on_map =
{
    if (deathmatch_no_grenade_launcher())
        return TRUE;
    
    if (deathmatch_starting_grenade_launcher())
        return TRUE;

    return FALSE;
};

// Rocket Launcher is removed from players' starting items
float() deathmatch_no_rocket_launcher_on_map =
{
    if (deathmatch_no_rocket_launcher())
        return TRUE;
    
    if (deathmatch_starting_rocket_launcher())
        return TRUE;

    return FALSE;
};

// Lightning Gun is removed from players' starting items
float() deathmatch_no_lightning_gun_on_map =
{
    if (deathmatch_no_lightning_gun())
        return TRUE;
    
    if (deathmatch_starting_lightning_gun())
        return TRUE;

    return FALSE;
};

// Weapons are removed on map load
float() deathmatch_no_weapons_on_map =
{
    if (deathmatch_supermode() || deathmatch_supermode2() || deathmatch_axe_only())
        return TRUE;

#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "disable_weapons")) != 0)
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
    if (deathmatch && stof(infokey(world, "disable_ammo")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Shell pickups are removed on map load
float() deathmatch_no_shell_pickups =
{
    if (deathmatch_no_ammo_pickups())
        return TRUE;
    
    if (deathmatch_no_shotgun() && deathmatch_no_super_shotgun())
        return TRUE;
    
    if (deathmatch_no_weapons_on_map() && (!deathmatch_starting_super_shotgun()))
        return TRUE;

#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "disable_ammo_shells")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Nail pickups are removed on map load
float() deathmatch_no_nail_pickups =
{
    if (deathmatch_no_ammo_pickups())
        return TRUE;
    
    if (deathmatch_no_nailgun() && deathmatch_no_super_nailgun())
        return TRUE;
    
    if (deathmatch_no_weapons_on_map() && (!deathmatch_starting_nailgun()) && (!deathmatch_starting_super_nailgun()))
        return TRUE;

#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "disable_ammo_nails")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Rocket pickups are removed on map load
float() deathmatch_no_rocket_pickups =
{
    if (deathmatch_no_ammo_pickups())
        return TRUE;
    
    if (deathmatch_no_grenade_launcher() && deathmatch_no_rocket_launcher())
        return TRUE;
    
    if (deathmatch_no_weapons_on_map() && (!deathmatch_starting_grenade_launcher()) && (!deathmatch_starting_rocket_launcher()))
        return TRUE;

#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "disable_ammo_rockets")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Cell pickups are removed on map load
float() deathmatch_no_cell_pickups =
{
    if (deathmatch_no_ammo_pickups())
        return TRUE;
    
    if (deathmatch_no_lightning_gun())
        return TRUE;
    
    if (deathmatch_no_weapons_on_map() && (!deathmatch_starting_lightning_gun()))
        return TRUE;

#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "disable_ammo_cells")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Powerups are removed on map load
float() deathmatch_no_powerups =
{
#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "disable_powerups")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Armor pickups are removed on map load
float() deathmatch_no_armor =
{
#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "disable_armor")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Health pickups are removed on map load
float() deathmatch_no_health =
{
#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "disable_health")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Mega-health pickups are removed on map load
float() deathmatch_no_mega_health =
{
#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "disable_mega_health")) != 0)
        return TRUE;
#endif

    return FALSE;
};

// Stops players from dropping backpacks on death
float() deathmatch_no_backpacks =
{
#ifdef __QW__ // NQ does not support infokeys
    if (deathmatch && stof(infokey(world, "disable_backpacks")) != 0)
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
