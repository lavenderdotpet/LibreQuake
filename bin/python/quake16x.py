
import os, sys
from PIL import Image
import pdb

base_folder = os.path.abspath(os.path.dirname(__file__)).replace("\\","/")
converted_folder = base_folder+"/converted/"
if not os.path.exists(converted_folder):
	os.makedirs(converted_folder)

files = os.listdir(base_folder)

converted = 0
for name in files:
	try:
		img = Image.open(name)
	except (PermissionError, OSError):
		## skip anything that can't be opened or isn't an image
		continue

	output_file = converted_folder + name
	
	if not img.width % 16 == 0:
		new_width  = img.width  - (img.width % 16) + 16
		
	else: 
		new_width = img.width
		
	if not img.height % 16 == 0:
		new_height = img.height - (img.height % 16) + 16
		
	else: new_height = img.height
		

	print(f"Converting: ({img.width}x{img.height}) -> ({new_width}x{new_height}) - {output_file}");
		
	resized = img.resize((new_width, new_height), Image.NEAREST)
	resized.save(output_file)
	converted += 1

plural = "" if converted == 1 else "s"
print(f"Total: {converted} image{plural} converted.")
