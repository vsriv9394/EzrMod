import hashlib
import pickle
import os
import numpy as np
from EzrMod.tape import Tape




def getHashFunction(filename):
	
	hasher = hashlib.md5()
	with open(filename,"rb") as f:
		buf = f.read()
		hasher.update(buf)
	return hasher.hexdigest()




def readExistingTape(function):

	filename = function.__globals__['__file__']

	outfile = filename + ".tape"
	hashNotVerified = True
	
	currentHash = getHashFunction(filename)

	tapeDict = None

	if os.path.exists(outfile):
		tapeDict = pickle.load(open(outfile,"rb"))
		if tapeDict["hash"]==currentHash:
			hashNotVerified = False
	
	return hashNotVerified, currentHash, outfile, tapeDict




def saveTape(tape, currentHash, outfile):

	tapeDict = \
	{
		"hash"   : currentHash,
		"size"   : tape.size,
		"op1"    : tape.op1,
		"op2"    : tape.op2,
		"value"  : tape.value,
		"deriv"  : tape.deriv,
		"oper"   : tape.oper,
		"ifEnd"  : tape.ifEnd,
		"elseEnd": tape.elseEnd
	}
	pickle.dump(tapeDict, open(outfile, "wb"))

	return tapeDict




def compileFunction(function, forceRecompile=True):

	hashNotVerified, currentHash, outfile, tapeDict = readExistingTape(function)

	if hashNotVerified or forceRecompile:

		print("Compiling conditional bifurcation for \"%s\""%(function.__name__))
		
		tapeBinaryTree = compileWithConditionalBifurcation(function)

		print("Stacking bifurcations for \"%s\""%(function.__name__))

		tape = stackTapes(tapeBinaryTree)

		tape.createArrays()
		
		tapeDict = saveTape(tape, currentHash, outfile)

	return tapeDict




def compileWithConditionalBifurcation(function, condVal=[]):

	condVal1 = []
	condVal2 = []

	condVal1.extend(condVal)
	condVal2.extend(condVal)

	condVal1.append(True)
	condVal2.append(False)

	tape1 = Tape(condVal1)
	function(tape1)

	if len(tape1.conditionals)==0: return [tape1]

	tape2 = Tape(condVal2)
	function(tape2)

	if len(tape1.conditionals)==len(condVal1) and len(tape2.conditionals)==len(condVal2):

		return [[tape1], [tape2]]

	elif len(tape1.conditionals)==len(condVal1):
		
		return [[tape1], compileWithConditionalBifurcation(function, condVal=condVal2)]

	elif len(tape2.conditionals)==len(condVal2):
		
		return [compileWithConditionalBifurcation(function, condVal=condVal1), [tape2]]

	else:

		return [compileWithConditionalBifurcation(function, condVal=condVal1),
		        compileWithConditionalBifurcation(function, condVal=condVal2)]




def stackTapes(tapeBinTree, iCond=0):
	
	if len(tapeBinTree)==1:
		
		return tapeBinTree[0]

	else:

		tape1 = stackTapes(tapeBinTree[0], iCond=iCond+1)
		tape2 = stackTapes(tapeBinTree[1], iCond=iCond+1)

		indStart = tape1.conditionals[iCond] + 1

		for i in range(tape2.size):
			
			if     tape2.op1[i]>=indStart:     tape2.op1[i] =     tape2.op1[i] + tape1.size - indStart
			if     tape2.op2[i]>=indStart:     tape2.op2[i] =     tape2.op2[i] + tape1.size - indStart
			if   tape2.ifEnd[i]>=indStart:   tape2.ifEnd[i] =   tape2.ifEnd[i] + tape1.size - indStart
			if tape2.elseEnd[i]>=indStart: tape2.elseEnd[i] = tape2.elseEnd[i] + tape1.size - indStart

		tape1.op1.extend(tape2.op1[indStart:])
		tape1.op2.extend(tape2.op2[indStart:])
		tape1.value.extend(tape2.value[indStart:])
		tape1.oper.extend(tape2.oper[indStart:])
		tape1.ifEnd.extend(tape2.ifEnd[indStart:])
		tape1.elseEnd.extend(tape2.elseEnd[indStart:])
		tape1.ifEnd[tape1.conditionals[iCond]] = tape1.size
		tape1.size = tape1.size + tape2.size - indStart
		tape1.elseEnd[tape1.conditionals[iCond]] = tape1.size

		return tape1
