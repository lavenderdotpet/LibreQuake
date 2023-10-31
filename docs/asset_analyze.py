'''
A script that analyzes the LibreQuake asset list etherpad
Lists out what assets still are unaccounted for, what assets are
accounted for, and who has claimed them.
Then prints out the ratio of claimed assets to total assets.
Script written by ZungryWare
'''
import sys

console = 1
#Green text
if console == 1:
	col = '\033[92m'
	end = '\033[0m'
else:
	col = "**"
	end = "**"

def bold(str_in):
	return col + str(str_in) + end

def bprint(s):
	sys.stdout.write(s)

def main():
	print(bold("LibreQuake Asset report:\n"))
	
	count_total = 0
	count_complete = 0
	
	#Go through the file, listing incomplete items
	print(bold("Items that still need to be accounted for:"))
	file1 = open("LQ_Assets.txt","r")
	#Go through each line
	for line in file1:
		#Only read lines that contain a file
		if line[:3] == "pak" or line[:3] == "mus":
			#Track the total number of items
			count_total += 1
			items = line.split(" - ")
			#Ensure there is a name on the list
			if len(items) == 1:
				bprint(items[0])
			elif len(items) >= 2:
				if items[1] == "\n":
					bprint(items[0])
	file1.close()
	
	#Go through the file again, listing complete items
	print(bold("\nItems that are complete or in progress:"))
	
	file1 = open("LQ_Assets.txt","r")
	for line in file1:
		if line[:3] == "pak" or line[:3] == "mus":
			items = line.split(" - ")
			#Ensure there is not a name on the list
			if len(items) >= 2:
				if items[1] != "\n":
					#Track the total number of COMPLETED items
					count_complete += 1
					bprint(bold(items[0]) + " is being accounted for by " + bold(items[1]))
	file1.close()
	print("\nItems accounted for: " + bold(str(count_complete) + "/" + str(count_total)))
	percent = (1.0*count_complete/count_total)*100
	percent_truncate = int(percent * 1000) / 1000.0
	print("We're " + bold(str(percent_truncate) + "%") + " of the way there!")
	
main()
