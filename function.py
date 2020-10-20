import numpy as np
import inspect
import os
from subprocess import call
import ctypes as C
from EzrMod.compile import compileFunction

class LoopedEzrFunction(object):

  def __init__(self, func, n, inVars, outVars, indexList=[], jac=True, check=False):

    self.jac = {}
    self.tape = compileFunction(func)
    ezrDir = os.path.dirname(inspect.getfile(compileFunction))

    with open("%s.c"%(func.__name__), "w") as f:

      f.write("#include \"%s/Backend/backend.h\"\n"%(ezrDir))
      if check: f.write("#include <stdio.h>\n")
      f.write("\n")
      f.write("void applyEzFunc\n")
      f.write("(\n")
      for index in indexList:
        f.write("  int *%s,\n"%(index[1]))
      for inVar in inVars:
        f.write("  double *%s,\n"%(inVar[1]))
      for outVar in outVars:
        f.write("  double *%s,\n"%(outVar[1]))
      for outVar in outVars:
        if outVar[3]==True:
          jacShapeOuter = list(outVar[0].shape)
          self.jac[outVar[1]] = {}
          if len(outVar[0].shape)==1:
            jacShapeOuter.extend(1)
          for inVar in inVars:
            if inVar[3]==True:
              jacShape = []
              jacShape.extend(jacShapeOuter)
              if len(inVar[0].shape)==1:
                jacShape.append(1)
              else:
                jacShape.extend(list(inVar[0].shape[1:]))
              if jac==True:
                self.jac[outVar[1]][inVar[1]] = np.zeros(jacShape)
                f.write("  double *jac__%s__%s,\n"%(outVar[1], inVar[1]))
      f.write("  int __size__,\n")
      f.write("  int *__op1__,\n")
      f.write("  int *__op2__,\n")
      f.write("  double *__value__,\n")
      f.write("  double *__deriv__,\n")
      f.write("  int *__oper__,\n")
      f.write("  int *__ifEnd__,\n")
      f.write("  int *__elseEnd__\n")
      f.write(")\n")
      f.write("{\n")
      f.write("  for(int i=0; i<%d; i++)\n"%(n))
      f.write("  {\n")
      f.write("    double *vptr=__value__, *dptr=__deriv__;\n")
      f.write("\n")
      for inVar in inVars:
        if len(inVar[0].shape)==1:
          f.write("    *(vptr++) = %s[%s];\n"%(inVar[1], inVar[2]))
          if check: f.write("    printf(\"%s = %%le\\n\", *(vptr-1));\n"%(inVar[1]))
        else:
          size = np.prod(inVar[0].shape[1:])
          if check:
            f.write("    printf(\"%s \");\n"%(inVar[1]))
            f.write("    for(int j=0; j<%d; j++) { *(vptr++) = %s[%s*%d+j]; printf(\" %%le\", *(vptr-1)); }\n"%(size, inVar[1], inVar[2], size))
            f.write("    printf(\"\\n\");\n")
          else:
            f.write("    for(int j=0; j<%d; j++) *(vptr++) = %s[%s*%d+j];\n"%(size, inVar[1], inVar[2], size))
      f.write("\n")
      f.write("    int end = forwProp(__size__, __op1__, __op2__, __value__, __oper__, __ifEnd__, __elseEnd__);\n")
      f.write("\n")
      f.write("    vptr = __value__ + end;\n")
      f.write("\n")
      outVars.reverse()
      for outVar in outVars:
        if len(outVar[0].shape)==1:
          f.write("    %s[%s] = *(--vptr); --end;\n"%(outVar[1], outVar[2]))
        else:
          size = np.prod(outVar[0].shape[1:])
          f.write("    for(int j=%d-1; j>=0; j--) { %s[%s*%d+j] = *(--vptr); --end; }\n"%(size, outVar[1], outVar[2], size))
      f.write("\n")
      outVars.reverse()
      if jac==True:
        for outVar in outVars:
          if len(outVar[0].shape)==1:
            if outVar[3]==True:
              f.write("    backProp(end, __op1__, __op2__, __value__, __deriv__, __oper__);\n")
              for inVar in inVars:
                if inVar[3]==True:
                  if len(inVar[0].shape)==1:
                    f.write("    *(jac__%s__%s++) = *(dptr++);\n"%(outVar[1], inVar[1]))
                  else:
                    size = np.prod(inVar[0].shape[1:])
                    f.write("    for(int k=0; k<%d; k++) *(jac__%s__%s++) = *(dptr++);\n"%(size, outVar[1], inVar[1]))
                else:
                  if len(inVar[0].shape)==1:
                    f.write("    dptr++;\n")
                  else:
                    size = np.prod(inVar[0].shape[1:])
                    f.write("    for(int k=0; k<%d; k++) dptr++;\n"%(size))
            f.write("    end++; dptr = __deriv__;\n")
          else:
            size = np.prod(outVar[0].shape[1:])
            f.write("    for(int j=0; j<%d; j++)\n"%(size))
            f.write("    {\n")
            if outVar[3]==True:
              f.write("      backProp(end, __op1__, __op2__, __value__, __deriv__, __oper__);\n")
              for inVar in inVars:
                if inVar[3]==True:
                  if len(inVar[0].shape)==1:
                    f.write("      *(jac__%s__%s++) = *(dptr++);\n"%(outVar[1], inVar[1]))
                  else:
                    size = np.prod(inVar[0].shape[1:])
                    f.write("      for(int k=0; k<%d; k++) *(jac__%s__%s++) = *(dptr++);\n"%(size, outVar[1], inVar[1]))
                else:
                  if len(inVar[0].shape)==1:
                    f.write("      dptr++;\n")
                  else:
                    size = np.prod(inVar[0].shape[1:])
                    f.write("      for(int k=0; k<%d; k++) dptr++;\n"%(size))
            f.write("      end++; dptr = __deriv__;\n")
            f.write("    }\n")
      f.write("  }\n")
      f.write("}\n")

    call("gcc -O3 -fPIC -std=c99 --shared %s/Backend/Tape.c %s.c -o lib%s.so"%(ezrDir, func.__name__, func.__name__), shell=True)

    _ip_ = C.POINTER(C.c_int)
    _dp_ = C.POINTER(C.c_double)

    self.lib = C.CDLL("lib%s.so"%(func.__name__))

    self.function = self.lib.__getattr__("applyEzFunc")
    self.function.restype = None
    self.function.argtypes = []
    for index in indexList:
      self.function.argtypes.append(_ip_)
    for inVar in inVars:
      self.function.argtypes.append(_dp_)
    for outVar in outVars:
      self.function.argtypes.append(_dp_)
    if jac==True:
      for key1 in self.jac.keys():
        for key2 in self.jac[key1].keys():
          self.function.argtypes.append(_dp_)
    self.function.argtypes.extend([C.c_int, _ip_, _ip_, _dp_, _dp_, _ip_, _ip_, _ip_])

    self.functionArgs = []
    for index in indexList:
      self.functionArgs.append(index[0].ctypes.data_as(_ip_))
    for inVar in inVars:
      self.functionArgs.append(inVar[0].ctypes.data_as(_dp_))
    for outVar in outVars:
      self.functionArgs.append(outVar[0].ctypes.data_as(_dp_))
    if jac==True:
      for outVar in outVars:
        if outVar[3]==True:
          for inVar in inVars:
            if inVar[3]==True:
              self.functionArgs.append(self.jac[outVar[1]][inVar[1]].ctypes.data_as(_dp_))
    self.functionArgs.append(self.tape["size"])
    self.functionArgs.append(self.tape["op1"].ctypes.data_as(_ip_))
    self.functionArgs.append(self.tape["op2"].ctypes.data_as(_ip_))
    self.functionArgs.append(self.tape["value"].ctypes.data_as(_dp_))
    self.functionArgs.append(self.tape["deriv"].ctypes.data_as(_dp_))
    self.functionArgs.append(self.tape["oper"].ctypes.data_as(_ip_))
    self.functionArgs.append(self.tape["ifEnd"].ctypes.data_as(_ip_))
    self.functionArgs.append(self.tape["elseEnd"].ctypes.data_as(_ip_))

  def compute(self):

    self.function(*(self.functionArgs))
