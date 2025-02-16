/*  Copyright (C) 1996-1997  Id Software, Inc.
    Copyright (C) 2025 RandomBrushes

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

// This implements kick-interaction. This is inspired by the approach
// published as insideQC-tutorial by Ivana Gibson, but re-implemented.

void() kick_touch
{
    local vector vel;
    float tmp, max_xy;

    // only players shall kick, only entities on the floor shall be interactive
    if(other.classname != "player" || (self.flags & FL_ONGROUND) == 0) {
        return;
    }

    // determine fastest player x/y-movement axis
    // this is an approximation of the player's kicking force
    max_xy = fabs(other.velocity_x);
    tmp = fabs(other.velocity_y);
    if(tmp > max_xy) {
        max_xy = tmp;
    }

    // compute velocity of kicked entity
    tmp = random();
    vel_x = (other.velocity_x * (1.2 + tmp));
    vel_y = (other.velocity_y * (1.2 + tmp));
    vel_z = 110 + max_xy;
    self.velocity = vel;       // set velocity
    self.flags -= FL_ONGROUND; // clear on-ground flag

    // apply some random rotations, scaled by player's kicking force
    tmp = 50 + (max_xy * random());
    vel_x = tmp;
    vel_y = tmp;
    vel_z = tmp;
    self.avelocity = vel;

    // check if entity is scheduled to be removed soon and give extra time for play
    if(self.think == SUB_Remove && (self.nextthink - time < 10)) {
        self.nextthink = time + 10;
    }

    // play a kick sound
    if(random() < 0.75) {
        sound (self, CHAN_ITEM, "zombie/z_miss.wav", 1, ATTN_NORM);
    } else {
        sound (self, CHAN_ITEM, "zombie/z_hit.wav", 1, ATTN_NORM);
    }
    

}
