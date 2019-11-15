
# LibreQuartz


The *LibreQuartz* project aims to create a complete, free content first
person shooter game, but *LibreQuartz* by itself is just the raw 
material for a game.  
It must be paired with a compatible engine to be played.

There is a massive [back
catalog](https://www.quaddicted.com), spanning over two decades,
containing thousands of *quake* levels and other modifications 
(“mods”) made by fans of the game.
*LibreQuartz* aims to be compatible with these and allows most to be
played without the need to use non-free software.

The engine uses a directory called `id1`, within that directory
there are two archives called `pak0.pak` and `pak1.pak`,
these archives contain all the game data except the soundtrack.
While the *quake* engine source code is free,
you would normally still need one of the proprietary data files from
[id Software](http://www.idsoftware.com/) to play *quake*.
*LibreQuartz* aims to create a free alternative: combined with 
the GPL-licensed *quake* source code, this results in a completely
free game.

For more information, see ~~http://LibreQuartz.github.io/~~
 not available at the moment.

# How to Play

Since *LibreQuartz* is only the game data, you will still need to
download an engine separately.  
These are also often termed “source ports” by the community.  
There are an overwhelming number of choices available, a lengthy list of
 which is available on the 
[quake Wiki](https://quakewiki.org/wiki/Engines).

One particularly recommended by the *LibreQuartz* project is
[QuakeSpasm](http://quakespasm.sourceforge.net/download.htm).  
This engine offers good support for
single-player and the majority of mods created for both
*quake* and *LibreQuartz*.

On _Windows_, you should place *LibreQuartz*’s data files (those ending
with `.pak`) in a directory named `id1` with the engine 
in the same directory as the `id1` folder (e.g, `fteqw64.exe`).

On _Unix-like systems_, these data files should go in either 
`/usr/share/games/quake` or your home directory.  
If *LibreQuartz* comes packaged as part of your
operating system distribution, it should already be installed into the
proper location.

Hopefully, your engine of choice should already be capable of running
*LibreQuartz* without extra configuration.  
This may not be the case, however, if the engine does not recognize any 
of the filenames for *LibreQuartz*, and might require manual 
intervention to make it so.  

The following should solve it:

  * Use the `+game` command line parameter.  
    For example, to play you can enter `+game +id1` either at a command
    line, or adding it to an application shortcut.

Additionally, for Unix-like operating systems, such as GNU/Linux or a
BSD variant, *LibreQuartz* may be packaged and installed with programs
named `LibreQuartz` that automatically run an engine for proper play.  
Desktop files may also be installed so that you can start the game using
a graphical interface and avoid the command line altogether.

# What “Free” Means

When we speak of free content or software, we refer to the movement in
which your freedoms to use, copy, modify, and study a work is not
infringed.  
For example, you may freely use *LibreQuartz* for any purpose you see 
fit, you may redistribute it to anyone without needing to ask
for permission, you may modify it (provided you keep the license
intact, see `COPYING`), and you may study it.

You may read more about free software at the [GNU](http://www.gnu.org/)
and [Free Software Foundation](http://www.fsf.org/) websites.

# Contributing to LibreQuartz

Contributions to *LibreQuartz* are always welcome, however there are a
few guidelines that should be followed:

## Intellectual property

We know people hate legalese, but this is important. This applies to
**everything** which is submitted.

You must be careful when basing on existing graphics or sounds.
Most *quake* projects are lax on reusing intellectual property.  
There are many mods which contain modified *quake* sprites, for example.
However, due to the nature of this project, we do not have the same
liberty to rip as we please.

The general rules go as follows:

  1. You must have permission for everything you submit.  
     If you make your own resources, do not base on resources from 
     *quake* or any other restricted work.  
     If you take work from other places, please make sure that the work 
     is freely-licensed or that you obtain permission to include it in 
     the *LibreQuartz* project.  
     They may not place additional restrictions compared to the normal 
     *LibreQuartz* license.

  2. Do not try to emulate *quake* resources exactly.  
     Where possible, put effort to make new versions look visibly 
     different from *quake*.  
     This is a tough call, because our compatibility with *quake* mods 
     limits how far we can deviate, but it is feasible.

  3. Be especially careful of “free textures” (or “free sounds” or
     “free graphics”) sites.  Although these would appear at first to
     be okay to use, many are free for “non-commercial use only.”
     One of the things we want to be able to do is put this in
     GNU/Linux distributions (which can be sold or developed
     commercially).

## Levels

All levels for *LibreQuartz* must be vanilla-compatible, requiring an
expanded-limits or limit-removing engine is not permissible.  
This means you may not exceed the limits of the original *quake* engine,
and do not depend on additional mapping features.  
Levels should be in *quake*’s original format, not in “valve”-format.

It is sensible to also heed the following guidelines:

  1. Make sure that skill levels are implemented, and that all
     multiplayer start points, both cooperative and deathmatch, are
     present.

  2. Try to make levels appropriately difficult for their position
     within the progression of the game.  Also bear in mind that not
     all players may be as skilled a player as you.

  3. While unrestricted by limits, do not make excessively complicated
     scenes.  
     It is desirable that *LibreQuartz* levels should be playable on 
     low-powered hardware, such as phones and old computers.

  4. Test your levels in 
     [DOS Quake](ftp://ftp.idsoftware.com/idstuff/quake/quake108.zip) 
     to make sure that vanilla compatibility is maintained.  
     This is an engine with strict adherence to vanilla quake limits and
     bugs, and working in it assures that levels can be played with any
     *quake* engine.

## Graphics

Graphics should generally have the same color and size as the original
*quake* graphics, as to remain compatible with mods.  
Otherwise, levels may end up looking like a nightmare in design.  
They may be thematically different as long as it doesn’t clash.

## Submitting your work

The most common, and a fairly simple method, to submit your work is by
posting it on the [LQ Discord](https://discord.gg/H9gwFTQ) or 
[LQ Matrix](https://matrix.to/#/+librequartz:matrix.org).

This allows a quick cycle or development and feedback.

An alternative to using the forum, is to post your submission on the
[issue tracker](https://github.com/MissLav/LibreQuartz/issues), which 
may also be peer-reviewed and provide a feedback cycle.

Unfortunately, the LibreQuartz project cannot provide hosting space in
the form of a web page nor FTP, however there are many free file hosts
to use when you need a location to upload files.  
Sites and services such as [Dropbox](https://www.dropbox.com/) and
[Mega](https://mega.co.nz/), as well as others, are common and should 
be simple to use.

### Crediting information

*LibreQuartz* is made up of submissions from many people all over the
globe.  
All of them, including **you**, deserve credit!  
Please do not forget to provide your name and email when submitting 
resources.

### Using Git

You can also commit on a clone of the *LibreQuartz* repository,
although this is a technical task and it is okay to let other
*LibreQuartz* maintainers to do it instead: that is our normal mode of 
operation.  
However, pull requests are much appreciated and you may submit them in
any manner you wish, with GitHub’s direct pull requests being the
simplest, but by far not the only means.

*LibreQuartz* uses the commit message style commonly seen in 
distributed version control systems, adopted by projects such as Linux 
and Git.
For an explanation of this style, see
[How to Write a Git Commit
Message](https://chris.beams.io/posts/git-commit/).
# lq
# lq
