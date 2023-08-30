from audioop import add
import pathlib
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import vplot as vpl
from matplotlib.ticker import FormatStrFormatter

import vplanet

# Path hacks
path = pathlib.Path(__file__).parents[0].absolute()
sys.path.insert(1, str(path.parents[0]))

# Run vplanet
# Runs vplanet and takes the bodies
SS = vplanet.run(path / "vpl.in", units=False, quiet=True) 
bodies = SS.bodies # takes the info of all the bodies

# Array that takes the name of all the bodies
acBodiesNames = [str(bodies[iBody]).split(" ")[-1][:-1] 
                    for iBody in range(len(bodies))]

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

if cUnitAngle in "deg":
    cUnitAngle = "$^\circ$"


for iBody in range(len(bodies)):
    cBodyName = acBodiesNames[iBody]
    fig, ([ax1, ax2], [ax3, ax4], [ax5, ax6]) = plt.subplots(3, 2, figsize=[14, 16])
    try: 
        ax1.plot(bodies[iBody].Time, bodies[iBody].SemiMajorAxis, "k")
        ax1.set_rasterization_zorder(0)
        ax1.set_ylabel(f"Semi-Major Axis [{cUnitLength}]")
        ax1.yaxis.set_major_formatter(FormatStrFormatter("%.6f"))

        ax2.plot(bodies[iBody].Time, bodies[iBody].Eccentricity, "k")
        ax2.set_ylabel("Eccentricity")

        plt.subplot(3, 2, 3)
        plt.plot(bodies[iBody].Time, bodies[iBody].Inc, "k")
        plt.ylabel(f"Inclination [{cUnitAngle}]")

        plt.subplot(3, 2, 4)
        plt.plot(bodies[iBody].Time, bodies[iBody].LongP, "k", marker=".", linewidth=0)
        plt.ylim(0, 360)
        plt.ylabel(f"Longitude of Pericenter [{cUnitAngle}]")

        plt.subplot(3, 2, 5)
        plt.plot(bodies[iBody].Time, bodies[iBody].LongA, color="k", marker=".", linewidth=0)
        plt.ylim(0, 360)
        plt.ylabel(f"Longitude of Ascending Node [{cUnitAngle}]")
        plt.xlabel(f"Time [{cUnitTime}]")

        try:
            etot = (bodies[iBody].TotOrbEnergy / bodies[iBody].TotOrbEnergy[0] - 1) * 1e9
            jtot = (bodies[iBody].TotAngMom / bodies[iBody].TotAngMom[0] - 1) * 1e11

            plt.subplot(3, 2, 6)
            plt.plot(bodies[iBody].Time, etot, color=vpl.colors.orange, label=(r"Energy $\times 10^9$"))
            plt.plot(
                bodies[iBody].Time, jtot, color=vpl.colors.purple, label=(r"Ang. Mom. $\times 10^{11}$")
            )
            plt.xlabel(f"Time [{cUnitTime}]", fontsize=16)
            plt.ylabel(r"$(\Delta E / E - 1)/10^{9}$", fontsize=16)
            plt.ylabel(r"$\Delta$E,  $\Delta$J")
            plt.xlabel(f"Time [{cUnitTime}]")
            plt.legend(loc="upper left")
        except AttributeError:
            print(f"WARNING: Conservation values undetected for body {cBodyName}.")

        # Save the figure
        fig.savefig(path / f"{cBodyName}_OrbElems.{sys.argv[1]}")
        print(f"Produced figure for body {cBodyName}")
    except AttributeError:
        print(f"WARNING: Cannot produce figure for body {cBodyName}.")
        print(f"Printing out available output options for {cBodyName}:")
        print(bodies[iBody].__dict__.keys())
