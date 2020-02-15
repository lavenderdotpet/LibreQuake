//Localization file
//This defines all of the text that is displayed to the player.
//Simply change the strings at the end of each line and recompile the progs to change what the text is in-game.

//Epilogue Texts
#define LOC_EPILOGUE_1 "This is the epilogue text for Episode 1.\nReplace it around line 5 of localization.qc.\nUse \\n to denote a new line."
#define LOC_EPILOGUE_1_FREEWARE "This is the epilogue text for the unregistered Episode 1.\nReplace it around line 5 of localization.qc.\nUse \\n to denote a new line."
#define LOC_EPILOGUE_2 "This is the epilogue text for Episode 2.\nReplace it around line 5 of localization.qc.\nUse \\n to denote a new line."
#define LOC_EPILOGUE_3 "This is the epilogue text for Episode 3.\nReplace it around line 5 of localization.qc.\nUse \\n to denote a new line."
#define LOC_EPILOGUE_4 "This is the epilogue text for Episode 4.\nReplace it around line 5 of localization.qc.\nUse \\n to denote a new line."
#define LOC_EPILOGUE_RUNES "This is the epilogue text that plays\nonce you have collected all four runes.\nReplace it around line 5 of localization.qc.\nUse \\n to denote a new line."
#define LOC_EPILOGUE_FINALE "This is the epilogue text that plays\nonce you have beaten the game.\nReplace it around line 5 of localization.qc.\nUse \\n to denote a new line."

//Server connection
//Note that the leading space is required.
//If you don't include it, there will be no space between the player's name and the rest of the text.
#define LOC_JOIN		" joined the match"
#define LOC_EXIT		" reached the exit"
#define LOC_EXIT_DM_A	" exited the match with "
#define LOC_EXIT_DM_B	" frags"
#define LOC_FULL		"All slots full. Selecting spawn point at random."

//User interface
#define LOC_NO_WEAPON	"You don't have that weapon"
#define LOC_NO_AMMO		"Out of ammo"

//Item collection
#define LOC_PICKUP			"You got "
#define LOC_PICKUP_HEALTH	"You receive "
#define LOC_LOST			" dropped "
#define LOC_RECOVER_A		" stole "
#define LOC_RECOVER_B		" ("
#define LOC_RECOVER_C		" seconds left.)"
#define LOC_BACKPACK		" from a backpack"
#define LOC_BONUS			" is coming for you all!!!"
#define LOC_HEALTH			" health"
#define LOC_HEALTH_BACKPACK	" health from a backpack"
#define LOC_ARMOR			" armor"

//Item names
#define LOC_QUAD_FADE	"The Crusher Sigil's power is dwindling"
#define LOC_OCT_FADE	"The Ultra-Mega-Crusher Sigil's power is dwindling"
#define LOC_PENT_FADE	"Lucifer's Aegis is almost gone!"
#define LOC_RING_FADE	"The Eye of Eryx is fading away"
#define LOC_BIO_FADE	"Your Hazmat Suit is about to expire"

#define LOC_NETNAME_QUAD	"the Crusher Sigil!"
#define LOC_NETNAME_OCT		"the Ultra-Mega-Crusher Sigil!"
#define LOC_NETNAME_PENT	"Lucifer's Aegis"
#define LOC_NETNAME_RING	"The Eye of Eryx"
#define LOC_NETNAME_BIO		"the Hazmat Suit"

#define LOC_NETNAME_AXE					"the Hammer"
#define LOC_NETNAME_SHOTGUN				"the Shotgun"
#define LOC_NETNAME_SUPER_SHOTGUN		"the Super Shotgun"
#define LOC_NETNAME_NAILGUN				"the Nailgun"
#define LOC_NETNAME_SUPER_NAILGUN		"the Super Nailgun"
#define LOC_NETNAME_GRENADE_LAUNCHER	"the Grenade Launcher"
#define LOC_NETNAME_ROCKET_LAUNCHER		"the Rocket Launcher"
#define LOC_NETNAME_LIGHTNING			"the Thunder Cannon"
#define LOC_NETNAME_RAILGUN				"the Railgun"

#define LOC_NETNAME_SHELLS	"shells"
#define LOC_NETNAME_NAILS	"nails"
#define LOC_NETNAME_ROCKETS	"rockets"
#define LOC_NETNAME_CELLS	"cells"

#define LOC_NETNAME_SILVER_KEY		"the silver key"
#define LOC_NETNAME_GOLD_KEY		"the gold key"
#define LOC_NETNAME_SILVER_RUNEKEY	"the silver runekey"
#define LOC_NETNAME_GOLD_RUNEKEY	"the gold runekey"
#define LOC_NETNAME_SILVER_KEYCARD	"the silver keycard"
#define LOC_NETNAME_GOLD_KEYCARD	"the gold keycard"
#define LOC_KEY_NEED				"You need "

//Misc. entity messages
#define LOC_COUNTER_COUNT_1A	""
#define LOC_COUNTER_COUNT_1B	" more to go..."
#define LOC_COUNTER_COUNT_2		"There are more to go..."
#define LOC_COUNTER_COMPLETE	"Sequence finished!"
#define LOC_SECRET				"You have discovered a secret!"
#define LOC_RUNE_YOU			"You"
#define LOC_RUNE_1				" got the rune of Duality!"
#define LOC_RUNE_2				" got the rune of Trickery!"
#define LOC_RUNE_3				" got the rune of Sorrow!"
#define LOC_RUNE_4				" got the rune of Revelation!"

//Domination mode messages
#define LOC_DOM_TAKE			" captured rune "

//Monster death messages
#define LOC_DEATH_ARMY 			" was killed by a Foot Soldier"
#define LOC_DEATH_ENFORCER 		" was eliminated by a Commando"
#define LOC_DEATH_DOG 			" was bitten by a Hellhound"
#define LOC_DEATH_OGRE 			" was obliterated by a Deep One"
#define LOC_DEATH_DEMON1 		" was slaughtered by a Moon Beast"
#define LOC_DEATH_WIZARD 		" was killed by a ???"
#define LOC_DEATH_ZOMBIE		" was cursed by a Husk"
#define LOC_DEATH_KNIGHT 		" was sliced by a Venusian Lizard Man"
#define LOC_DEATH_HELL_KNIGHT 	" was killed by a ???"
#define LOC_DEATH_FISH 			" was killed by a ???"
#define LOC_DEATH_SHAMBLER 		" was killed by a ???"
#define LOC_DEATH_SHALRATH 		" was killed by a ???"
#define LOC_DEATH_TARBABY 		" was absorbed by an Ooze"
#define LOC_DEATH_BOSS 			" was killed by a ???"
#define LOC_DEATH_OLDONE 		" was magicked by Abhoth"
#define LOC_DEATH_MONSTER		" was slain by some abomnination"

//Environmental and Misc. death messages
#define LOC_DEATH_EXPLO_BOX 	" was detonated by an explosive crate"
#define LOC_DEATH_SQUISH 		" was crushed"
#define LOC_DEATH_SQUISH2 		" was crushed by "
#define LOC_DEATH_FIREBAR	 	" was burned by a fire bar"
#define LOC_DEATH_TRAP_SPIKE	" was shot by a spike turret"
#define LOC_DEATH_TRAP_LASER	" was shot by a laser turret"
#define LOC_DEATH_TRAP_ROCKET 	" was blasted by a rocket turret"
#define LOC_DEATH_TRAP_GRENADE 	" was blasted by a grenade turret"
#define LOC_DEATH_FIREBALL		" was hit by a ball of lava"
#define LOC_DEATH_LEAVE			" tried to escape the arena"
#define LOC_DEATH_DROWN1		" ran out of air"
#define LOC_DEATH_DROWN2		" drowned"
#define LOC_DEATH_DROWN3		" fell to a watery grave"
#define LOC_DEATH_SLIME1		" shouldn't have played with acid"
#define LOC_DEATH_SLIME2		" was burned by the acid"
#define LOC_DEATH_LAVA1			" combusted"
#define LOC_DEATH_LAVA2			" felt the heat"
#define LOC_DEATH_LAVA3			" shouldn't have played with lava"
#define LOC_DEATH_FALL_1		" fell off a cliff"
#define LOC_DEATH_FALL_2		" took a long flight off a short runway"
#define LOC_DEATH_SPACE_1		" fell into space"
#define LOC_DEATH_SPACE_2		"'s screams went unheard"
#define LOC_DEATH_VOID_1		" fell into the void"
#define LOC_DEATH_VOID_2		" fell out of existence"
#define LOC_DEATH_DISCHARGE_1	" mixed water with electricity"
#define LOC_DEATH_DISCHARGE_2	" took a toaster bath"
#define LOC_DEATH_DISCHARGE_3	" shouldn't have played with electricity"
#define LOC_DEATH_SELF_GRENADE	" wasn't careful with explosives"
#define LOC_DEATH_SELF_ROCKET	" blew himself up"
#define LOC_DEATH_SELF_OTHER	" had a death-wish"
#define LOC_DEATH_SUICIDE		" commited suicide"
#define LOC_DEATH_OTHER			" died"

//Multiplayer death messages
//Deathstring 1 is the standard one
//Deathstring 2 has a 1/33 chance to be used instead
//Deathstring G is used for when the victim was gibbed (Grenade Launcher and Rocket Launcher only)
//Deathstring Q is used if the attacker had a Quad Damage
//Deathstring D1 is used if the attack was a discharge (Lightning Gun only)
//Deathstring D2 has a 1/33 chance to be used instead (Lightning Gun only)
//The format for printing is: victim name, deathstring A, attacker name, deathstring B
#define LOC_DEATH_AXE_1A	" was brutally beaten by "
#define LOC_DEATH_AXE_1B	"'s Hammer"
#define LOC_DEATH_AXE_2A	" was savagely beaten by "
#define LOC_DEATH_AXE_2B	"'s Hammer"
#define LOC_DEATH_AXE_QA	"'s bucket was kicked by "
#define LOC_DEATH_AXE_QB	""

#define LOC_DEATH_SHOTGUN_1A	" sucked on "
#define LOC_DEATH_SHOTGUN_1B	"'s muffler"
#define LOC_DEATH_SHOTGUN_2A	" nibbled on "
#define LOC_DEATH_SHOTGUN_2B	"'s muffler"
#define LOC_DEATH_SHOTGUN_QA	" was put six feet under by "
#define LOC_DEATH_SHOTGUN_QB	""

#define LOC_DEATH_SUPER_SHOTGUN_1A	" was blasted by "
#define LOC_DEATH_SUPER_SHOTGUN_1B	"'s Super Shotgun"
#define LOC_DEATH_SUPER_SHOTGUN_2A	" was eliminated by "
#define LOC_DEATH_SUPER_SHOTGUN_2B	"'s Super Shotgun"
#define LOC_DEATH_SUPER_SHOTGUN_QA	" was sent home in a box by "
#define LOC_DEATH_SUPER_SHOTGUN_QB	""

#define LOC_DEATH_NAILGUN_1A	" was pierced by "
#define LOC_DEATH_NAILGUN_1B	"'s Nailgun"
#define LOC_DEATH_NAILGUN_2A	" was perforated by "
#define LOC_DEATH_NAILGUN_2B	"'s Nailgun"
#define LOC_DEATH_NAILGUN_QA	" was sent beyond the veil by "
#define LOC_DEATH_NAILGUN_QB	""

#define LOC_DEATH_SUPER_NAILGUN_1A	" was gunned down by "
#define LOC_DEATH_SUPER_NAILGUN_1B	"'s Super Nailgun"
#define LOC_DEATH_SUPER_NAILGUN_2A	" was hunted down by "
#define LOC_DEATH_SUPER_NAILGUN_2B	"'s Super Nailgun"
#define LOC_DEATH_SUPER_NAILGUN_QA	"'s chips were cashed by "
#define LOC_DEATH_SUPER_NAILGUN_QB	""

#define LOC_DEATH_GRENADE_LAUNCHER_1A	" tripped over "
#define LOC_DEATH_GRENADE_LAUNCHER_1B	"'s grenade"
#define LOC_DEATH_GRENADE_LAUNCHER_2A	" landed on "
#define LOC_DEATH_GRENADE_LAUNCHER_2B	"'s grenade"
#define LOC_DEATH_GRENADE_LAUNCHER_GA	" was torn asunder by "
#define LOC_DEATH_GRENADE_LAUNCHER_GB	"'s grenade"
#define LOC_DEATH_GRENADE_LAUNCHER_QA	"'s clock was cleaned by "
#define LOC_DEATH_GRENADE_LAUNCHER_QB	""

#define LOC_DEATH_ROCKET_LAUNCHER_1A	" was slammed by "
#define LOC_DEATH_ROCKET_LAUNCHER_1B	"'s rocket"
#define LOC_DEATH_ROCKET_LAUNCHER_2A	" was shattered by "
#define LOC_DEATH_ROCKET_LAUNCHER_2B	"'s rocket"
#define LOC_DEATH_ROCKET_LAUNCHER_GA	" was blasted apart by "
#define LOC_DEATH_ROCKET_LAUNCHER_GB	"'s rocket"
#define LOC_DEATH_ROCKET_LAUNCHER_Q1A	" rode "
#define LOC_DEATH_ROCKET_LAUNCHER_Q1B	"'s pale horse"
#define LOC_DEATH_ROCKET_LAUNCHER_Q2A	" rode "
#define LOC_DEATH_ROCKET_LAUNCHER_Q2B	"'s pale horse"
#define LOC_DEATH_ROCKET_LAUNCHER_Q3A	" rode "
#define LOC_DEATH_ROCKET_LAUNCHER_Q3B	"'s pale horse"

#define LOC_DEATH_LIGHTNING_1A	" was fried by "
#define LOC_DEATH_LIGHTNING_1B	"'s Thunder Cannon"
#define LOC_DEATH_LIGHTNING_2A	" was volt-charged by "
#define LOC_DEATH_LIGHTNING_2B	"'s Thunder Cannon"
#define LOC_DEATH_LIGHTNING_QA	" took "
#define LOC_DEATH_LIGHTNING_QB	"'s last train to glory"
#define LOC_DEATH_LIGHTNING_D1A	" was given shock treatment by "
#define LOC_DEATH_LIGHTNING_D1B	""
#define LOC_DEATH_LIGHTNING_D2A	" was given a toaster bath by "
#define LOC_DEATH_LIGHTNING_D2B	""

#define LOC_DEATH_RAILGUN_1A	" was picked off by "
#define LOC_DEATH_RAILGUN_1B	"'s Railgun"
#define LOC_DEATH_RAILGUN_2A	" was taken out by "
#define LOC_DEATH_RAILGUN_2B	"'s Railgun"
#define LOC_DEATH_RAILGUN_QA	"'s Plug was Pulled by "
#define LOC_DEATH_RAILGUN_QB	""

//More Multiplayer death messages
#define LOC_DEATH_TELEFRAG_A	" was teleported into by "
#define LOC_DEATH_TELEFRAG_B	""

#define LOC_DEATH_DEFLECT_A ""
#define LOC_DEATH_DEFLECT_B	"'s telefrag on "
#define LOC_DEATH_DEFLECT_C	" was deflected by Lucifer's influence"

#define LOC_TEAMKILL_1	" kills a teammate"
#define LOC_TEAMKILL_2	" invokes friendly-fire"
#define LOC_TEAMKILL_3	" should really apologize"
#define LOC_TEAMKILL_4	" doesn't know what team he's on"
#define LOC_TEAMKILL_5	" got a teammate crushed"









