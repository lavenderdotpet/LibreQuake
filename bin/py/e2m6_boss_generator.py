'''
The boss fight in e2m6 uses too many path_corner and trap_spikeshooter entities
to be placed by hand. This is the script I used to automatically place them into
the map file. Written by ZungryWare.
'''

import sys
import os
import shutil
import re
import math
import random
from datetime import datetime

# =============
# Configuration
# =============
SHOOTER_SPEED = 170
SHOOTER_SPACING = 32
SHOOTER_ANGLES = (0, 180, 0)
TRAIN_CORRECTION = 0

SHOOTER_OFFSET = (-64, 0, 0)
PATH_OFFSET = (-64 + 8, -32, -32)
GLOBAL_OFFSET = (-192, 0, 0)

RELAY_ORIGIN = (952, 760, 88)

POINTS = {
    "2": (944, 688, 224),
    "3": (944, 368, 224),
    "4": (944, 368, 96),
    "4b": (944, 176, 96),
    "4c": (944, -176, 96),
    "5": (944, -304, 96),
    "6": (944, -304, 224),
    "7": (944, -496, 224),
}
SEGMENTS = {
    "2_3": ("2", "3"),
    "3_4": ("3", "4"),
    "4_4b": ("4", "4b"),
    "4b_4c": ("4b", "4c"),
    "4c_5": ("4c", "5"),
    "5_6": ("5", "6"),
    "6_7": ("6", "7"),
}
WAVES = [
    {
        "targetname_start": "wave_1_start",
        "targetname_loop": "wave_1_loop",
        "targetname_looper": "wave_1_looper",
        "targetname_path": "wave_1_path",
        "points_start": ["4", "7"],
        "points_loop": ["2", "7"],
    },
    {
        "targetname_start": "wave_2_start",
        "targetname_loop": "wave_2_loop",
        "targetname_looper": "wave_2_looper",
        "targetname_path": "wave_2_path",
        "points_start": ["4", "7"],
        "points_loop": ["4", "7"],
    },
    {
        "targetname_start": "wave_3_start",
        "targetname_loop": "wave_3_loop",
        "targetname_looper": "wave_3_looper",
        "targetname_path": "wave_3_path",
        "points_start": ["4", "5"],
        "points_loop": ["4", "5"],
    },
]

KILL_LASERS_TARGETNAME = "kill_lasers"

DOOR_ANGLES = (0, 0, 0)
DOOR_SPEED = 350
DOOR_WAIT = 0.15
DOOR_OFFSET = (32, 0, 0)
DOOR_BRUSH_DATA = '''// brush 0
{
( -48 -16 16 ) ( -48 16 -16 ) ( -48 16 16 ) tlightrdfb [ 0 -1 0 0 ] [ 0 0 -1 -16 ] 0 1 1
( 0 -16 16 ) ( -48 -16 -16 ) ( -48 -16 16 ) aqmetl01 [ -1 0 0 0 ] [ 0 0 -1 0 ] 0 1 1
( 0 16 -16 ) ( -48 -16 -16 ) ( 0 -16 -16 ) aqmetl01 [ -1.0000000000000002 0 0 0 ] [ 0 1.0000000000000002 0 -32 ] 0 1 1
( 0 16 16 ) ( -48 -16 16 ) ( -48 16 16 ) aqmetl01 [ -1.0000000000000002 0 0 0 ] [ 0 1.0000000000000002 0 -32 ] 0 1 1
( 0 16 16 ) ( -48 16 -16 ) ( 0 16 -16 ) aqmetl01 [ -1 0 0 0 ] [ 0 0 -1 0 ] 0 1 1
( -40 -16 16 ) ( -40 16 16 ) ( -40 16 -16 ) skip [ 0 -1 0 0 ] [ 0 0 -1 -16 ] 0 1 1
}
// brush 1
{
( -40 -16 16 ) ( -40 16 -16 ) ( -40 16 16 ) skip [ 0 -1 0 -16 ] [ 0 0 -1 -72 ] 0 1 1
( 0 -16 16 ) ( -48 -16 -16 ) ( -48 -16 16 ) w94_1 [ 4.371139006309478e-08 0 -0.9999999999999993 -47.99994 ] [ -0.9999999999999993 0 -4.371139006309478e-08 -16 ] 270 1 1
( 0 16 -16 ) ( -48 -16 -16 ) ( 0 -16 -16 ) w94_1 [ 4.3711390063094775e-08 0.9999999999999992 0 0 ] [ -0.9999999999999992 4.3711390063094775e-08 0 -16 ] 270 1 1
( 0 16 16 ) ( -48 -16 16 ) ( -48 16 16 ) w94_1 [ 4.3711390063094775e-08 -0.9999999999999992 0 -31.999937 ] [ -0.9999999999999992 -4.3711390063094775e-08 0 -16 ] 270 1 1
( 0 16 16 ) ( -48 16 -16 ) ( 0 16 -16 ) w94_1 [ 4.371139006309477e-08 0 0.999999999999999 80.00003 ] [ -0.999999999999999 0 4.371139006309477e-08 -16 ] 270 1 1
( 0 16 16 ) ( 0 -16 -16 ) ( 0 -16 16 ) skip [ 0 1 0 16 ] [ 0 0 -1 -72 ] 0 1 1
}
'''

EXPLOSIONS = [
    {
        "targetname": "wave_0_explosion",
        "duration": 1.5,
        "explosions_per_second": 3,
        "bbox": [696, 280, 416, 648, 152, 288],
    },
    {
        "targetname": "wave_1_explosion",
        "duration": 1.5,
        "explosions_per_second": 4,
        "bbox": [696, 280, 416, 648, 152, 288],
    },
    {
        "targetname": "wave_2_explosion",
        "duration": 1.5,
        "explosions_per_second": 5,
        "bbox": [696, 280, 416, 648, 152, 288],
    },
    {
        "targetname": "wave_3_explosion",
        "duration": 4,
        "explosions_per_second": 3,
        "bbox": [696, 280, 416, 648, 152, 288],
    },
    {
        "targetname": "wave_3_explosion",
        "duration": 4,
        "explosions_per_second": 20,
        "bbox": [696, 760, 440, 648, -568, -8],
    },
]


# =======================
# Vector helper functions
# =======================
def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])

def subtract(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])

def vlerp(v1, v2, t):
  return (
    (1 - t) * v1[0] + t * v2[0],
    (1 - t) * v1[1] + t * v2[1],
    (1 - t) * v1[2] + t * v2[2]
  )

def scale(vector, scalar):
  return (
    vector[0] * scalar,
    vector[1] * scalar,
    vector[2] * scalar
  )

def normalize(vector):
  magnitude = math.sqrt(vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2)

  # Prevent dividing by 0 and causing NaNs by ORing with 1
  return (
    vector[0] / (magnitude or 1),
    vector[1] / (magnitude or 1),
    vector[2] / (magnitude or 1)
  )

def magnitude(vector):
  return math.sqrt(vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2)

def get_point_pos(key):
    return add(POINTS[key], GLOBAL_OFFSET)

def get_point_pos_shooter(key):
    return add(get_point_pos(key), SHOOTER_OFFSET)

def get_point_pos_path(key):
    return add(get_point_pos(key), PATH_OFFSET)

def random_point_in_bbox(bbox):
    x = min(bbox[0], bbox[3]) + (random.random() * abs(bbox[0] - bbox[3]))
    y = min(bbox[1], bbox[4]) + (random.random() * abs(bbox[1] - bbox[4]))
    z = min(bbox[2], bbox[5]) + (random.random() * abs(bbox[2] - bbox[5]))
    return (x, y, z)

# ======================
# Graph helper functions
# ======================
def are_connected(a, b):
    for _, value in SEGMENTS.items():
        if value[0] == a and value[1] == b:
            return True
        if value[0] == b and value[1] == a:
            return True
    return False

def get_connections_to(start, end):
    # Breadth-first search
    q = [start]
    prevs = {start: start}
    while (len(q) > 0):
        cur = q.pop(0)
        
        if (cur == end):
            break

        for next in POINTS:
            if are_connected(cur, next):
                if next not in prevs:
                    q.append(next)
                    prevs[next] = cur
    
    # Generate path
    path = [end]
    while True:
        prev = prevs.get(path[-1])
        if prev and prev != path[-1]:
            path.append(prev)
        else:
            break
    
    # Return path reversed
    return path[::-1]

def get_point_travel_time(a, b):
    a_pos = get_point_pos(a)
    b_pos = get_point_pos(b)

    return magnitude(subtract(a_pos, b_pos)) / SHOOTER_SPEED

def get_segment_from_points(a, b):
    segment = None
    reversed = False
    for key, value in SEGMENTS.items():
        if value[0] == a and value[1] == b:
            segment = key
            break
        if value[0] == b and value[1] == a:
            segment = key
            reversed = True
            break
    
    return segment, reversed

# =================
# Buildable Classes
# =================
class Buildable:
    name_counter = 0

    def format_vector(self, vec):
        return f"{vec[0]} {vec[1]} {vec[2]}"

    def build_string(self, data, brush_data=None, brush_origin=None):
        ret = ""

        ret += "{\n"
        for key, value in data.items():
            if isinstance(value, Buildable):
                value = value.get_targetname()
            if type(value) is list or type(value) is tuple:
                value = self.format_vector(value)
            ret += f'"{key}" "{value}"\n'
        ret += f'"_generated" "1"\n'
        ret += self.build_brush_string(brush_data, brush_origin)
        ret += "}\n"

        return ret
    
    def build_brush_string(self, brush_data, brush_origin):
        if brush_data is not None:
            if brush_origin is not None:
                return self.offset_brush_string(brush_data, brush_origin)
            return brush_data
        return ""
    
    def offset_brush_string(self, brush_data, brush_origin):
        # Define the regex pattern to match parenthetical expressions
        pattern_parenthesis = r'\(\s*-?\d+\s+-?\d+\s+-?\d+\s*\)'
        pattern_brackets = r'\[\s*-?\d+\s+-?\d+\s+-?\d+\s*\]'

        # Function to replace the matched parenthetical with the summed values
        def replace_match(match, useBrackets=False):
            parenthetical = match.group()
            parsed = tuple(map(int, re.findall(r'-?\d+', parenthetical)))
            summed = add(parsed, brush_origin)
            # Return the new parenthetical string
            if useBrackets:
                return f"[ {summed[0]} {summed[1]} {summed[2]} ]"
            return f"( {summed[0]} {summed[1]} {summed[2]} )"

        # Use re.sub to find all parentheticals and replace them with the new values
        result = re.sub(pattern_parenthesis, lambda x : replace_match(x, False), brush_data)
        # result = re.sub(pattern_brackets, lambda x : replace_match(x, True), brush_data)
    
        return result

    def generate_targetname(self, prefix):
        str = f"{prefix}_{Buildable.name_counter}"
        Buildable.name_counter += 1
        return str
    
    def build(self):
        return self.build_string({})

    def get_targetname(self):
        return self.targetname

class Shooter(Buildable):
    def __init__(self, origin, angles, is_laser=True):
        self.targetname = self.generate_targetname("sh")
        self.origin = origin
        self.angles = angles
        self.is_laser = is_laser

    def build(self):
        shooter_string = self.build_string({
            "classname": "trap_spikeshooter",
            "origin": self.origin,
            "angles": self.angles,
            "targetname": self.targetname,
            "spawnflags": 2050 if self.is_laser else 2049,
        })
        killer_string = self.build_string({
            "classname": "trigger_relay",
            "origin": RELAY_ORIGIN,
            "targetname": KILL_LASERS_TARGETNAME,
            "killtarget": self.targetname,
            "spawnflags": 2048,
        })
        door_string = self.build_string(
            {
                "classname": "func_door",
                "angles": DOOR_ANGLES,
                "sounds": 2,
                "wait": DOOR_WAIT,
                "lip": 0.2,
                "speed": DOOR_SPEED,
                "targetname": self.targetname,
                "spawnflags": 2053,
            },
            DOOR_BRUSH_DATA,
            add(self.origin, DOOR_OFFSET),
        )
        return shooter_string + killer_string + door_string

class Corner(Buildable):
    def __init__(self, target, origin, wait=0, targetname=None):
        if targetname is None:
            self.targetname = self.generate_targetname("p")
        else:
            self.targetname = targetname
        self.origin = origin
        self.target = target
        self.wait = wait

    def build(self):
        return self.build_string({
            "classname": "path_corner",
            "origin": self.origin,
            "target": self.target,
            "targetname": self.targetname,
            "spawnflags": 2048,
            "wait": self.wait or 0.001,
        })

class Relay(Buildable):
    def __init__(self, target, delay=0):
        self.targetname = self.generate_targetname("r")
        self.target = target
        self.delay = delay

    def build(self):
        return self.build_string({
            "classname": "trigger_relay",
            "origin": RELAY_ORIGIN,
            "delay": self.delay,
            "target": self.target,
            "targetname": self.targetname,
            "spawnflags": 2048,
        })

class Sequence(Buildable):
    def __init__(self, events, targetname=None):
        if targetname is None:
            self.targetname = self.generate_targetname("r")
        else:
            self.targetname = targetname
        self.events = events

    def build(self):
        string = ""
        for event in self.events:
            string += self.build_string({
                "classname": "trigger_relay",
                "origin": RELAY_ORIGIN,
                "delay": event["delay"] or 0.01,
                "target": event["target"],
                "targetname": self.targetname,
                "spawnflags": 2048,
            })
        return string

class Explosion(Buildable):
    def __init__(self, duration, explosions_per_second, bbox, targetname=None):
        if targetname is None:
            self.targetname = self.generate_targetname("exg")
        else:
            self.targetname = targetname

        # Randomly generate explosions
        self.events = []
        for _ in range(round(duration * explosions_per_second)):
            delay = random.random() * duration
            origin = random_point_in_bbox(bbox)
            self.events.append({
                "delay": delay,
                "origin": origin,
                "targetname": self.generate_targetname("ex")
            })
        
        # Always put one explosion dead center at the start
        origin = (
            (bbox[0] + bbox[3]) / 2,
            (bbox[1] + bbox[4]) / 2,
            (bbox[2] + bbox[5]) / 2,
        )
        self.events.append({
            "delay": 0,
            "origin": origin,
            "targetname": self.generate_targetname("ex")
        })

    def build(self):
        string = ""
        for event in self.events:
            string += self.build_string({
                "classname": "trigger_relay",
                "origin": RELAY_ORIGIN,
                "targetname": self.targetname,
                "target": event["targetname"],
                "delay": event["delay"],
                "spawnflags": 2048,
            })
            string += self.build_string({
                "classname": "info_notnull",
                "use": "OgreGrenadeExplode",
                "origin": event["origin"],
                "targetname": event["targetname"],
                "spawnflags": 2048,
            })
        return string


# ==================
# Building functions
# ==================
def build_shooters(shooters):
    str = ""
    for _, shooter in shooters["points"].items():
        str += shooter.build()
    for _, sub_shooters in shooters["segments"].items():
        for shooter in sub_shooters:
            str += shooter["object"].build()

    return str

def build_shooter_sequences(sequences):
    str = ""
    for _, sequence_group in sequences.items():
        str += sequence_group[0].build()
        str += sequence_group[1].build()

    return str

def build_wave_sequences(sequences):
    str = ""
    for sequence in sequences:
        str += sequence.build()

    return str

def build_paths(paths):
    str = ""
    for path in paths:
        for corner in path:
            str += corner.build()

    return str

def build_explosions(explosions):
    str = ""
    for explosion in explosions:
        str += explosion.build()

    return str


# ===================
# Generator functions
# ===================
def generate_shooters_for_segment(seg):
    shooters = []

    a = get_point_pos_shooter(seg[0])
    b = get_point_pos_shooter(seg[1])

    delta = subtract(b, a)
    step = scale(normalize(delta), SHOOTER_SPACING)
    num_steps = math.ceil(magnitude(delta) / SHOOTER_SPACING)

    cur = step
    for i in range(1, num_steps):
        pos = add(cur, a)
        shooters.append({
            "frac": i/num_steps,
            "object": Shooter(pos, SHOOTER_ANGLES)
        })
        cur = add(cur, step)

    return shooters

def generate_shooters():
    shooters = {
        "points": {},
        "segments": {},
    }

    # Generate shooters on all the points
    for key in POINTS:
        shooters["points"][key] = Shooter(get_point_pos_shooter(key), SHOOTER_ANGLES)

    # Generate shooters on all the paths
    for key, value in SEGMENTS.items():
        shooters["segments"][key] = generate_shooters_for_segment(value)

    return shooters

def generate_event(target, delay):
    return {
        "target": target,
        "delay": delay
    }

def generate_shooter_sequence(shooters, segment):
    a = SEGMENTS[segment][0]
    b = SEGMENTS[segment][1]

    sequence_duration = get_point_travel_time(a, b)
    relevant_shooters = shooters["segments"][segment]

    # Build events lists
    events_forward = [generate_event(shooters["points"][b], sequence_duration)]
    events_backward = [generate_event(shooters["points"][a], sequence_duration)]
    for shooter in relevant_shooters:
        events_forward.append(generate_event(shooter["object"], sequence_duration * shooter["frac"]))
        events_backward.append(generate_event(shooter["object"], sequence_duration * (1 - shooter["frac"])))
    
    return (Sequence(events_forward), Sequence(events_backward))

def generate_shooter_sequences(shooters):
    sequences = {}

    for key in SEGMENTS:
        sequences[key] = generate_shooter_sequence(shooters, key)

    return sequences

def generate_wave_sequence_event(shooter_sequences, start, end, delay):
    # Find the segment which contains this start and end
    segment, reversed = get_segment_from_points(start, end)
    
    if segment is not None:
        index = 1 if reversed else 0
        shooter_sequence = shooter_sequences[segment][index]
        time = get_point_travel_time(start, end)
        return generate_event(shooter_sequence, delay), time

def generate_wave_sequence_events(shooter_sequences, start, end, delay):
    # Steps in a wave may have several intermediate steps. We need to use BFS to
    # find the shortest path from one point to another and include all steps on
    # that path.
    events = []
    new_delay = delay

    # Get all intermediate steps
    intermediate_steps = get_connections_to(start, end)
    for current, next in zip(intermediate_steps, intermediate_steps[1:]):
        new_event, time = generate_wave_sequence_event(shooter_sequences, current, next, new_delay)
        events.append(new_event)
        new_delay += time
        new_delay += TRAIN_CORRECTION
    
    return events, new_delay

def generate_wave_sequence(shooter_sequences, wave):
    events_start = []
    events_loop = []

    events_start_delay = 0
    events_loop_delay = 0

    # Events start
    for current, next in zip(wave["points_start"], wave["points_start"][1:]):
        new_events, time = generate_wave_sequence_events(shooter_sequences, current, next, events_start_delay)
        events_start.extend(new_events)
        events_start_delay = time
        events_start_delay += TRAIN_CORRECTION
    
    # Events start link to loop
    current = wave["points_start"][-1]
    next = wave["points_loop"][0]
    new_events, time = generate_wave_sequence_events(shooter_sequences, current, next, events_start_delay)
    events_start.extend(new_events)
    events_start_delay = time
    events_start_delay += TRAIN_CORRECTION

    # Events loop
    for current, next in zip(wave["points_loop"], wave["points_loop"][1:]):
        new_events, time = generate_wave_sequence_events(shooter_sequences, current, next, events_loop_delay)
        events_loop.extend(new_events)
        events_loop_delay = time
        events_loop_delay += TRAIN_CORRECTION
    
    # Events loop link back to start
    current = wave["points_loop"][-1]
    next = wave["points_loop"][0]
    new_events, time = generate_wave_sequence_events(shooter_sequences, current, next, events_loop_delay)
    events_loop.extend(new_events)
    events_loop_delay = time
    events_loop_delay += TRAIN_CORRECTION

    # Insert events to trigger re-loop
    events_start.append(generate_event(wave["targetname_looper"], events_start_delay))
    events_loop.append(generate_event(wave["targetname_looper"], events_loop_delay))
    
    return Sequence(events_start, wave["targetname_start"]), Sequence(events_loop, wave["targetname_loop"])

def generate_wave_sequences(shooter_sequences):
    sequences_start = []
    sequences_loop = []

    for wave in WAVES:
        ss, sl = generate_wave_sequence(shooter_sequences, wave)
        sequences_start.append(ss)
        sequences_start.append(sl)

    return sequences_start, sequences_loop

def generate_wave_path_points(start, end):
    points = []

    # Get all intermediate steps
    intermediate_steps = get_connections_to(start, end)
    for point in intermediate_steps[1:]:
        points.append(point)
    
    return points

def generate_wave_path(wave):
    path_start = []
    path_loop = []

    points_start = [wave["points_start"][0]]
    for current, next in zip(wave["points_start"], wave["points_start"][1:]):
        points_start.extend(generate_wave_path_points(current, next))
    points_start.extend(generate_wave_path_points(wave["points_start"][-1], wave["points_loop"][0]))

    points_loop = [wave["points_loop"][0]]
    for current, next in zip(wave["points_loop"], wave["points_loop"][1:]):
        points_loop.extend(generate_wave_path_points(current, next))
    points_loop.extend(generate_wave_path_points(wave["points_loop"][-1], wave["points_loop"][0]))

    print("POINTS: ")
    print(points_start)
    print(points_loop)

    # Generate loop first
    path_loop.append(Corner("TEMP", get_point_pos_path(points_loop[0])))
    for point in points_loop[1:][::-1]:
        path_loop.insert(0, Corner(path_loop[0], get_point_pos_path(point)))
    path_loop[-1].target = path_loop[0]

    # Generate start
    path_start.append(Corner(path_loop[0], get_point_pos_path(points_start[-1])))
    for point in points_start[1:-1][::-1]:
        path_start.insert(0, Corner(path_start[0], get_point_pos_path(point)))
    path_start.insert(0, Corner(path_start[0], get_point_pos_path(points_start[0]), 0, wave["targetname_path"]))

    return path_loop, path_start

def generate_paths():
    paths_start = []
    paths_loop = []

    for wave in WAVES:
        ps, pl = generate_wave_path(wave)
        paths_start.append(ps)
        paths_loop.append(pl)

    return paths_start, paths_loop

def generate_explosions():
    explosions = []

    for explosion in EXPLOSIONS:
        explosions.append(Explosion(explosion["duration"], explosion["explosions_per_second"], explosion["bbox"], explosion["targetname"]))

    return explosions


# ========================
# File operation functions
# ========================
def backup_map(file_path):
    # Create the backup file path
    file_dir, file_name = os.path.split(file_path)
    file_name_wo_ext, file_ext = os.path.splitext(file_name)
    datetime_string = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    backup_file_name = f"{file_name_wo_ext}_backup_{datetime_string}{file_ext}"
    backup_file_path = os.path.join(file_dir, backup_file_name)

    # Copy the file to create a backup
    shutil.copy2(file_path, backup_file_path)
    print(f"Backup created: {backup_file_path}")

import re

    # Stack to store the positions of '{'
def remove_sections_with_string(data, target_string):
    stack = []
    sections_to_remove = []

    for i, char in enumerate(data):
        if char == '{':
            stack.append(i)
        elif char == '}':
            if stack:
                start = stack.pop()
                # If the stack is empty after popping, it means we found an outermost section
                if not stack:
                    section = data[start:i+1]
                    if target_string in section:
                        sections_to_remove.append((start, i+1))

    # Build the new data excluding sections that need to be removed
    modified_data = []
    last_index = 0
    for start, end in sections_to_remove:
        modified_data.append(data[last_index:start])  # Add text before the section
        last_index = end  # Move the index past the section

    modified_data.append(data[last_index:])  # Add the remaining part of the text

    # Join the list into a final string
    modified_data = ''.join(modified_data)

    return modified_data

def clean_map_data(data):
    return remove_sections_with_string(data, '"_generated" "1"')

def print_stats(data):
    counts = {}
    strs = re.findall(r'\"classname\"\ *\"[^\"]+\"', data)
    for str in strs:
        classname = str.split('"')[3]
        counts[classname] = counts.get(classname, 0) + 1
    
    print()
    print("Map data generated with:")
    total_count = 0
    for classname, count in counts.items():
        print(f"- {count} instances of {classname}")
        total_count += count
    print(f"{total_count} total entities")


def write_to_map_file(file_path, shooters, shooter_sequences, wave_sequences, paths, explosions):
    with open(file_path, 'r') as file:
        data = file.read()

    # Remove all existing generated entities from the map file so we can add in the new entities
    data = clean_map_data(data)

    # Build shooters
    new_data = ""
    new_data += build_shooters(shooters)
    new_data += build_shooter_sequences(shooter_sequences)
    new_data += build_wave_sequences(wave_sequences)
    new_data += build_paths(paths)
    new_data += build_explosions(explosions)

    # Print stats
    print_stats(new_data)

    # Write all new entity data
    data += new_data

    # Write the modified data to the output file
    with open(file_path, 'w') as file:
        file.write(data)


# ====
# Main
# ====
def main():
    # Parse command line args
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} [map file path]")
        exit()
    file_path = sys.argv[1]
    
    # Ensure map file exists
    if not os.path.isfile(file_path):
        print(f'The file \"{file_path}\" does not exist.')
        return

    # First things first, write a backup of the map file in case we screwed something up
    backup_map(file_path)

    # Generate
    shooters = generate_shooters()
    shooter_sequences = generate_shooter_sequences(shooters)
    wave_sequences_start, wave_sequences_loop = generate_wave_sequences(shooter_sequences)
    paths_start, paths_loop = ([], []) # generate_paths()
    explosions = generate_explosions()

    # Write to map file
    write_to_map_file(
        file_path,
        shooters,
        shooter_sequences,
        [*wave_sequences_start, *wave_sequences_loop],
        [*paths_start, *paths_loop],
        explosions,
    )

if __name__ == "__main__":
    main()
