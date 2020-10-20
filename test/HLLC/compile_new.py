import numpy as np
import EzrMod as ez
from TurbModel import nScal
from ConsToPrim import *
from HLLC import *

nS = 5 + nScal

Uc = np.zeros((1,nS))
Up = np.zeros((1,nS))

Uc[0,0] = 1.5
Uc[0,1] = 9
Uc[0,2] = 12
Uc[0,4] = 150

cons2prim = \
ez.LoopedEzrFunction(
	ConsToPrim, 1,
	[
		[Uc, "Uc", "i", True]
	],
	[
		[Up, "Up", "i", True]
	],
	indexList=[],
	jac=True,
	check=False
)

cons2prim.compute()

print(cons2prim.jac["Up"]["Uc"])

'''
gradUp = np.zeros((30, nS, 3))
area = np.zeros((30))
normal = np.zeros((30,3))
lDisp = np.zeros((30,3))
rDisp = np.zeros((30,3))

sMax = np.zeros((30))
F = np.zeros((30,nS))

cvofa = np.zeros((30,2), dtype=np.int32)

flux = \
ez.LoopedEzrFunction(
	HLLC, 30,
	[
		[Up, "U_Lcopy", "cvofa[i*2]", True],
		[gradUp, "gradU_Lcopy", "cvofa[i*2]", True],
		[Up, "U_Rcopy", "cvofa[i*2+1]", True],
		[gradUp, "gradU_Rcopy", "cvofa[i*2+1]", True],
		[area, "area", "i", False],
		[normal, "normal", "i", False],
		[lDisp, "lDisp", "i", False],
		[rDisp, "rDisp", "i", False]
	],
	[
		[sMax, "sMax", "i", False],
		[F, "F", "i", True]
	],
	indexList=[[cvofa, "cvofa"]],
)

print(flux.jac.keys())
for key in flux.jac["F"].keys():
	print(flux.jac["F"][key].shape)
'''
