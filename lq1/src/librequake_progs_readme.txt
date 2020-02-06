These progs.dat have a few additional features over the original progs:

-Bug Fixes: Every bug in the original game that's fixable through the progs.dat, I have squashed. If you know of any bugs that are in these progs that haven't been fixed, please tell me so I can fix them! Some more debatable bugs that are important to gameplay have been left in. For example, in deathmatch, the bug where taking multiple mega-health items will rot down your health faster has been left in, since that is integral to deathmatch gameplay. But it's fixed in singleplayer.

-Multiple .src files: The four .src files are as follows:
progs.src: For compiling the progs for LibreQuake
progs_id1.src: For compiling the fixed progs for the original Quake
progs_qw.src: For compiling the server progs for LibreQuakeWorld
progs_id1_qw.src: For compiling the fixed progs for the original QuakeWorld

-Localization Files: Since LibreQuake has different messages to the player than the original game, I thought it would make sense to put those messages in a separate file, so all messages printed to the player (aside from error messages) can be found in localization.qc or localization_id1.qc

-Merged NetQuake and QuakeWorld source files: NetQuake and QuakeWorld share their source files for the most part. So any changes you make to NetQuake will also be changed for QuakeWorld! This is great if you want to make a multiplayer mod for Quake that can be run in NetQuake or QuakeWorld. I have done my best to leave comments in places where there are differences between the two.

-Cleaned up Code: The code is overall much neater in these progs.

-Removed Unnecessary Garbage: A lot of stuff in the original progs didn't do anything, so I have removed it.

-New Singleplayer and Multiplayer Modes: In order to keep things cleaner, I have made gamemodes.qc, which handles all gamemode checks. Some new modes have been added, such as disabling powerups in deathmatch.

-Minor Tweaks: Lots of minor tweaks have been made to the game. Things like changed particle colors, making the misc_teleporttrain spin around like it was originally intended to, making Shub-Niggurath use her unused wakeup sound, and more!

Hopefully you find these progs useful!
-ZungryWare