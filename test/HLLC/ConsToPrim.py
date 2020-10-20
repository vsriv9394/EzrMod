import EzrMod as ez
from TurbModel import *
from GasProp import *

def ConsToPrim(tape):

	rho     = ez.scalar(tape)
	rhoVel  = ez.vector(tape)
	rhoE    = ez.scalar(tape)
	rhoScal = [ez.scalar(tape) for iScal in range(nScal)]


	scal = [rhoScal[i]/rho for i in range(nScal)]
	vel  = rhoVel / rho
	e    = rhoE/rho - 0.5 * vel.dot(vel) - calcTKE(scal)
	enth = e + R * e / calcCv(e)

	rho  = rho * 1.0
	vel  = vel * 1.0
	enth = enth * 1.0
	scal = [scal[i]*1.0 for i in range(nScal)]
