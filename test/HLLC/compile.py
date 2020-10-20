import EzrMod as ez
from ConsToPrim import *
from HLLC import *

InternalFluxTape = ez.compileFunction(HLLC)
VariableTape     = ez.compileFunction(ConsToPrim)

t = InternalFluxTape
with open("trace_Flux", "w") as f:
	for i in range(t["size"]):
		f.write("%4d %4d %+le %4s %4d %4d\n"%(t["op1"][i], t["op2"][i], t["value"][i], ez.operationsFromId[t["oper"][i]], t["ifEnd"][i], t["elseEnd"][i]))

t = VariableTape
with open("trace_Var", "w") as f:
	for i in range(t["size"]):
		f.write("%4d %4d %+le %4s %4d %4d\n"%(t["op1"][i], t["op2"][i], t["value"][i], ez.operationsFromId[t["oper"][i]], t["ifEnd"][i], t["elseEnd"][i]))
