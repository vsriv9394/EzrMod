import numpy as np

class Tape(object):

	def __init__(self, condVal):

		self.size    = 0
		self.op1     = []
		self.op2     = []
		self.value   = []
		self.oper    = []
		self.ifEnd   = []
		self.elseEnd = []
		self.deriv   = None

		self.conditionals         = []
		self.condVal              = condVal
		self.history              = []
		self.returnCounter        = 0
		self.valueHistory         = {}

	def createArrays(self):

		self.op1     = np.array(self.op1, dtype=np.int32)
		self.op2     = np.array(self.op2, dtype=np.int32)
		self.value   = np.array(self.value)
		self.deriv   = np.zeros_like(self.value)
		self.oper    = np.array(self.oper, dtype=np.int32)
		self.ifEnd   = np.array(self.ifEnd, dtype=np.int32)
		self.elseEnd = np.array(self.elseEnd, dtype=np.int32)
