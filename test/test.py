import ctypes as C
import EzrMod as ez

def simpleFunction(tape):

	x = ez.scalar(tape)
	y = ez.scalar(tape)
	z = ez.scalar(tape)

	res = 0.0

	if x>y:
		res = (x+y)*z

	if y>3.0:
		res = (x+y)**2

	res = res * 1.0

tape = ez.compileFunction(simpleFunction)

for i in range(tape["size"]):
	print("%3d %3d %+le %4s %3d %3d"%(tape["op1"][i], tape["op2"][i], tape["value"][i],
	      ez.operationsFromId[tape["oper"][i]], tape["ifEnd"][i], tape["elseEnd"][i]))

libTape  = C.CDLL("../Backend/libBackend.so")
forwprop = libTape.__getattr__("forwProp")
backprop = libTape.__getattr__("backProp")

iPtr = C.POINTER(C.c_int)
dPtr = C.POINTER(C.c_double)

forwprop.argtypes = [C.c_int, iPtr, iPtr, dPtr, iPtr, iPtr, iPtr]
backprop.argtypes = [C.c_int, iPtr, iPtr, dPtr, dPtr, iPtr]
forwprop.restype = C.c_int
backprop.restype = None

tape["value"][0] = 1.0
tape["value"][1] = 4.0
tape["value"][2] = 6.0

idres = \
forwprop(tape["size"],
				 tape["op1"].ctypes.data_as(iPtr),
				 tape["op2"].ctypes.data_as(iPtr),
				 tape["value"].ctypes.data_as(dPtr),
				 tape["oper"].ctypes.data_as(iPtr),
				 tape["ifEnd"].ctypes.data_as(iPtr),
				 tape["elseEnd"].ctypes.data_as(iPtr))

print(tape["value"][idres-1])

backprop(idres-1,
         tape["op1"].ctypes.data_as(iPtr),
         tape["op2"].ctypes.data_as(iPtr),
         tape["value"].ctypes.data_as(dPtr),
         tape["deriv"].ctypes.data_as(dPtr),
         tape["oper"].ctypes.data_as(iPtr))

print(tape["deriv"][:3])
