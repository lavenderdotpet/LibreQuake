/*  
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

==============================================================================*/

#define LOC_EPILOGUE_1              "EPISODE 1 COMPLETION TEXT GOES HERE"
#define LOC_EPILOGUE_1_FREEWARE     "EPISODE 1 COMPLETION TEXT GOES HERE"
#define LOC_EPILOGUE_2              "EPISODE 2 COMPLETION TEXT GOES HERE"
#define LOC_EPILOGUE_3              "EPISODE 3 COMPLETION TEXT GOES HERE"
#define LOC_EPILOGUE_4              "EPISODE 4 COMPLETION TEXT GOES HERE"
#define LOC_EPILOGUE_RUNES          "ALL RUNES TEXT GOES HERE"
#define LOC_EPILOGUE_FINALE         "GAME COMPLETION TEXT GOES HERE"

/*==============================================================================

			CLIENT & SERVER STATE STRINGS

==============================================================================*/

#define LOC_CLIENT_JOIN             " joined the game"
#define LOC_CLIENT_DISCON           " exited the level"
#define LOC_CLIENT_DISCON_DM_A      " left the game with "
#define LOC_CLIENT_DISCON_DM_B      " frags"

/*==============================================================================

			CLIENT WEAPON STATUS STRINGS

==============================================================================*/

#define LOC_WEAPON_INVALID          "Invalid weapon"
#define LOC_WEAPON_NOAMMO           "Out of ammo"

/*==============================================================================

			CLIENT ITEM COLLECTION STRINGS

==============================================================================*/

#define LOC_ITEM_PICKUP_NORMAL      "You got "
#define LOC_ITEM_PICKUP_HEALTH      "You receieve "

#define LOC_ITEM_FROM_BACKPACK      " from a backpack"  // Unused..

#define LOC_ITEM_TYPE_HEALTH        " health"
#define LOC_ITEM_TYPE_ARMOR         " armor"

#define LOC_ITEM_NAME_QUADDMG       "the Crusher Sigil"
#define LOC_ITEM_NAME_PENTPROT      "Lucifier's Protection"
#define LOC_ITEM_NAME_SHADRING      "the Eye of Enigma"
#define LOC_ITEM_NAME_BIOSUIT       "the Diving Suit"
#define LOC_ITEM_NAME_BACKPACK      "Backpack"

#define LOC_ITEM_FADE_QUADDMG       "Your Crusher Sigil is fading..."
#define LOC_ITEM_FADE_PENTPROT      "Lucifier's Protection is fading..."
#define LOC_ITEM_FADE_SHADRING      "The Eye of Enigma is fading..."
#define LOC_ITEM_FADE_BIOSUIT       "Air in Diving Suit is running out..."

/*==============================================================================

			WEAPON AND AMMO STRINGS

==============================================================================*/

#define LOC_WEAPON_NAME_AXE             "Axe"       // Unused..
#define LOC_WEAPON_NAME_SHOTGUN         "Shotgun"   // Unused..
#define LOC_WEAPON_NAME_SUPER_SHOTGUN   "Double-Barreled Shotgun"
#define LOC_WEAPON_NAME_NAILGUN         "Nailgun"
#define LOC_WEAPON_NAME_SUPER_NAILGUN   "Super Nailgun"
#define LOC_WEAPON_NAME_GRENADE_LAUNCH  "Grenade Launcher"
#define LOC_WEAPON_NAME_ROCKET_LAUNCH   "Rocket Launcher"
#define LOC_WEAPON_NAME_THUNDERBOLT     "Lightning Gun"

#define LOC_WEAPON_AMMO_SHELLS          "shells"
#define LOC_WEAPON_AMMO_NAILS           "nails"
#define LOC_WEAPON_AMMO_ROCKETS         "rockets"
#define LOC_WEAPON_AMMO_CELLS           "cells"

/*==============================================================================

			KEY STRINGS

==============================================================================*/

#define LOC_KEY_NAME_SILVER             "the Silver Key"
#define LOC_KEY_NAME_SILVER_RUNE        "the Silver Key"
#define LOC_KEY_NAME_SILVER_CARD        "the Silver Keycard"
#define LOC_KEY_NAME_GOLD               "the Gold Key"
#define LOC_KEY_NAME_GOLD_RUNE          "the Gold Key"
#define LOC_KEY_NAME_GOLD_CARD          "the Gold Keycard"
#define LOC_KEY_NEED                    "You need "

/*==============================================================================

			MISC STRINGS

==============================================================================*/

#define LOC_COUNTER_COUNT_1A	        "Only "
#define LOC_COUNTER_COUNT_1B	        " more to go..."
#define LOC_COUNTER_COUNT_2		        "There are more to go..."
#define LOC_COUNTER_COMPLETE	        "Sequence completed!"
#define LOC_SECRET				        "You found a secret!"

/*==============================================================================

			RUNE STRINGS

==============================================================================*/

#define LOC_RUNE_GET                    "You got the rune!"

#ifdef __LIBREQUAKE__

#define LOC_RUNE_LQ_YOU			        "You"
#define LOC_RUNE_LQ_BLOOD		        " got the Rune of Blood!"
#define LOC_RUNE_LQ_BONE			    " got the Rune of Bone!"
#define LOC_RUNE_LQ_MIND			    " got the Rune of Mind!"
#define LOC_RUNE_LQ_SOUL			    " got the Rune of Soul!"

#endif // __LIBREQUAKE__

/*==============================================================================

			CLIENT DEATH TO MONSTER STRINGS

==============================================================================*/

#define LOC_DEATH_ARMY 				    " was shot by a Chosen"
#define LOC_DEATH_ENFORCER 			    " was mowed down by a Cyberhunter"
#define LOC_DEATH_DOG 				    " was gored by a Gore Hound"
#define LOC_DEATH_OGRE 				    " was demolished by a Deep One"
#define LOC_DEATH_DEMON1 			    " was disemboweled by a Moon Rat"
#define LOC_DEATH_WIZARD 			    " was poisoned by a Messenger"
#define LOC_DEATH_ZOMBIE			    " was pelted by a Deathless Cultist"
#define LOC_DEATH_KNIGHT 			    " was stabbed by a Carcosan Knight"
#define LOC_DEATH_HELL_KNIGHT 		    " was gutted by a Biohell Warrior"
#define LOC_DEATH_FISH 				    " was nibbled by a Spine Eel"
#define LOC_DEATH_SHAMBLER 			    " was shredded by a Hollow"
#define LOC_DEATH_SHALRATH 			    " was blasted by a Servant of Nyarlathotep"
#define LOC_DEATH_TARBABY 			    " was swarmed by a Bog Face"
#define LOC_DEATH_BOSS 				    " was blasted by Cthulhi"
#define LOC_DEATH_OLDONE 			    " became one with Shoggoth"

/*==============================================================================

			CLIENT DEATH TO ENVIRONMENT STRINGS

==============================================================================*/

#define LOC_DEATH_EXPLO_BOX     	    " was sent sky high"
#define LOC_DEATH_SQUISH 	    	    " was crushed"
#define LOC_DEATH_SQUISH2 	    	    " was crushed by "
#define LOC_DEATH_TRAP_SPIKE    	    " was perforated"
#define LOC_DEATH_TRAP_LASER	        " was lasered"
#define LOC_DEATH_FIREBALL	    	    " was hit by a lavaball"
#define LOC_DEATH_LEAVE		    	    " tried to escape"
#define LOC_DEATH_DROWN1	    	    " forgot how to swim"
#define LOC_DEATH_DROWN2	    	    " drowned"
#define LOC_DEATH_DROWN3	    	    " ran out of air"
#define LOC_DEATH_SLIME1	    	    " dissolved in acid"
#define LOC_DEATH_SLIME2	    	    " was disincorporated"
#define LOC_DEATH_LAVA1		    	    " fell into lava"
#define LOC_DEATH_LAVA2		    	    " combusted"
#define LOC_DEATH_LAVA3		    	    " dove headfirst into hot lava"
#define LOC_DEATH_FALL_1	    	    " fell off a cliff"
#define LOC_DEATH_FALL_2	    	    " took a long walk off a short pier"
#define LOC_DEATH_SPACE_1	    	    " fell into space"
#define LOC_DEATH_SPACE_2	    	    "'s screams went unheard"
#define LOC_DEATH_VOID_1		        " fell into the void"
#define LOC_DEATH_VOID_2	    	    " fell out of existence"
#define LOC_DEATH_DISCHARGE_WATER	    " took a toaster bath"
#define LOC_DEATH_DISCHARGE_SLIME	    " took a toaster bath"
#define LOC_DEATH_DISCHARGE_LAVA	    " took a toaster bath"
#define LOC_DEATH_SELF_GRENADE	        " didn't launch the grenade far enough"
#define LOC_DEATH_SELF_ROCKET	        " played with explosives"
#define LOC_DEATH_SELF_OTHER	        " died"
#define LOC_DEATH_SUICIDE		        " committed suicide"
#define LOC_DEATH_OTHER		    	    " died"

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

#define LOC_DEATH_AXE_1A	            " was hacked to death by "
#define LOC_DEATH_AXE_1B	            ""
#define LOC_DEATH_AXE_2A	            " was chopped to bits by "
#define LOC_DEATH_AXE_2B	            ""
#define LOC_DEATH_AXE_QA	            "'s bucket was kicked by "
#define LOC_DEATH_AXE_QB	            ""

#define LOC_DEATH_SHOTGUN_1A	        " sucked on "
#define LOC_DEATH_SHOTGUN_1B	        "'s muffler"
#define LOC_DEATH_SHOTGUN_2A	        " nibbled on "
#define LOC_DEATH_SHOTGUN_2B	        "'s muffler"
#define LOC_DEATH_SHOTGUN_QA	        " was put six feet under by "
#define LOC_DEATH_SHOTGUN_QB	        ""

#define LOC_DEATH_SUPER_SHOTGUN_1A	    " was blasted by "
#define LOC_DEATH_SUPER_SHOTGUN_1B	    ""
#define LOC_DEATH_SUPER_SHOTGUN_2A	    " was shredded by "
#define LOC_DEATH_SUPER_SHOTGUN_2B	    ""
#define LOC_DEATH_SUPER_SHOTGUN_QA	    " was sent home in a box by "
#define LOC_DEATH_SUPER_SHOTGUN_QB	    ""

#define LOC_DEATH_NAILGUN_1A	        " was pierced by "
#define LOC_DEATH_NAILGUN_1B	        ""
#define LOC_DEATH_NAILGUN_2A	        " was filled with holes by "
#define LOC_DEATH_NAILGUN_2B	        ""
#define LOC_DEATH_NAILGUN_QA	        "'s mortal coil was shuffled off by "
#define LOC_DEATH_NAILGUN_QB	        ""

#define LOC_DEATH_SUPER_NAILGUN_1A	    " was perforated by "
#define LOC_DEATH_SUPER_NAILGUN_1B	    ""
#define LOC_DEATH_SUPER_NAILGUN_2A	    " was given speed holes by "
#define LOC_DEATH_SUPER_NAILGUN_2B	    ""
#define LOC_DEATH_SUPER_NAILGUN_QA	    "'s chips were cashed by "
#define LOC_DEATH_SUPER_NAILGUN_QB	    ""

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
#define LOC_DEATH_ROCKET_LAUNCHER_2A	" was shredded by "
#define LOC_DEATH_ROCKET_LAUNCHER_2B	"'s rocket"
#define LOC_DEATH_ROCKET_LAUNCHER_GA	" was gibbed by "
#define LOC_DEATH_ROCKET_LAUNCHER_GB	"'s rocket"
#define LOC_DEATH_ROCKET_LAUNCHER_Q1A	" was sent beyond the veil by "
#define LOC_DEATH_ROCKET_LAUNCHER_Q1B	""
#define LOC_DEATH_ROCKET_LAUNCHER_Q2A	" was sent beyond the veil by "
#define LOC_DEATH_ROCKET_LAUNCHER_Q2B	""
#define LOC_DEATH_ROCKET_LAUNCHER_Q3A	" was sent beyond the veil by "
#define LOC_DEATH_ROCKET_LAUNCHER_Q3B	""

#define LOC_DEATH_LIGHTNING_1A	        " was electrocuted by "
#define LOC_DEATH_LIGHTNING_1B	        ""
#define LOC_DEATH_LIGHTNING_2A	        " was given electroshock therapy by "
#define LOC_DEATH_LIGHTNING_2B	        ""
#define LOC_DEATH_LIGHTNING_QA	        " rode "
#define LOC_DEATH_LIGHTNING_QB	        "'s white horse"
#define LOC_DEATH_LIGHTNING_D1A	        " was given a toaster bath by "
#define LOC_DEATH_LIGHTNING_D1B	        ""
#define LOC_DEATH_LIGHTNING_D2A	        " was given a toaster bath by "
#define LOC_DEATH_LIGHTNING_D2B	        ""

#define LOC_DEATH_TELEFRAG_A	        " was telefragged by "
#define LOC_DEATH_TELEFRAG_B	        ""

#define LOC_DEATH_DEFLECT_A	            "Lucifer's Protection deflects "
#define LOC_DEATH_DEFLECT_B	            "'s telefrag on "
#define LOC_DEATH_DEFLECT_C	            ""

#define LOC_TEAMKILL_1	                " killed a teammate"
#define LOC_TEAMKILL_2	                " friendly-fired"
#define LOC_TEAMKILL_3	                " needs an eye exam"
#define LOC_TEAMKILL_4	                " betrayed their friend"
#define LOC_TEAMKILL_5	                " crushed a teammate"

#ifdef __LIBREQUAKE__

/*==============================================================================

			LIBREQUAKE UTILITY STRINGS

==============================================================================*/

#define LOC_LQ_ISDEVELOPER              "You must be a developer!"

/*==============================================================================

			LIBREQUAKE CAMERA STRINGS

==============================================================================*/

#define LOC_LQ_CAMERAS_MAX              "You have too many cameras!"
#define LOC_LQ_CAMERA_SPAWN_A           "Camera placed successfully, "
#define LOC_LQ_CAMERA_SPAWN_B           " remaining"
#define LOC_LQ_CAMERA_TIME_A            "Time between cameras changed to "
#define LOC_LQ_CAMERA_TIME_B            " seconds"
#define LOC_LQ_CAMERA_NONE              "Oh noes! No camera found! :("

#endif // __LIBREQUAKE__