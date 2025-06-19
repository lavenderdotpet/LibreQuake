/*  
	Copyright (C) 1996-1997  Id Software, Inc.
	Copyright (C) 2023 ZungryWare <zungrysoftentertainment@gmail.com>
	Copyright (C) 2024 Ivy Bowling <motolegacy@proton.me>

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

//
// localized_text.qc -- Centralized location for text that can be printed out
// during gameplay. Formerly localization.qc
//

/*==============================================================================

			EPISODE EPILOGUE STRINGS

		These strings in-engine have a 40 character limit before
		truncation.

==============================================================================*/

#ifdef __LIBREQUAKE__

#define LOC_EPILOGUE_0		"\nAs the ethereal essence of your very\nbeing drifts through time and space,\nyou experience relentless calm and\nserene determination. You embrace the\nliminal, formless nature of your\nexistence within the amorphous expanse\nbetween realities.\n\nSuspended between the veils of life\nand death, among the realm of celestial\ndissolution, you wait to be called upon\nagain. To regain your corporeal form\nand step into the crucible of fate.\nTo finish your task and keep at bay the\nonslaught of cosmic horrors.\n"
#define LOC_EPILOGUE_1		"Congratulations! You have beaten Episode 1 of LibreQuake!"
#define LOC_EPILOGUE_1_FREEWARE	LOC_EPILOGUE_1
#define LOC_EPILOGUE_2		"Congratulations! You have beaten Episode 2 of LibreQuake!"
#define LOC_EPILOGUE_3		"Congratulations! You have beaten Episode 3 of LibreQuake!"
#define LOC_EPILOGUE_4		"Congratulations! You have beaten Episode 4 of LibreQuake!"
#define LOC_EPILOGUE_RUNES	"You have collected all of the runes and may advance to the final map!"
#define LOC_EPILOGUE_FINALE	"Thanks for playing the beta version of LibreQuake!"

#else

#define LOC_EPILOGUE_1	"As the corpse of the monstrous entity\nChthon sinks back into the lava whence\nit rose, you grip the Rune of Earth\nMagic tightly. Now that you have\nconquered the Dimension of the Doomed,\nrealm of Earth Magic, you are ready to\ncomplete your task. A Rune of magic\npower lies at the end of each haunted\nland of Quake. Go forth, seek the\ntotality of the four Runes!"
#define LOC_EPILOGUE_1_FREEWARE	"As the corpse of the monstrous entity\nChthon sinks back into the lava whence\nit rose, you grip the Rune of Earth\nMagic tightly. Now that you have\nconquered the Dimension of the Doomed,\nrealm of Earth Magic, you are ready to\ncomplete your task in the other three\nhaunted lands of Quake. Or are you? If\nyou don't register Quake, you'll never\nknow what awaits you in the Realm of\nBlack Magic, the Netherworld, and the\nElder World!"
#define LOC_EPILOGUE_2	"The Rune of Black Magic throbs evilly in\nyour hand and whispers dark thoughts\ninto your brain. You learn the inmost\nlore of the Hell-Mother; Shub-Niggurath!\nYou now know that she is behind all the\nterrible plotting which has led to so\nmuch death and horror. But she is not\ninviolate! Armed with this Rune, you\nrealize that once all four Runes are\ncombined, the gate to Shub-Niggurath's\nPit will open, and you can face the\nWitch-Goddess herself in her frightful\notherworld cathedral."
#define LOC_EPILOGUE_3	"The charred viscera of diabolic horrors\nbubble viscously as you seize the Rune\nof Hell Magic. Its heat scorches your\nhand, and its terrible secrets blight\nyour mind. Gathering the shreds of your\ncourage, you shake the devil's shackles\nfrom your soul, and become ever more\nhard and determined to destroy the\nhideous creatures whose mere existence\nthreatens the souls and psyches of all\nthe population of Earth."
#define LOC_EPILOGUE_4	"Despite the awful might of the Elder\nWorld, you have achieved the Rune of\nElder Magic, capstone of all types of\narcane wisdom. Beyond good and evil,\nbeyond life and death, the Rune\npulsates, heavy with import. Patient and\npotent, the Elder Being Shub-Niggurath\nweaves her dire plans to clear off all\nlife from the Earth, and bring her own\nfoul offspring to our world! For all the\ndwellers in these nightmare dimensions\nare her descendants! Once all Runes of\nmagic power are united, the energy\nbehind them will blast open the Gateway\nto Shub-Niggurath, and you can travel\nthere to foil the Hell-Mother's plots\nin person."
#define LOC_EPILOGUE_RUNES	"Now, you have all four Runes. You sense\ntremendous invisible forces moving to\nunseal ancient barriers. Shub-Niggurath\nhad hoped to use the Runes Herself to\nclear off the Earth, but now instead,\nyou will use them to enter her home and\nconfront her as an avatar of avenging\nEarth-life. If you defeat her, you will\nbe remembered forever as the savior of\nthe planet. If she conquers, it will be\nas if you had never been born."
#define LOC_EPILOGUE_FINALE	"Congratulations and well done! You have\nbeaten the hideous Shub-Niggurath, and\nher hundreds of ugly changelings and\nmonsters. You have proven that your\nskill and your cunning are greater than\nall the powers of Quake. You are the\nmaster now. Id Software salutes you."

#endif // __LIBREQUAKE__

/*==============================================================================

			CLIENT & SERVER STATE STRINGS

==============================================================================*/

#ifdef __LIBREQUAKE__

#define LOC_CLIENT_JOIN				" joined the server"
#define LOC_CLIENT_EXIT_LEVEL		" exited the level"
#define LOC_CLIENT_DISCON_A			" left the server the game with "
#define LOC_CLIENT_DISCON_B			" frags"

#else

#define LOC_CLIENT_JOIN				" entered the game"
#define LOC_CLIENT_EXIT_LEVEL		" exited the level"
#define LOC_CLIENT_DISCON_A			" left the game with "
#define LOC_CLIENT_DISCON_B			" frags"

#endif // __LIBREQUAKE__

/*==============================================================================

			CLIENT WEAPON STATUS STRINGS

==============================================================================*/

#ifdef __LIBREQUAKE__

#define LOC_WEAPON_INVALID				"Invalid weapon"
#define LOC_WEAPON_NOAMMO				"Out of ammo"

#else

#define LOC_WEAPON_INVALID				"no weapon."
#define LOC_WEAPON_NOAMMO				"not enough ammo."

#endif // __LIBREQUAKE__

/*==============================================================================

			CLIENT ITEM COLLECTION STRINGS

==============================================================================*/

#define LOC_ITEM_PICKUP_NORMAL			"You got "
#define LOC_ITEM_PICKUP_HEALTH			"You receieve "
#define LOC_ITEM_PICKUP_ADD_HEALTH  	" additional health"

#define LOC_ITEM_FROM_BACKPACK			" from a backpack"  // Unused..

#define LOC_ITEM_TYPE_HEALTH			" health"
#define LOC_ITEM_TYPE_ARMOR				" armor"

#ifdef __LIBREQUAKE__

#define LOC_ITEM_NAME_QUADDMG			"the Crusher Sigil"
#define LOC_ITEM_NAME_OCTDMG			"the Demolisher Sigil"
#define LOC_ITEM_NAME_PENTPROT			"Lucifier's Protection"
#define LOC_ITEM_NAME_SHADRING			"the Eye of Enigma"
#define LOC_ITEM_NAME_BIOSUIT			"the Diving Suit"
#define LOC_ITEM_NAME_BACKPACK			"Backpack"

#define LOC_ITEM_FADE_QUADDMG			"Your Crusher Sigil is fading..."
#define LOC_ITEM_FADE_OCTDMG			"Your Demolisher Sigil is fading..."
#define LOC_ITEM_FADE_PENTPROT			"Lucifier's Protection is fading..."
#define LOC_ITEM_FADE_SHADRING			"The Eye of Enigma is fading..."
#define LOC_ITEM_FADE_BIOSUIT			"Air in Diving Suit is running out..."

#define LOC_BONUS_POWERS				" is coming for you all!!!"

#define LOC_ITEM_LOST_A					" lost "
#define LOC_ITEM_LOST_B					" with "
#define LOC_ITEM_LOST_C					" seconds left"

#else

#define LOC_ITEM_NAME_QUADDMG			"Quad Damage"
#define LOC_ITEM_NAME_OCTDMG			"OctaPower"
#define LOC_ITEM_NAME_PENTPROT			"Pentagram of Protection"
#define LOC_ITEM_NAME_SHADRING			"Ring of Shadows"
#define LOC_ITEM_NAME_BIOSUIT			"Biosuit"
#define LOC_ITEM_NAME_BACKPACK			"Backpack"

#define LOC_ITEM_FADE_QUADDMG			"Quad Damage is wearing off"
#define LOC_ITEM_FADE_OCTDMG			"OctaPower is wearing off"
#define LOC_ITEM_FADE_PENTPROT			"Protection is almost burned out"
#define LOC_ITEM_FADE_SHADRING			"Ring of Shadows magic is fading"
#define LOC_ITEM_FADE_BIOSUIT			"Air supply in Biosuit expiring"

#define LOC_BONUS_POWERS				" attains bonus powers!!!"

#define LOC_ITEM_LOST_A					" lost a "
#define LOC_ITEM_LOST_B					" with "
#define LOC_ITEM_LOST_C					" seconds remaining"

#endif // __LIBREQUAKE__

/*==============================================================================

			WEAPON AND AMMO STRINGS

==============================================================================*/

#ifdef __LIBREQUAKE__

#define LOC_WEAPON_NAME_AXE				"Axe"		// Unused..
#define LOC_WEAPON_NAME_SHOTGUN			"Shotgun"   // Unused..
#define LOC_WEAPON_NAME_SUPER_SHOTGUN   "Double-Barreled Shotgun"
#define LOC_WEAPON_NAME_NAILGUN			"Nailgun"
#define LOC_WEAPON_NAME_SUPER_NAILGUN   "Super Nailgun"
#define LOC_WEAPON_NAME_GRENADE_LAUNCH  "Grenade Launcher"
#define LOC_WEAPON_NAME_ROCKET_LAUNCH   "Rocket Launcher"
#define LOC_WEAPON_NAME_THUNDERBOLT		"Lightning Gun"

#else

#define LOC_WEAPON_NAME_AXE				"Axe"	// Unused..
#define LOC_WEAPON_NAME_SHOTGUN			"Shotgun"   // Unused..
#define LOC_WEAPON_NAME_SUPER_SHOTGUN   "Double-barrelled Shotgun"
#define LOC_WEAPON_NAME_NAILGUN			"nailgun"
#define LOC_WEAPON_NAME_SUPER_NAILGUN   "Super Nailgun"
#define LOC_WEAPON_NAME_GRENADE_LAUNCH  "Grenade Launcher"
#define LOC_WEAPON_NAME_ROCKET_LAUNCH   "Rocket Launcher"
#define LOC_WEAPON_NAME_THUNDERBOLT		"Thunderbolt"

#endif // __LIBREQUAKE__

#define LOC_WEAPON_AMMO_SHELLS			"shells"
#define LOC_WEAPON_AMMO_NAILS			"nails"
#define LOC_WEAPON_AMMO_ROCKETS			"rockets"
#define LOC_WEAPON_AMMO_CELLS			"cells"

/*==============================================================================

			KEY STRINGS

==============================================================================*/

#ifdef __LIBREQUAKE__

#define LOC_KEY_NAME_SILVER				"Silver Key"
#define LOC_KEY_NAME_SILVER_RUNE		"Silver Key"
#define LOC_KEY_NAME_SILVER_CARD		"Silver Keycard"
#define LOC_KEY_NAME_GOLD				"Gold Key"
#define LOC_KEY_NAME_GOLD_RUNE			"Gold Key"
#define LOC_KEY_NAME_GOLD_CARD			"Gold Keycard"
#define LOC_KEY_NEED					"You need "

#else

#define LOC_KEY_NAME_SILVER				"silver key"
#define LOC_KEY_NAME_SILVER_RUNE		"silver runekey"
#define LOC_KEY_NAME_SILVER_CARD		"silver keycard"
#define LOC_KEY_NAME_GOLD				"gold key"
#define LOC_KEY_NAME_GOLD_RUNE			"gold runekey"
#define LOC_KEY_NAME_GOLD_CARD			"gold keycard"
#define LOC_KEY_NEED					"You need "

#endif // __LIBREQUAKE__

/*==============================================================================

			MISC STRINGS

==============================================================================*/

#define LOC_COUNTER_COUNT_1A			"Only "
#define LOC_COUNTER_COUNT_1B			" more to go..."
#define LOC_COUNTER_COUNT_2				"There are more to go..."
#define LOC_COUNTER_COMPLETE			"Sequence completed!"

#ifdef __LIBREQUAKE__

#define LOC_SECRET						"You found a secret!"

#else

#define LOC_SECRET						"You found a secret area!"

#endif // __LIBREQUAKE__

/*==============================================================================

			RUNE STRINGS

==============================================================================*/

#define LOC_RUNE_GET					"You got the rune!"

#ifdef __LIBREQUAKE__

#define LOC_RUNE_LQ_YOU					"You"
#define LOC_RUNE_LQ_BLOOD				" got the Rune of Blood!"
#define LOC_RUNE_LQ_BONE				" got the Rune of Bone!"
#define LOC_RUNE_LQ_MIND				" got the Rune of Mind!"
#define LOC_RUNE_LQ_SOUL				" got the Rune of Soul!"

#endif // __LIBREQUAKE__

/*==============================================================================

			CLIENT DEATH TO MONSTER STRINGS

==============================================================================*/

#ifdef __LIBREQUAKE__

#define LOC_DEATH_ARMY 					" was shot by a Chosen"
#define LOC_DEATH_ENFORCER 				" was mowed down by a Cyberhunter"
#define LOC_DEATH_DOG 					" was gored by a Gore Hound"
#define LOC_DEATH_OGRE 					" was demolished by a Barrel Fang"
#define LOC_DEATH_DEMON1 				" was disemboweled by a Moon Rat"
#define LOC_DEATH_WIZARD 				" was shot by a Messenger"
#define LOC_DEATH_ZOMBIE				" was pelted by a Deathless Cultist"
#define LOC_DEATH_KNIGHT 				" was stabbed by a Carcosan Knight"
#define LOC_DEATH_HELL_KNIGHT 			" was gutted by a Biohell Warrior"
#define LOC_DEATH_FISH 					" was nibbled by a Spine Eel"
#define LOC_DEATH_SHAMBLER 				" was shredded by a Hollow"
#define LOC_DEATH_SHALRATH 				" was blasted by a Servant of Nyarlathotep"
#define LOC_DEATH_TARBABY 				" was swarmed by a Bog Face"
#define LOC_DEATH_BOSS 					" was obliterated by Cthulhi"
#define LOC_DEATH_OLDONE 				" became one with Shoggoth"

#else

#define LOC_DEATH_ARMY 					" was shot by a Grunt"
#define LOC_DEATH_ENFORCER 				" was blasted by an Enforcer"
#define LOC_DEATH_DOG 					" was mauled by a Rottweiler"
#define LOC_DEATH_OGRE 					" was destroyed by an Ogre"
#define LOC_DEATH_DEMON1 				" was eviscerated by a Fiend"
#define LOC_DEATH_WIZARD 				" was scragged by a Scrag"
#define LOC_DEATH_ZOMBIE				" joins the Zombies"
#define LOC_DEATH_KNIGHT 				" was slashed by a Knight"
#define LOC_DEATH_HELL_KNIGHT 			" was slain by a Death Knight"
#define LOC_DEATH_FISH 					" was fed to the Rotfish"
#define LOC_DEATH_SHAMBLER 				" was smashed by a Shambler"
#define LOC_DEATH_SHALRATH 				" was exploded by a Vore"
#define LOC_DEATH_TARBABY 				" was slimed by a Spawn"
#define LOC_DEATH_BOSS 					" was blasted by Cthulhi"
#define LOC_DEATH_OLDONE 				" became one with Shub-Niggurath"

#endif // __LIBREQUAKE__

/*==============================================================================

			CLIENT DEATH TO ENVIRONMENT STRINGS

==============================================================================*/

#ifdef __LIBREQUAKE__

#define LOC_DEATH_EXPLO_BOX				" was sent sky high"
#define LOC_DEATH_SQUISH 				" was crushed"
#define LOC_DEATH_SQUISH2 				" was crushed by "
#define LOC_DEATH_TRAP_SPIKE			" was perforated"
#define LOC_DEATH_TRAP_LASER			" was lasered"
#define LOC_DEATH_FIREBALL				" was hit by a lavaball"
#define LOC_DEATH_LEAVE					" tried to escape"
#define LOC_DEATH_DROWN1				" forgot how to swim"
#define LOC_DEATH_DROWN2				" ran out of air"
#define LOC_DEATH_SLIME1				" dissolved in acid"
#define LOC_DEATH_SLIME2				" was disincorporated"
#define LOC_DEATH_LAVA1					" fell into lava"
#define LOC_DEATH_LAVA2					" combusted"
#define LOC_DEATH_LAVA3					" dove headfirst into hot lava"
#define LOC_DEATH_FALL1					" fell off a cliff"
#define LOC_DEATH_FALL2					" took a long walk off a short pier"
#define LOC_DEATH_SPACE1				" fell into space"
#define LOC_DEATH_SPACE2				"'s screams went unheard"
#define LOC_DEATH_VOID1					" fell into the void"
#define LOC_DEATH_VOID2					" fell out of existence"
#define LOC_DEATH_DISCHARGE_WATER		" took a toaster bath"
#define LOC_DEATH_DISCHARGE_SLIME		" took a toaster bath"
#define LOC_DEATH_DISCHARGE_LAVA		" took a toaster bath"
#define LOC_DEATH_DISCHARGE_SELF		"'s Lightning Gun Malfunctioned"
#define LOC_DEATH_SELF_GRENADE			" didn't launch the grenade far enough"
#define LOC_DEATH_SELF_ROCKET			" played with explosives"
#define LOC_DEATH_SELF_OTHER			" misfired"
#define LOC_DEATH_SUICIDE				" committed suicide"
#define LOC_DEATH_OTHER					" died"

#else

#define LOC_DEATH_EXPLO_BOX				" blew up"
#define LOC_DEATH_SQUISH 				" was squished"
#define LOC_DEATH_SQUISH2 				" was squished by "
#define LOC_DEATH_TRAP_SPIKE			" was spiked"
#define LOC_DEATH_TRAP_LASER			" was spiked"
#define LOC_DEATH_FIREBALL				" ate a lavaball"
#define LOC_DEATH_LEAVE					" tried to leave"
#define LOC_DEATH_DROWN1				" sleeps with the fishes"
#define LOC_DEATH_DROWN2				" sucks it down"
#define LOC_DEATH_SLIME1				" gulped a load of slime"
#define LOC_DEATH_SLIME2				" can't exist on slime alone"
#define LOC_DEATH_LAVA1					" turned into hot slag"
#define LOC_DEATH_LAVA2					" visits the Volcano God"
#define LOC_DEATH_LAVA3					" burst into flames"
#define LOC_DEATH_FALL					" fell to his death"
#define LOC_DEATH_DISCHARGE_WATER		" discharges into the water"
#define LOC_DEATH_DISCHARGE_SLIME		" discharges into the slime"
#define LOC_DEATH_DISCHARGE_LAVA		" discharges into the lava"
#define LOC_DEATH_DISCHARGE_SELF		" electrocutes himself"
#define LOC_DEATH_SELF_GRENADE			" tries to put the pin back in"
#define LOC_DEATH_SELF_ROCKET			" becomes bored with life"
#define LOC_DEATH_SELF_OTHER			" checks if his weapon is loaded"
#define LOC_DEATH_SUICIDE				" suicides"
#define LOC_DEATH_OTHER					" died"

#endif // __LIBREQUAKE__

/*==============================================================================

			CLIENT DEATH TO CLIENT STRINGS

==============================================================================*/

// Deathstring 1 is the standard one
// Deathstring 2 has a 1/100 chance to be used instead
// Deathstring G is used for when the victim was gibbed (Grenade Launcher and Rocket Launcher only)
// Deathstring Q is used if the attacker had a Quad Damage
// Deathstring D1 is used if the attack was a discharge (Lightning Gun only)
// Deathstring D2 has a 1/100 chance to be used instead (Lightning Gun only)
// The format for printing is: victim name, deathstring A, attacker name, deathstring B

#ifdef __LIBREQUAKE__

#define LOC_DEATH_AXE_1A				" was hacked to death by "
#define LOC_DEATH_AXE_1B				""
#define LOC_DEATH_AXE_2A				" was chopped to bits by "
#define LOC_DEATH_AXE_2B				""
#define LOC_DEATH_AXE_QA				"'s bucket was kicked by "
#define LOC_DEATH_AXE_QB				""

#define LOC_DEATH_SHOTGUN_1A			" sucked on "
#define LOC_DEATH_SHOTGUN_1B			"'s muffler"
#define LOC_DEATH_SHOTGUN_2A			" nibbled on "
#define LOC_DEATH_SHOTGUN_2B			"'s muffler"
#define LOC_DEATH_SHOTGUN_QA			" was put six feet under by "
#define LOC_DEATH_SHOTGUN_QB			""

#define LOC_DEATH_SUPER_SHOTGUN_1A		" was blasted by "
#define LOC_DEATH_SUPER_SHOTGUN_1B		""
#define LOC_DEATH_SUPER_SHOTGUN_2A		" was shredded by "
#define LOC_DEATH_SUPER_SHOTGUN_2B		""
#define LOC_DEATH_SUPER_SHOTGUN_QA		" was sent home in a box by "
#define LOC_DEATH_SUPER_SHOTGUN_QB		""

#define LOC_DEATH_NAILGUN_1A			" was pierced by "
#define LOC_DEATH_NAILGUN_1B			""
#define LOC_DEATH_NAILGUN_2A			" was filled with holes by "
#define LOC_DEATH_NAILGUN_2B			""
#define LOC_DEATH_NAILGUN_QA			"'s mortal coil was shuffled off by "
#define LOC_DEATH_NAILGUN_QB			""

#define LOC_DEATH_SUPER_NAILGUN_1A		" was perforated by "
#define LOC_DEATH_SUPER_NAILGUN_1B		""
#define LOC_DEATH_SUPER_NAILGUN_2A		" was given speed holes by "
#define LOC_DEATH_SUPER_NAILGUN_2B		""
#define LOC_DEATH_SUPER_NAILGUN_QA		"'s chips were cashed by "
#define LOC_DEATH_SUPER_NAILGUN_QB		""

#define LOC_DEATH_GRENADE_LAUNCHER_1A	" tripped over "
#define LOC_DEATH_GRENADE_LAUNCHER_1B	"'s grenade"
#define LOC_DEATH_GRENADE_LAUNCHER_2A	" stepped on "
#define LOC_DEATH_GRENADE_LAUNCHER_2B	"'s grenade"
#define LOC_DEATH_GRENADE_LAUNCHER_GA	" was gibbed by "
#define LOC_DEATH_GRENADE_LAUNCHER_GB	"'s grenade"
#define LOC_DEATH_GRENADE_LAUNCHER_QA	"'s clock was cleaned by "
#define LOC_DEATH_GRENADE_LAUNCHER_QB	""

#define LOC_DEATH_ROCKET_LAUNCHER_1A	" was blasted by "
#define LOC_DEATH_ROCKET_LAUNCHER_1B	"'s rocket"
#define LOC_DEATH_ROCKET_LAUNCHER_2A	" was fulminated by "
#define LOC_DEATH_ROCKET_LAUNCHER_2B	"'s rocket"
#define LOC_DEATH_ROCKET_LAUNCHER_GA	" was gibbed by "
#define LOC_DEATH_ROCKET_LAUNCHER_GB	"'s rocket"
#define LOC_DEATH_ROCKET_LAUNCHER_Q1A	" rode "
#define LOC_DEATH_ROCKET_LAUNCHER_Q1B	"'s pale horse"

#define LOC_DEATH_LIGHTNING_1A			" was electrocuted by "
#define LOC_DEATH_LIGHTNING_1B			""
#define LOC_DEATH_LIGHTNING_2A			" was given shock treatment by "
#define LOC_DEATH_LIGHTNING_2B			""
#define LOC_DEATH_LIGHTNING_QA			" was sent beyond the veil by "
#define LOC_DEATH_LIGHTNING_QB			""
#define LOC_DEATH_LIGHTNING_DA			" was given a toaster bath by "
#define LOC_DEATH_LIGHTNING_DB			""

#define LOC_DEATH_TELEFRAG				" was telefragged by "

#define LOC_DEATH_DEFLECT_A				"Lucifer's Protection deflected "
#define LOC_DEATH_DEFLECT_B				"'s telefrag on "

#define LOC_TEAMKILL_1					" killed a teammate"
#define LOC_TEAMKILL_2					" friendly-fired"
#define LOC_TEAMKILL_3					" needs an eye exam"
#define LOC_TEAMKILL_4					" betrayed their friend"
#define LOC_TEAMKILL_SQUISH				" crushed a teammate"

#define LOC_DEATH_KILL					" killed "

#else

#define LOC_DEATH_AXE_1A				" was ax-murdered by "
#define LOC_DEATH_AXE_1B				""

#define LOC_DEATH_SHOTGUN_1A			" chewed on "
#define LOC_DEATH_SHOTGUN_1B			"'s boomstick"

#define LOC_DEATH_SUPER_SHOTGUN_1A		" ate 2 loads of "
#define LOC_DEATH_SUPER_SHOTGUN_1B		"'s buckshot"
#define LOC_DEATH_SUPER_SHOTGUN_QA		" ate 8 loads of "
#define LOC_DEATH_SUPER_SHOTGUN_QB		"'s buckshot"

#define LOC_DEATH_NAILGUN_1A			" was nailed by "
#define LOC_DEATH_NAILGUN_1B			""

#define LOC_DEATH_SUPER_NAILGUN_1A		" was punctured by "
#define LOC_DEATH_SUPER_NAILGUN_1B		""

#define LOC_DEATH_GRENADE_LAUNCHER_1A   " eats "
#define LOC_DEATH_GRENADE_LAUNCHER_1B   "'s pineapple"
#define LOC_DEATH_GRENADE_LAUNCHER_GA   " was gibbed by "
#define LOC_DEATH_GRENADE_LAUNCHER_GB   "'s grenade"

#define LOC_DEATH_ROCKET_LAUNCHER_1A	" rides "
#define LOC_DEATH_ROCKET_LAUNCHER_1B	"'s rocket"
#define LOC_DEATH_ROCKET_LAUNCHER_GA	" was gibbed by "
#define LOC_DEATH_ROCKET_LAUNCHER_GB	"'s rocket"
#define LOC_DEATH_ROCKET_LAUNCHER_Q1A	" was brutalized by "
#define LOC_DEATH_ROCKET_LAUNCHER_Q1B	"'s quad rocket"
#define LOC_DEATH_ROCKET_LAUNCHER_Q2A	" was smeared by "
#define LOC_DEATH_ROCKET_LAUNCHER_Q2B	"'s quad rocket"
#define LOC_DEATH_ROCKET_LAUNCHER_Q3A	" rips "
#define LOC_DEATH_ROCKET_LAUNCHER_Q3B	" a new one"

#define LOC_DEATH_LIGHTNING_1A			" accepts "
#define LOC_DEATH_LIGHTNING_1B			"'s shaft"
#define LOC_DEATH_LIGHTNING_DA			" accepts "
#define LOC_DEATH_LIGHTNING_DB			"'s discharge"

#define LOC_DEATH_TELEFRAG				" was telefragged by "

#define LOC_DEATH_DEFLECT_A				"Satan's power deflects "
#define LOC_DEATH_DEFLECT_B				"'s telefrag on "

#define LOC_TEAMKILL_1					" mows down a teammate"
#define LOC_TEAMKILL_2					" checks his glasses"
#define LOC_TEAMKILL_3					" gets a frag for the other team"
#define LOC_TEAMKILL_4					" loses another friend"
#define LOC_TEAMKILL_SQUISH				" squished a teammate"

#define LOC_DEATH_KILL					" killed "

#endif // __LIBREQUAKE__

#ifdef __LIBREQUAKE__

/*==============================================================================

			LIBREQUAKE UTILITY STRINGS

==============================================================================*/

#define LOC_LQ_ISDEVELOPER				"You must be a developer!"

/*==============================================================================

			LIBREQUAKE CAMERA STRINGS

==============================================================================*/

#define LOC_LQ_CAMERAS_MAX				"You have too many cameras!"
#define LOC_LQ_CAMERA_SPAWN_A			"Camera placed successfully, "
#define LOC_LQ_CAMERA_SPAWN_B			" remaining"
#define LOC_LQ_CAMERA_TIME_A			"Time between cameras changed to "
#define LOC_LQ_CAMERA_TIME_B			" seconds"
#define LOC_LQ_CAMERA_NONE				"Oh noes! No camera found! :("

#endif // __LIBREQUAKE__
