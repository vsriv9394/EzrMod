#include "backend.h"
#ifdef DEBUG
#include <time.h>
#include <stdio.h>
#endif

int forwProp(int size, int *op1, int *op2, double *value, int *oper, int *ifEnd, int *elseEnd)
{
	#ifdef DEBUG
	clock_t start, stop; start = clock();
	#endif

	double x, y, z; int operId; int xId, yId; int end = size;
	
	int i=0;

	while(i<end)
	{
		operId = oper[i];
		
		if(operId>-1)
		{
			xId = op1[i]; yId = op2[i]; x = value[xId]; if(yId>=0) y = value[yId];
			
			if(operId<18)
			{
				switch(operId)
				{
					case NEG:  z = -x;            break;
					case ABS:  z = x>=0 ? x : -x; break;
					case MAX:  z = x>y ? x : y;   break;
					case MIN:  z = x<y ? x : y;   break;
					case ADD:  z = x + y;         break;
					case SUB:  z = x - y;         break;
					case MUL:  z = x * y;         break;
					case DIV:  z = x / y;         break;
					case POW:  z = pow(x,y);      break;
					case EXP:  z = exp(x);        break;
					case LOG:  z = log(x);        break;
					case SQRT: z = sqrt(x);       break;
					case SIN:  z = sin(x);        break;
					case COS:  z = cos(x);        break;
					case TAN:  z = tan(x);        break;
					case SINH: z = sinh(x);       break;
					case COSH: z = cosh(x);       break;
					case TANH: z = tanh(x);       break;
				}
				value[i] = z;
			}
			else
			{
				switch(operId)
				{
					case IFEQ: if(x==y) end = ifEnd[i]; else {end = elseEnd[i]; i=ifEnd[i]-1;} break;
					case IFNE: if(x!=y) end = ifEnd[i]; else {end = elseEnd[i]; i=ifEnd[i]-1;} break;
					case IFLT: if(x<y)  end = ifEnd[i]; else {end = elseEnd[i]; i=ifEnd[i]-1;} break;
					case IFGT: if(x>y)  end = ifEnd[i]; else {end = elseEnd[i]; i=ifEnd[i]-1;} break;
					case IFLE: if(x<=y) end = ifEnd[i]; else {end = elseEnd[i]; i=ifEnd[i]-1;} break;
					case IFGE: if(x>=y) end = ifEnd[i]; else {end = elseEnd[i]; i=ifEnd[i]-1;} break;
				}
			}
		}
		
		i++;
	}

	#ifdef DEBUG
	stop = clock(); printf("Time for forwProp = %.10le\n", ((double)(stop-start))/CLOCKS_PER_SEC);
	#endif

	return end;
}

void backProp(int depVar, int *op1, int *op2, double *value, double *deriv, int *oper)
{
	#ifdef DEBUG
	clock_t start, stop; start = clock();
	#endif

	double x, y, z, dx, dy, dz; int operId; int xId, yId;
	
	for(int i=0; i<depVar; i++) deriv[i] = 0.0; int i=depVar; deriv[i] = 1.0;

	while(i>=0)
	{
		dz = deriv[i];
		if(dz==0.0) { i--; continue; }

		operId = oper[i];
		
		if(operId>-1)
		{
			xId = op1[i];
			yId = op2[i];
			z = value[i];
			x = value[xId];
			if(yId>=0) y = value[yId];
			
			if(operId<18)
			{
				switch(operId)
				{
					case NEG:  dx = -1.0;                                        break;
					case ABS:  dx = (x==z) ? 1.0 : -1.0;                         break;
					case MAX:  if(x==z) {dx=1.0; dy=0.0;} else {dx=0.0; dy=1.0;} break;
					case MIN:  if(x==z) {dx=1.0; dy=0.0;} else {dx=0.0; dy=1.0;} break;
					
					case ADD:  dx = 1.0;   dy =  1.0;            break;
					case SUB:  dx = 1.0;   dy = -1.0;            break;
					case MUL:  dx = y;     dy =  x;              break;
					case DIV:  dx = 1.0/y; dy = -z/y;            break;
					
					case POW:  dx = (x==0.0) ? 0.0 : y*z/x; dy = z*log(fabs(x)); break;
					
					case EXP:  dx =  z;       break;
					case LOG:  dx =  1.0/x;   break;
					case SQRT: dx =  0.5/z;   break;
					case SIN:  dx =  cos(x);  break;
					case COS:  dx = -sin(x);  break;
					case TAN:  dx =  1.0-z*z; break;
					case SINH: dx =  cosh(x); break;
					case COSH: dx =  sinh(x); break;
					case TANH: dx =  1.0-z*z; break;
				}
				
				deriv[xId] += dz * dx;
				if(yId>=0) deriv[yId] += dz * dy;
			}
		}
		
		i--;
	}

	#ifdef DEBUG
	stop = clock(); printf("Time for backProp = %.10le\n", ((double)(stop-start))/CLOCKS_PER_SEC);
	#endif
}
