import EzrMod as ez
from TurbModel import nScal, calcTKE, calcMuTurb, calcDiffTurb, PrTurb
from GasProp import R, calcCp, calcCv, calcMuLam, calcPrLam

def HLLC(tape):

	# INPUTS ####################################################################################################################

	rhoLcv  = ez.scalar(tape)
	velLcv  = ez.vector(tape)
	enthLcv = ez.scalar(tape)
	scalLcv = [ez.scalar(tape) for iScal in range(nScal)]

	rhoRcv  = ez.scalar(tape)
	velRcv  = ez.vector(tape)
	enthRcv = ez.scalar(tape)
	scalRcv = [ez.scalar(tape) for iScal in range(nScal)]

	gradRhoL  = ez.vector(tape)
	gradVelL  = ez.tensor(tape)
	gradEnthL = ez.vector(tape)
	gradScalL = [ez.vector(tape) for iScal in range(nScal)]

	gradRhoR  = ez.vector(tape)
	gradVelR  = ez.tensor(tape)
	gradEnthR = ez.vector(tape)
	gradScalR = [ez.vector(tape) for iScal in range(nScal)]

	area  = ez.scalar(tape)
	n     = ez.vector(tape)
	lDisp = ez.vector(tape)
	rDisp = ez.vector(tape)

	# INTERPOLATION #############################################################################################################

	rhoL  =   rhoLcv    +  gradRhoL.dot(lDisp)
	velL  =   velLcv    +  gradVelL.dot(lDisp)
	enthL =  enthLcv    + gradEnthL.dot(lDisp)
	scalL = [scalLcv[iScal] + gradScalL[iScal].dot(lDisp) for iScal in range(nScal)]

	rhoR  =   rhoRcv    +  gradRhoR.dot(rDisp)
	velR  =   velRcv    +  gradVelR.dot(rDisp)
	enthR =  enthRcv    + gradEnthR.dot(rDisp)
	scalR = [scalRcv[iScal] + gradScalR[iScal].dot(rDisp) for iScal in range(nScal)]

	# CALCULATE VARIABLES #######################################################################################################

	CpL = calcCp(enthL)
	CpR = calcCp(enthR)

	gammaL = CpL / (CpL - R)
	gammaR = CpR / (CpR - R)

	tkeL = calcTKE(scalL)
	tkeR = calcTKE(scalR)

	unL   = velL.dot(n)
	TL    = enthL / CpL
	pL    = rhoL * R * TL
	cL    = ez.sqrt(gammaL * R * TL)
	rhoEL = rhoL * enthL - pL + 0.5 * velL.dot(velL) + tkeL

	unR   = velR.dot(n)
	TR    = enthR / CpR
	pR    = rhoR * R * TR
	cR    = ez.sqrt(gammaL * R * TR)
	rhoER = rhoR * enthR - pR + 0.5 * velR.dot(velR) + tkeR

	# VISCOUS FLUXES ############################################################################################################

	cvDisp = lDisp - rDisp
	cvDist = cvDisp.norm()
	cvDisp = cvDisp / cvDist

	gradVel  = 0.5 * (gradVelL + gradVelR)
	gradEnth = 0.5 * (gradEnthL + gradEnthR)
	gradScal = [0.5 * (gradScalL[iScal] + gradScalR[iScal]) for iScal in range(nScal)]

	gradVel  = gradVel - (gradVel.dot(cvDisp) - (velR-velL)/cvDist).outer(cvDisp)
	gradEnth = gradEnth - (gradEnth.dot(cvDisp) - (enthR-enthL)/cvDist)*(cvDisp)
	gradScal = [gradScal[i] - (gradScal[i].dot(cvDisp) - (scalR[i]-scalL[i])/cvDist)*cvDisp for i in range(nScal)]

	I = ez.eye(tape)

	rho = 0.5 * (rhoL + rhoR)
	vel = 0.5 * (velL + velR)
	T = 0.5 * (TL + TR)
	scal = [0.5 * (scalL[iScal] + scalR[iScal]) for iScal in range(nScal)]

	mu  = calcMuLam(T)
	muT = calcMuTurb(rho, mu, scal, gradVel)
	strain = 0.5 * (gradVel + gradVel.T())
	tau = 2 * (muT + mu) * (strain - (strain.trace()/3.0)*I) - (2.0/3.0) * rho * calcTKE(scal) * I

	diff = calcDiffTurb(rho, mu, scal, gradVel)

	Frho     =  0
	Frhou    = -tau.dot(n)
	FrhoE    = -tau.dot(n).dot(vel)-(mu/calcPrLam(T)+muT/PrTurb)*gradEnth.dot(n)
	FrhoScal = [-diff[iScal]*gradScal[iScal].dot(n) for iScal in range(nScal)]

	# SUBROUTINE ################################################################################################################

	roeL      = ez.sqrt(rhoL) / (ez.sqrt(rhoL) + ez.sqrt(rhoR))
	roeR      = ez.sqrt(rhoR) / (ez.sqrt(rhoL) + ez.sqrt(rhoR))
	velRoe    = roeL * velL + roeR * velR
	unRoe     = velRoe.dot(n)
	gamPByRho = roeL * (cL*cL + 0.5 * (gammaL-1.0) * velL.dot(velL)) + roeR * (cR*cR + 0.5 * (gammaR-1.0) * velR.dot(velR))
	cRoe      = ez.sqrt(gamPByRho - (0.5 * (gammaL+gammaR) - 1.0) * 0.5 * velRoe.dot(velRoe))

	sL = ez.min(unRoe-cRoe, unL-cL)
	sR = ez.min(unRoe+cRoe, unR+cR)
	sM = (pL - pR + rhoR*unR*(sR-unR) - rhoL*unL*(sL-unL)) / (rhoR*(sR-unR) - rhoL*(sL-unL))

	pStar = rhoR*(unR-sR)*(unR-sM) + pR

	if sM >= 0.0:

		if sL > 0.0:

			Frho     = Frho     + rhoL * unL
			Frhou    = Frhou    + rhoL*velL*unL + pL*n
			FrhoE    = FrhoE    + (rhoEL + pL) * unL
			FrhoScal = [FrhoScal[iScal] + Frho * scalL[iScal] for iScal in range(nScal)]

		else:

			rhoSL  = rhoL * (sL - unL) / (sL - sM)
			rhouSL = (rhoL * velL * (sL - unL) + (pStar - pL) * n) / (sL - sM)
			rhoESL = (rhoEL * (sL - unL) - pL*unL + pStar*sM) / (sL - sM)

			Frho     = Frho     + rhoSL * sM
			Frhou    = Frhou    + rhouSL * sM + pStar * n
			FrhoE    = FrhoE    + (rhoESL + pStar) * sM
			FrhoScal = [FrhoScal[iScal] + Frho * scalL[iScal] for iScal in range(nScal)]

	else:

		if sR >= 0.0:

			rhoSR  = rhoR * (sR - unR) / (sR - sM)
			rhouSR = (rhoR * velR * (sR - unR) + (pStar - pR) * n) / (sR - sM)
			rhoESR = (rhoER * (sR - unR) - pR*unR + pStar*sM) / (sR - sM)

			Frho     = Frho     + rhoSR * sM
			Frhou    = Frhou    + rhouSR * sM + pStar * n
			FrhoE    = FrhoE    + (rhoESR + pStar) * sM
			FrhoScal = [FrhoScal[iScal] + Frho * scalR[iScal] for iScal in range(nScal)]

		else:

			Frho     = Frho     + rhoR * unR
			Frhou    = Frhou    + rhoR*velR*unR + pR*n
			FrhoE    = FrhoE    + (rhoER + pR) * unR
			FrhoScal = [FrhoScal[iScal] + Frho * scalR[iScal] for iScal in range(nScal)]

	sMax = ez.max(ez.abs(sL), ez.abs(sR))

	Frho     = Frho * area
	Frhou    = Frhou * area
	FrhoE    = FrhoE * area
	FrhoScal = [FrhoScal[iScal] * area for iScal in range(nScal)]
