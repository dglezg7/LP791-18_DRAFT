from audioop import add
from fileinput import filename
from operator import isub
import pathlib
import sys
import os
from turtle import color

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import vplot as vpl
from matplotlib.ticker import FormatStrFormatter
import json

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
#print("cDestFolder", cDestFolder)


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

### 
dMassb = 0
cPlanetMass = r"$M_\oplus$"
# Finding the mass of planet b

with open('b.in', 'r') as file:
    lines = file.readlines()
    # Iterate through each line in the file
    for line in lines:
        # Split the line into words
        words = line.split() 
        if len(words) > 0 and words[0] == "dMass":
            dMassb = abs(float(words[1]))
            break
print(f"mass of b: {dMassb} {cPlanetMass}")    

# Keeps track of the subdirs that have completed sims
lcSimsComplete = []
for dirpath, dirnames, filenames in os.walk(path / cDestFolder):
    for dirname in dirnames:
        subdirectory_path = os.path.join(dirpath, dirname)
        for subdirpath, subdirnames, subfiles in os.walk(subdirectory_path):
            for file in subfiles:
                if file.endswith(".forward"):
                    #print("subdirectory_path", subdirectory_path)
                    lcSimsComplete.append(subdirectory_path)
                    break
        continue
lcSimsComplete.sort()
iNumSimsComplete = len(lcSimsComplete)

# Bodies that will be appended if they output an eccentriciy.
lcRelevantBodies = []

cEccFileName = "EccData.json"
cEccFilePath = path / cEccFileName
# Contains all info about each body's initial and max eccentricity and the system's stability
ldEcc = []
# Keeping track of Sims that have already been loaded and stored in the .json file
iNumLoadedSims = 0
# Check if the file exists in the current working directory
if os.path.exists(cEccFilePath):
    print(f"The file '{cEccFileName}' exists in the directory {path}. No need to extract VPL data.")
    # Now we open the .json file to make some figures
    with open(cEccFilePath, "r") as file:
        ldEcc = json.load(file)
    iNumLoadedSims = len(ldEcc)
    #print(ldEcc)
    #print(iNumLoadedSims)
    # Loading in only keys that contain eccentricity info, meaning they're the bodies
    for cKey in ldEcc[0]:
        if type(ldEcc[0][cKey]) is list:
            lcRelevantBodies.append(cKey)    
if iNumLoadedSims < iNumSimsComplete: # Must load rest of the data if incomplete
    if os.path.exists(cEccFilePath):
        print(f"The file {cEccFileName} exists in {path} but does not contain all of the known data. Extracting the rest...")
    else:
        print(f"The file '{cEccFileName}' does not exist in the directory {path}. Extracting VPL data...")

    # i = 0 # Only relevant for debugging issues
    # Extracting data from each of the completed simulations
    for iSubdir in range(iNumLoadedSims, iNumSimsComplete):
        cSubdir = lcSimsComplete[iSubdir]
        # Run vplanet
        # Runs vplanet and takes the bodies
        os.chdir(cSubdir)
        #print("cSubDir:", cSubdir)
        #print("Current directory content:", os.listdir())
        
        SS = vplanet.run("vpl.in", units=False, quiet=True) 
        bodies = SS.bodies # takes the info of all the bodies

        # Array that takes the name of all the bodies
        acBodyNames = [str(bodies[iBody]).split(" ")[-1][:-1] 
                            for iBody in range(len(bodies))]
        sdEccBodyData = {}
        dMaxEcc = 0 # Initializing maximum Eccentricity of system
        for iBody in range(len(bodies)):
            # Determing maximum Eccentricity
            dBodyMaxEcc = 0
            cBodyName = acBodyNames[iBody]
            try:                
                dBodyMaxEcc = max(bodies[iBody].Eccentricity)
                if dBodyMaxEcc > dMaxEcc:
                    dMaxEcc = dBodyMaxEcc
            except AttributeError:
                pass

            # Appendning initial and max Ecc of each body
            ldEccBodyList = []
            try:
                ldEccBodyList.append(bodies[iBody].Eccentricity[0])
                if cBodyName not in lcRelevantBodies:
                    lcRelevantBodies.append(cBodyName)
            except AttributeError:
                pass
            try:
                # I'm including this in the data just in case we want to use it later.
                ldEccBodyList.append(dBodyMaxEcc)
            except AttributeError:
                pass

            if len(ldEccBodyList) == 2:
                sdEccBodyData[acBodyNames[iBody]] = ldEccBodyList

        # Initially assuming system is stable
        bStable = True
        if dMaxEcc >= 1:
            bStable = False
        #print(dMaxEcc, sdEccBodyData)

        sdEccBodyData["stable"] = bStable
        ldEcc.append(sdEccBodyData)

        os.chdir(path / cDestFolder)

        # variable i is only related to debugging issues.
        #i += 1
        #if i > 2:        
        #    break
    # Write the list of dictionaries to a JSON file
    with open(cEccFilePath, "w") as file:
        json.dump(ldEcc, file)

    print(f"Data has been saved to {path / cEccFilePath}.")

# Here we Make a 3x1 figure placing 2 differe initial Ecc on each axis labeling stability
#Typical plot parameters that make for pretty plots
mpl.rcParams['figure.figsize'] = (12,5)
mpl.rcParams['font.size'] = 6.1
iCols = 3
fig, axes = plt.subplots(ncols=3, nrows=1, sharey=False)

# Now here we must loop through the bodies
#print("lcRelevantBodies", lcRelevantBodies)
print(f"Number of simulations complete: {iNumSimsComplete}")
#print(lcSimsComplete)

# Keeps track of which subplot to focus on
iSim = 0
for iBody in range(len(lcRelevantBodies)):
    cBodyX = lcRelevantBodies[iBody]
    for jBody in range(iBody + 1, len(lcRelevantBodies)):
        if iSim >= iCols:
            break
        cBodyY = lcRelevantBodies[jBody]
        print(cBodyX, cBodyY)
        # Two lists below will be used to locate the stable/unstable points on the figure
        ldInitBodyXStable = []
        ldInitBodyYStable = []
        ldInitBodyXUnstable = []
        ldInitBodyYUnstable = []
        ldInitBodyXAll = []
        ldInitBodyYAll = []

        for sEcc in ldEcc:
            dInitBodyX = sEcc[cBodyX][0]
            dInitBodyY = sEcc[cBodyY][0]
            if sEcc["stable"] is True:
                ldInitBodyXStable.append(dInitBodyX)
                ldInitBodyYStable.append(dInitBodyY)                
            if sEcc["stable"] is False:
                ldInitBodyXUnstable.append(dInitBodyX)
                ldInitBodyYUnstable.append(dInitBodyY)
            ldInitBodyXAll.append(dInitBodyX)
            ldInitBodyYAll.append(dInitBodyY)
        dMinX = round(min(ldInitBodyXAll), 1)
        dMaxX = round(max(ldInitBodyXAll), 1)
        dMinY = round(min(ldInitBodyYAll), 1)
        dMaxY = round(max(ldInitBodyYAll), 1)

        #print(cBodyX, ldInitBodyXAll)
        #print(cBodyY, ldInitBodyYAll)
        axes[iSim].scatter(ldInitBodyXStable, ldInitBodyYStable, 
                           color = vpl.colors.pale_blue, label = "Stable")
        axes[iSim].scatter(ldInitBodyXUnstable, ldInitBodyYUnstable, 
                           color = "black", label = "Unstable")
        axes[iSim].set_xlim(dMinX, dMaxX)
        axes[iSim].set_ylim(dMinY, dMaxY)
        axes[iSim].set_xlabel(f"Initial Eccentricity of {cBodyX}", fontsize = 16)
        axes[iSim].set_ylabel(f"Initial Eccentricity of {cBodyY}", fontsize = 16)
        iSim += 1
plt.suptitle(r"$M_b = $" + str(dMassb) + cPlanetMass, fontsize=24)
axes[-1].legend(loc = "upper right")

plt.tight_layout()
plt.show()

# Save the figure
cFileType = "png"
try:
    cFileType = sys.argv[1]
    print(f"File type detected. Saving as .{cFileType} format.")
except IndexError:
    print("No file type detected. Defaulting to .png format.")
fig.savefig(path / f"EccPlot_Massb_{dMassb}.{cFileType}")
print("Figure saved.")
