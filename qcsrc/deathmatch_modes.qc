//
// deathmatch_modes.qc -- Centralized location for defining which deathmatch
// modes have which settings
//

float() deathmatch_weapon_stay =
{
    return deathmatch >= 2;
}

float() deathmatch_item_respawn =
{
    return deathmatch && (deathmatch != 2);
}

float() deathmatch_classic =
{
    return deathmatch == 1;
}

float() deathmatch_supermode =
{
    return deathmatch == 4;
}

float() deathmatch_supermode2 =
{
    return deathmatch == 5;
}

float() deathmatch_no_powerups =
{
    return deathmatch == 6;
}
