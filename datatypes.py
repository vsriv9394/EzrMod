import numpy as np

operationsFromId = \
[
  "NEG" ,
  "ABS" ,
  "MAX" ,
  "MIN" ,
  "ADD" ,
  "SUB" ,
  "MUL" ,
  "DIV" ,
  "POW" ,
  "EXP" ,
  "LOG" ,
  "SQRT",
  "SIN" ,
  "COS" ,
  "TAN" ,
  "SINH",
  "COSH",
  "TANH",
  "IFEQ",
  "IFNE",
  "IFLT",
  "IFGT",
  "IFLE",
  "IFGE",
  "INP"
]

operations = \
{
  "NEG" : 0,
  "ABS" : 1,
  "MAX" : 2,
  "MIN" : 3,
  "ADD" : 4,
  "SUB" : 5,
  "MUL" : 6,
  "DIV" : 7,
  "POW" : 8,
  "EXP" : 9,
  "LOG" : 10,
  "SQRT": 11,
  "SIN" : 12,
  "COS" : 13,
  "TAN" : 14,
  "SINH": 15,
  "COSH": 16,
  "TANH": 17,
  "IFEQ": 18,
  "IFNE": 19,
  "IFLT": 20,
  "IFGT": 21,
  "IFLE": 22,
  "IFGE": 23
}

class scalar(object):

  def __init__(self, tape, value=0.0):

    self.tape = tape
    self.id   = self.tape.size

    if value is not None:

      if value not in self.tape.valueHistory.keys():
      
        self.tape.size += 1
        self.tape.op1.append(-1)
        self.tape.op2.append(-1)
        self.tape.value.append(value)
        self.tape.oper.append(-1)
        self.tape.ifEnd.append(-1)
        self.tape.elseEnd.append(-1)
        self.tape.history.append({})

        if value!=0.0:

          self.tape.valueHistory[value] = self.id

      else:

        self.id = self.tape.valueHistory[value]

  def addUnaryOperation(self, operId):

    notFound = True

    result = scalar(self.tape, value=None)

    if operId in self.tape.history[self.id].keys():

      result.id = self.tape.history[self.id][operId]
      notFound = False

    if notFound:
      
      self.tape.size += 1
      self.tape.op1.append(self.id)
      self.tape.op2.append(-1)
      self.tape.value.append(0.0)
      self.tape.oper.append(operId)
      self.tape.ifEnd.append(-1)
      self.tape.elseEnd.append(-1)
      self.tape.history.append({})

      self.tape.history[self.id][operId] = result.id

    return result

  def addBinaryOperation(self, other, operId):

    if type(other).__name__ in ["int", "float", "int32", "int64", "float64"]:
      
      other = scalar(self.tape, value=other)

    notFound     = True
    operNotFound = True

    result = scalar(self.tape, value=None)

    if self.id>other.id:
      
      keyId = self.id
      valId = other.id

    else:

      keyId = other.id
      valId = self.id

    if operId in self.tape.history[keyId].keys():
      
      operNotFound = False
      
      if valId in self.tape.history[keyId][operId].keys():
        
        result.id = self.tape.history[keyId][operId][valId]
        notFound = False

    if notFound:

      self.tape.size += 1
      self.tape.op1.append(self.id)
      self.tape.op2.append(other.id)
      self.tape.value.append(0.0)
      self.tape.oper.append(operId)
      self.tape.ifEnd.append(-1)
      self.tape.elseEnd.append(-1)
      self.tape.history.append({})
      
      if operNotFound:
        self.tape.history[keyId][operId] = {}
      
      self.tape.history[keyId][operId][valId] = result.id

    return result

  def addLogicalOperation(self, other, operId):
    
    if type(other).__name__ in ["int", "float", "int32", "int64", "float64"]:
    
      other = scalar(self.tape, value=other)

    notFound     = True
    operNotFound = True

    result = scalar(self.tape, value=None)

    if len(self.tape.conditionals) < len(self.tape.condVal):
      
      rtnval = self.tape.condVal[len(self.tape.conditionals)]
    
    else:
      
      rtnval = True
    
    self.tape.size += 1
    self.tape.op1.append(self.id)
    self.tape.op2.append(other.id)
    self.tape.value.append(0.0)
    self.tape.oper.append(operId)
    self.tape.ifEnd.append(-1)
    self.tape.elseEnd.append(-1)
    self.tape.conditionals.append(result.id)
    self.tape.history.append({})

    return rtnval
  
  def __neg__(self):
    return self.addUnaryOperation(operations["NEG"])
  
  def __radd__(self, other):
    if type(other).__name__ in ["int", "float", "int32", "int64", "float64"]:
      return scalar(self.tape, value=other) + self
  
  def __rsub__(self, other):
    if type(other).__name__ in ["int", "float", "int32", "int64", "float64"]:
      return scalar(self.tape, value=other) - self
  
  def __rmul__(self, other):
    if type(other).__name__ in ["int", "float", "int32", "int64", "float64"]:
      return scalar(self.tape, value=other) * self
  
  def __rdiv__(self, other):
    if type(other).__name__ in ["int", "float", "int32", "int64", "float64"]:
      return scalar(self.tape, value=other) / self
  
  def __rtruediv__(self, other):
    if type(other).__name__ in ["int", "float", "int32", "int64", "float64"]:
      return scalar(self.tape, value=other) / self
  
  def __rpow__(self, other):
    if type(other).__name__ in ["int", "float", "int32", "int64", "float64"]:
      return scalar(self.tape, value=other) ** self
  
  def __add__(self, other):
    return self.addBinaryOperation(other, operations["ADD"])

  def __sub__(self, other):
    return self.addBinaryOperation(other, operations["SUB"])

  def __mul__(self, other):
    if type(other).__name__ in ["scalar", "int", "float", "int32", "int64", "float64"]:
      return self.addBinaryOperation(other, operations["MUL"])
    else:
      return other * self

  def __div__(self, other):
    return self.addBinaryOperation(other, operations["DIV"])

  def __truediv__(self, other):
    return self.addBinaryOperation(other, operations["DIV"])

  def __pow__(self, other):
    return self.addBinaryOperation(other, operations["POW"])

  def __eq__(self, other):
    return self.addLogicalOperation(other, operations["IFEQ"])

  def __ne__(self, other):
    return self.addLogicalOperation(other, operations["IFNE"])

  def __le__(self, other):
    return self.addLogicalOperation(other, operations["IFLE"])

  def __ge__(self, other):
    return self.addLogicalOperation(other, operations["IFGE"])

  def __lt__(self, other):
    return self.addLogicalOperation(other, operations["IFLT"])

  def __gt__(self, other):
    return self.addLogicalOperation(other, operations["IFGT"])

def max(x,y):
  if type(x).__name__ in ["int", "float", "int32", "int64", "float64"] and type(y).__name__ in ["int", "float", "int32", "int64", "float64"]:
    if float(x)>float(y): return x
    else: return y
  if type(x).__name__ in ["int", "float", "int32", "int64", "float64"]:
    return y.addBinaryOperation(x, operation["MAX"])
  else:
    return x.addBinaryOperation(y, operations["MAX"])

def min(x,y):
  if type(x).__name__ in ["int", "float", "int32", "int64", "float64"] and type(y).__name__ in ["int", "float", "int32", "int64", "float64"]:
    if float(x)<float(y): return x
    else: return y
  if type(x).__name__ in ["int", "float", "int32", "int64", "float64"]:
    return y.addBinaryOperation(x, operation["MIN"])
  else:
    return x.addBinaryOperation(y, operations["MIN"])

def abs(x):
  if type(x).__name__ in ["int", "float", "int32", "int64", "float64"]: return np.abs(x)
  else: return x.addUnaryOperation(operations["ABS"])

def exp(x):
  if type(x).__name__ in ["int", "float", "int32", "int64", "float64"]: return np.exp(x)
  else: return x.addUnaryOperation(operations["EXP"])

def log(x):
  if type(x).__name__ in ["int", "float", "int32", "int64", "float64"]: return np.log(x)
  else: return x.addUnaryOperation(operations["LOG"])

def sqrt(x):
  if type(x).__name__ in ["int", "float", "int32", "int64", "float64"]: return np.sqrt(x)
  else: return x.addUnaryOperation(operations["SQRT"])

def sin(x):
  if type(x).__name__ in ["int", "float", "int32", "int64", "float64"]: return np.sin(x)
  else: return x.addUnaryOperation(operations["SIN"])

def cos(x):
  if type(x).__name__ in ["int", "float", "int32", "int64", "float64"]: return np.cos(x)
  else: return x.addUnaryOperation(operations["COS"])

def tan(x):
  if type(x).__name__ in ["int", "float", "int32", "int64", "float64"]: return np.tan(x)
  else: return x.addUnaryOperation(operations["TAN"])

def sinh(x):
  if type(x).__name__ in ["int", "float", "int32", "int64", "float64"]: return np.sinh(x)
  else: return x.addUnaryOperation(operations["SINH"])

def cosh(x):
  if type(x).__name__ in ["int", "float", "int32", "int64", "float64"]: return np.cosh(x)
  else: return x.addUnaryOperation(operations["COSH"])

def tanh(x):
  if type(x).__name__ in ["int", "float", "int32", "int64", "float64"]: return np.tanh(x)
  else: return x.addUnaryOperation(operations["TANH"])

class vector(object):

  def __init__(self, value):

    if type(value).__name__=="Tape":
      
      self.x = scalar(value, value=0)
      self.y = scalar(value, value=0)
      self.z = scalar(value, value=0)

    else:

      self.x = value[0]
      self.y = value[1]
      self.z = value[2]

  def __neg__(self):
    return vector([self.x, -self.y, -self.z])

  def __add__(self, other):
    return vector([self.x + other.x, self.y + other.y, self.z + other.z])

  def __sub__(self, other):
    return vector([self.x - other.x, self.y - other.y, self.z - other.z])

  def __mul__(self, other):
    return vector([self.x * other, self.y * other, self.z * other])

  def __rmul__(self, other):
    return vector([self.x * other, self.y * other, self.z * other])

  def __div__(self, other):
    return vector([self.x / other, self.y / other, self.z / other])

  def __truediv__(self, other):
    return vector([self.x / other, self.y / other, self.z / other])

  def dot(self, other):
    
    if type(other).__name__=="vector":
      return self.x * self.x + self.y * self.y + self.z * self.z
    
    if type(other).__name__=="tensor":
      return other.T().dot(self)

  def norm(self):
    return sqrt(self.dot(self))

  def cross(self, other):
    return vector([self.y*other.z-self.z*other.y, self.z*other.x-self.x*other.z, self.x*other.y-self.y*other.x])

  def outer(self, other):
    return tensor([[self.x*other.x, self.x*other.y, self.x*other.z],
                   [self.y*other.x, self.y*other.y, self.y*other.z],
                   [self.z*other.x, self.z*other.y, self.z*other.z]])

class tensor(object):
  
  def __init__(self, value):

    if type(value).__name__=="Tape":

      self.xx = scalar(value, value=0)
      self.xy = scalar(value, value=0)
      self.xz = scalar(value, value=0)

      self.yx = scalar(value, value=0)
      self.yy = scalar(value, value=0)
      self.yz = scalar(value, value=0)

      self.zx = scalar(value, value=0)
      self.zy = scalar(value, value=0)
      self.zz = scalar(value, value=0)

    else:
    
      self.xx = value[0][0]
      self.xy = value[0][1]
      self.xz = value[0][2]

      self.yx = value[1][0]
      self.yy = value[1][1]
      self.yz = value[1][2]

      self.zx = value[2][0]
      self.zy = value[2][1]
      self.zz = value[2][2]

  def __neg__(self):
    return tensor([[-self.xx, -self.yx, -self.zx],
                   [-self.xy, -self.yy, -self.zy],
                   [-self.xz, -self.yz, -self.zz]])

  def __add__(self, other):
    return tensor([[self.xx+other.xx, self.xy+other.xy, self.xz+other.xz],
                   [self.yx+other.yx, self.xy+other.yy, self.xz+other.yz],
                   [self.xx+other.zx, self.xy+other.zy, self.xz+other.zz]])

  def __sub__(self, other):
    return tensor([[self.xx-other.xx, self.xy-other.xy, self.xz-other.xz],
                   [self.yx-other.yx, self.xy-other.yy, self.xz-other.yz],
                   [self.xx-other.zx, self.xy-other.zy, self.xz-other.zz]])

  def __mul__(self, other):
    return tensor([[self.xx*other, self.xy*other, self.xz*other],
                   [self.yx*other, self.xy*other, self.xz*other],
                   [self.xx*other, self.xy*other, self.xz*other]])

  def __rmul__(self, other):
    return tensor([[self.xx*other, self.xy*other, self.xz*other],
                   [self.yx*other, self.xy*other, self.xz*other],
                   [self.xx*other, self.xy*other, self.xz*other]])

  def __div__(self, other):
    return tensor([[self.xx/other, self.xy/other, self.xz/other],
                   [self.yx/other, self.xy/other, self.xz/other],
                   [self.xx/other, self.xy/other, self.xz/other]])

  def __truediv__(self, other):
    return tensor([[self.xx/other, self.xy/other, self.xz/other],
                   [self.yx/other, self.xy/other, self.xz/other],
                   [self.xx/other, self.xy/other, self.xz/other]])

  def dot(self, other):
    
    if type(other).__name__=="tensor":
      return self.xx*other.xx + self.xy*other.xy + self.xz*other.xz\
           + self.yx*other.yx + self.yy*other.yy + self.yz*other.yz\
           + self.zx*other.zx + self.zy*other.zy + self.zz*other.zz
    
    if type(other).__name__=="vector":
      return vector([self.xx*other.x + self.xy*other.y + self.xz*other.z,
                     self.yx*other.x + self.yy*other.y + self.yz*other.z,
                     self.zx*other.x + self.zy*other.y + self.zz*other.z])

  def T(self):
    return tensor([[self.xx, self.yx, self.zx],
                   [self.xy, self.yy, self.zy],
                   [self.xz, self.yz, self.zz]])

  def trace(self):
    return self.xx + self.yy + self.zz

  def symm(self):
    return 0.5 * (self + self.T())

def eye(tape):

  eye1 = scalar(tape, value=1.0)
  eye0 = scalar(tape, value=0.0)

  return tensor([[eye1, eye0, eye0],
                 [eye0, eye1, eye0],
                 [eye0, eye0, eye1]])
