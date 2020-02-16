//TODO: Finish Domination System

float(entity p) GetTeam;

void() domination_touch =
{
	if (other.classname != "player")
		return;
	
	if (self.pausetime > time)
		return;
	
	if (self.enemy == other)
		return;
	
	if (self.team == GetTeam(other) && self.team && teamplay)
		return;
	
	self.pausetime = time + .5;
	
	bprint (PRINT_HIGH, other.netname);
	bprint (PRINT_HIGH, LOC_DOM_TAKE);
	bprint (PRINT_HIGH, ftos(self.count));
	bprint (PRINT_HIGH, "\n");
	
	sound (self, CHAN_VOICE, "misc/runekey.wav", 1, ATTN_NONE);
	
	self.team = GetTeam(other);
	
	self.enemy = other;
};

void() domination_think =
{
#ifndef qw
	//NetQuake Only
	self.nextthink = time + .2;
	self.think = domination_think;
	
	self.cnt --;
	if (self.cnt <= 0)
	{
		self.cnt = 25;
		if (self.enemy)
		{
			if (self.team == GetTeam(self.enemy) || !teamplay)
			{
				self.enemy.frags = self.enemy.frags + 1;
				self.team = GetTeam(self.enemy);
			}
			else
			{
				self.enemy = world;
				self.team = 0;
			}
		}
	}
	
	if (self.team > 8 || self.team == 0)
		particle (self.origin + '0 0 16', '0 0 0', ((self.team - 1) * 16), 20);
	else
		particle (self.origin + '0 0 16', '0 0 0', ((self.team - 1) * 16) + 15, 20);
#endif
};

//Deletes the selected entity and puts a domination point in its place
//e is the selected entity
//i is a number between 0 and 3 that determines the rune's model.
void(entity e, float runeskin, float i) set_as_domination_point = {
	local entity oself;
	
	oself = self;
	
	self = spawn();
	
	if (runeskin == 0 || runeskin == 4)
		setmodel(self, "progs/end1.mdl");
	if (runeskin == 1 || runeskin == 5)
		setmodel(self, "progs/end2.mdl");
	if (runeskin == 2 || runeskin == 6)
		setmodel(self, "progs/end3.mdl");
	if (runeskin == 3 || runeskin == 7)
		setmodel(self, "progs/end4.mdl");
	
	setsize (self, '-16 -16 -24', '16 16 32');
	setorigin(self, e.origin + '16 16 32');
	
	self.classname = "domination_point";
	self.count = i;
	self.touch = domination_touch;
	self.nextthink = time + .2;
	self.think = domination_think;
	
	PlaceItem ();
	
	self = oself;
	
	remove(e);
}

//Defines whether the entity is able to be replaced with a domination point
float(entity t) priority_for_entity =
{	
	if (t.classname == "item_shells") {return 1;}
	if (t.classname == "item_spikes") {return 1;}
	if (t.classname == "item_rockets") {return 1;}
	if (t.classname == "item_cells") {return 1;}
	if (t.classname == "item_health" && !(t.spawnflags & 2)) {return 1;}
	
	return 0;
}

#define NUM_CANDIDATES 35
//Finds three items in the map and converts them to domination points
//Tries to find items that are fairly far away from each other
//It is random, so new domination points will be selected every time
void() find_domination_points =
{
	local float count;
	local float runeskin;
	local entity t;
	local entity candidates[NUM_CANDIDATES];
	local float dist;
	local float dist2;
	local float pick1;
	local float pick2;
	local float pick3;
	local float pickdistance;
	
	//Pick the random set of three runes
	runeskin = floor(random() * 4);
	
	//Build list of candidates for domination point locations
	t = world;
	do {
		t = nextent(t);
		if (priority_for_entity(t) == 1)
		{
			candidates[count] = t;
			count ++;
		}
	} while (t != world && count < NUM_CANDIDATES);
	
	
	//Pick the first domination point from the candidates list at complete random
	pick1 = floor(random() * count);
	
	if (!candidates[pick1])
		return;
	
	//Select an item that had close to the largest distance from pick1
	//The random call is to make the placement a bit more random
	for (float i = 0; i < count; i ++)
	{
		if (random() < .2)
		{
			dist = vlen(candidates[i].origin - candidates[pick1].origin);
			if (dist > pickdistance && i != pick1)
			{
				pickdistance = dist;
				pick2 = i;
			}
		}
	}
	pickdistance = 0;
	
	if (!candidates[pick2])
	{
		set_as_domination_point(candidates[pick1], runeskin, 1);
		return;
	}
	
	//Lastly, select an item that had close to the largest distance from pick1 and pick2
	//The random call is to make the placement a bit more random
	for (float i = 0; i < count; i ++)
	{	
		if (random() < .4)
		{
			dist = vlen(candidates[i].origin - candidates[pick1].origin);
			dist2 = vlen(candidates[i].origin - candidates[pick2].origin);
			if (dist2 < dist)
				dist = dist2;
			if (dist > pickdistance && i != pick1)
			{
				pickdistance = dist;
				pick3 = i;
			}
		}
	}
	pickdistance = 0;
	
	if (!candidates[pick3])
	{
		set_as_domination_point(candidates[pick1], runeskin  , 1);
		set_as_domination_point(candidates[pick2], runeskin+1, 2);
		return;
	}
	
	set_as_domination_point(candidates[pick1], runeskin  , 1);
	set_as_domination_point(candidates[pick2], runeskin+1, 2);
	set_as_domination_point(candidates[pick3], runeskin+2, 3);
};


