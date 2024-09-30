/*  Copyright (C) 2024 Ivy Bowling <motolegacy@proton.me>

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

#ifdef __LIBREQUAKE__

#define LQ_MAXCAMERAS   3

float cameras_in_world;
float clients_at_camera;
float time_between_cameras;

/*
============
LQ_SpawnCamera

============
*/
void() LQ_SpawnCamera =
{
    if (!cvar("developer")) {
        bprint(PRINT_HIGH, LOC_LQ_ISDEVELOPER);
        bprint(PRINT_HIGH, "\n");
        return;
    }

    if (cameras_in_world >= LQ_MAXCAMERAS) {
        bprint(PRINT_HIGH, LOC_LQ_CAMERAS_MAX);
        bprint(PRINT_HIGH, "\n");
        return;
    }

    string camera_targetname;
    entity camera = spawn();
    camera.classname = "lq_camera";

    switch(cameras_in_world) {
        case 0: camera_targetname = "lq_camera_1"; break;
        case 1: camera_targetname = "lq_camera_2"; break;
        case 2: camera_targetname = "lq_camera_3"; break;
    }

    camera.targetname = camera_targetname;

    setorigin(camera, self.origin);
    camera.angles = self.v_angle;

    cameras_in_world++;

    bprint(PRINT_HIGH, LOC_LQ_CAMERA_SPAWN_A);
    bprint(PRINT_HIGH, ftos(LQ_MAXCAMERAS - cameras_in_world));
    bprint(PRINT_HIGH, LOC_LQ_CAMERA_SPAWN_B);
    bprint(PRINT_HIGH, "\n");
};

/*
============
LQ_AppendCameraTime

============
*/
void(float time_addition) LQ_AppendCameraTime = 
{
    if (!cvar("developer")) {
        bprint(PRINT_HIGH, LOC_LQ_ISDEVELOPER);
        bprint(PRINT_HIGH, "\n");
        return;
    }

    time_between_cameras += time_addition;

    if (time_between_cameras <= 0)
        time_between_cameras = 1;

    bprint(PRINT_HIGH, LOC_LQ_CAMERA_TIME_A);
    bprint(PRINT_HIGH, ftos(time_between_cameras));
    bprint(PRINT_HIGH, LOC_LQ_CAMERA_TIME_B);
    bprint(PRINT_HIGH, "\n");
};

/*
============
LQ_ChangeCamera

============
*/
void() LQ_ChangeCamera =
{
    // If there's only one camera in the world,
    // don't bother. Stick here.
    if (cameras_in_world == 1)
        return;

    entity camera;

    // Look for second camera if at first
    if (clients_at_camera == 1) {
        camera = find(world, targetname, "lq_camera_2");
        clients_at_camera = 2;
    } else {
        // At camera 3, go back to one.
        if (clients_at_camera == 3) {
            camera = find(world, targetname, "lq_camera_1");
            clients_at_camera = 1;
        }
        // We're at camera 2, try to find a 3rd
        if (clients_at_camera == 2) {
            camera = find(world, targetname, "lq_camera_3");
            clients_at_camera = 3;
        }
        // No dice, only two. go to one.
        if (camera == world) {
            camera = find(world, targetname, "lq_camera_1");
            clients_at_camera = 1;
        }
    }

    entity players = find(world, classname, "player");

    while(players != world) {
        // Plop at the camera
        setorigin(players, camera.origin);
        players.angles = players.v_angle = camera.angles;

        // Set up camera change
        self.nextthink = time + time_between_cameras;

        players = find(players, classname, "player");
    }
};

/*
============
LQ_PlayCameras

============
*/
void() LQ_PlayCameras =
{
    if (!cvar("developer")) {
        bprint(PRINT_HIGH, LOC_LQ_ISDEVELOPER);
        bprint(PRINT_HIGH, "\n");
        return;
    }

    entity camera = find(world, targetname, "lq_camera_1");

    if (camera == world) {
        bprint(PRINT_HIGH, LOC_LQ_CAMERA_NONE);
        bprint(PRINT_HIGH, "\n");
        return;
    }

    // We're at the first camera
    clients_at_camera = 1;

    // Default time to 1 second
    if (!time_between_cameras)
        time_between_cameras = 1;

    // Tell the engine to turn on intermission 3
    WriteByte (MSG_ALL, SVC_CUTSCENE);
    WriteString (MSG_ALL, "");  // No message :)

    entity players = find(world, classname, "player");

    while(players != world) {
        // Make the player static-ish
        players.view_ofs = '0 0 0';
        players.fixangle = TRUE;
        players.takedamage = DAMAGE_NO;
        players.solid = SOLID_NOT;
        players.movetype = MOVETYPE_NONE;
        players.modelindex = 0;

        // Plop them at camera one
        setorigin(players, camera.origin);
        players.angles = players.v_angle = camera.angles;

        // Set up camera change
        camera.think = LQ_ChangeCamera;
        camera.nextthink = time + time_between_cameras;

        players = find(players, classname, "player");
    }
};

#endif // __LIBREQUAKE__