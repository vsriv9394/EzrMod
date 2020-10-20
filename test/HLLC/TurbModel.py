nScal = 1

PrTurb = 0.90

def calcTKE(scal):

	return 0.0

def calcMuTurb(rho, mu, scal, gradVel):

	chi = rho * scal[0] / mu
	fv1 = chi**3 / (chi**3 + 357.911)
	return rho * scal[0] * fv1

def calcDiffTurb(rho, mu, scal, gradVel):

	return [(mu + calcMuTurb(rho, mu, scal, gradVel)) * 1.5]
