//TODO: Finish Domination System

float(entity p) GetTeam;

void() domination_touch =
{
	if (self.pausetime > time)
		return;
	
	if (self.team == GetTeam(other))
		return;
	
	self.pausetime = time + .5;
	
	self.team = GetTeam(other);
};

void() info_domination_point = {};

//Deletes the selected entity and puts a domination point in its place
//e is the selected entity
//i is a number between 0 and 3 that determines the rune's model.
void(entity e, float i) set_as_domination_point = {
	local entity oself;
	
	oself = self;
	
	self = spawn();
	setorigin(self, e.origin);
	
	remove(e);
	
	//Sets it to a different classname, so it won't be found again by find_domination_points
	self.classname = "domination_point";
	self.touch = domination_touch;
	setsize (self, '-16 -16 -24', '16 16 32');
	
	if (i == 0 || i == 4)
		setmodel(self, "progs/end1.mdl");
	if (i == 1 || i == 5)
		setmodel(self, "progs/end2.mdl");
	if (i == 2 || i == 6)
		setmodel(self, "progs/end3.mdl");
	if (i == 3 || i == 7)
		setmodel(self, "progs/end4.mdl");
	
	StartItem ();
	
	self = oself;
}

void() find_domination_points =
{
	local float count;
	local float offset;
	local entity t;
	
	offset = floor(random() * 4);
	
	precache_sound ("misc/runekey.wav");
	
	precache_model ("progs/end1.mdl");
	precache_model2 ("progs/end2.mdl");
	precache_model2 ("progs/end3.mdl");
	precache_model2 ("progs/end4.mdl");
	
	while (count < 3) {
		//We can search from world, since entities get removed after being converted into domination points
		t = find(world, classname, "info_domination_point");
		if (t)
			set_as_domination_point(t, count + offset);
	}
	
	setmodel (self, "progs/end1.mdl");
};


