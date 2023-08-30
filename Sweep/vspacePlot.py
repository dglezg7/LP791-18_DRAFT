from audioop import add
import pathlib
import sys
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import vplot as vpl
from matplotlib.ticker import FormatStrFormatter

import vplanet

# Path hacks
path = pathlib.Path(__file__).parents[0].absolute()
sys.path.insert(1, str(path.parents[0]))

with open('vspace.in', 'r') as file:
    lines = file.readlines()
cDestFolder = ""
for line in lines:
    words = line.split()
    if len(words) > 0 and words[0] == "sDestFolder":
        cDestFolder = words[1]
        break
print(cDestFolder)


# Below we introduce figure axis unit labels
cUnitMass = ""
cUnitLength = ""
cUnitTime = "" 
cUnitAngle = ""
cUnitTemp = ""

# Adds unit from vpl.in file
def addUnit(cUnit, cLabel, TmpLine):
    #print("TmpLine:", TmpLine)
    if len(TmpLine) > 0 and TmpLine[0] == cLabel and len(cUnit) == 0:
        cUnit = TmpLine[1]
    return cUnit

# Open the vpl.in file in the same directory as the script
with open('vpl.in', 'r') as file:
    lines = file.readlines()

# Iterate through each line in the file
for line in lines:
    # Split the line into words
    words = line.split()

    # Check if the line contains the following keywords
    cUnitMass = addUnit(cUnitMass, "sUnitMass", words)
    cUnitLength = addUnit(cUnitLength, "sUnitLength", words)
    cUnitTime = addUnit(cUnitTime, "sUnitTime", words)
    cUnitAngle = addUnit(cUnitAngle, "sUnitAngle", words)
    cUnitTemp = addUnit(cUnitTemp, "sUnitTemp", words)

for dirpath, dirnames, filenames in os.walk(path / cDestFolder):
    for dirname in dirnames:
        subdirectory_path = sorted(os.path.join(dirpath, dirname))
        print(subdirectory_path)
        # Run vplanet
        # Runs vplanet and takes the bodies
        os.chdir(subdirectory_path)
        SS = vplanet.run("vpl.in", units=False, quiet=True) 
        bodies = SS.bodies # takes the info of all the bodies

        # Array that takes the name of all the bodies
        acBodiesNames = [str(bodies[iBody]).split(" ")[-1][:-1] 
                            for iBody in range(len(bodies))]
        dMassb = 0
        cPlanetMass = "$M_\oplus$"
        # Finding the mass of planet b
        
        with open('b.in', 'r') as file:
            lines = file.readlines()
            # Iterate through each line in the file
            for line in lines:
                # Split the line into words
                words = line.split()
                if len(words) > 0:
                    print(words[0], words[1]) 
                if len(words) > 0 and words[0] == "dMass":
                    dMassb = abs(float(words[1]))
                    break
        print(f"mass of b: {dMassb} {cPlanetMass}")

