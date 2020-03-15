# Python Script: Generate a simple SNDCURVE lump...
# Public Domain code by G. Wessner aka "Stilgar".
# 1600 bytes, each representing 1 mapunit of distance.
# Begin: 127, End: 1

# Initial volume
Volume = 127
# Initial fader
Fader = 0

# Prepare the output file, if we can't, skip the main loop.
with open('lumps/sndcurve.lmp', 'w') as OutFile:
    # Loop out each byte
    # This could probably be done neater with "or" statements...
    # However, I'm less than sure how complex if/and/or works in Python!
    for i in range(1600):
        Fader = Fader + 1    
        if i < 16 and Fader == 2:
            Volume = Volume - 1
            Fader = 0
        elif i < 64 and Fader == 4:
            Volume = Volume - 1
            Fader = 0
        elif i < 256 and Fader == 8:
            Volume = Volume - 1
            Fader = 0
        elif i < 1024 and Fader == 16:
            Volume = Volume - 1
            Fader = 0
        elif Fader == 32:
            Volume = Volume - 1
            Fader = 0
        # Don't allow negative values to sneak in.
        if Volume < 0:
            Volume = 0
        # Byte-ify that Volume.
        OutValue = chr(Volume)
        # Put to file.
        OutFile.write(OutValue)
